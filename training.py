# MODULE trainer.py
# this file is part of Opening Trainer by Joshua Blinkhorn

# SYNOPSIS

import datetime
import chess
import random

import access
import stats
import paths
from graphics import print_board, clear


NEW = 0
FIRST_STEP = 1
SECOND_STEP = 2
REVIEW = 3
INACTIVE = 4

EASY = 'E'
OKAY = 'O'
HARD = 'H'
PAUSE = 'P'

PROBLEM = 0
NODE = 1

class TrainingData :
    def __init__(self) :
        self.status = INACTIVE
        self.last_date = datetime.date.today()
        self.due_date = datetime.date.today()
        
class  MetaData:
    def __init__(self, name, player) :
        self.name = name
        self.player = player
        self.learning_data = [datetime.date.today(),0]
        self.learn_max = 10

def train(filepath):
    root = access.load_item(filepath)
    player = root.meta.player
    board = root.board()
    node = root        
    queue = generate_training_queue(root, board)
    play_queue(queue, root, filepath)

def play_queue(queue, root, filepath) :
    while(len(queue) != 0) :
        card = queue.pop(0)
        result = play_card(card, root, filepath)
        if (result == PAUSE) :
            return 
        handle_card_result(result,card,queue,root)
        access.save_item(filepath, root)
    
        
def play_card(card, root, filepath) :
    front = card[PROBLEM].variations[0]
    back = front.variations[0]
    node = card[NODE]
    status = node.training.status
    player = root.meta.player
    if (card_front(filepath,node,front.board(),player) == PAUSE) :
        return PAUSE
    return card_back(node, back.board(), player)

def card_front(filepath, node, board, player) :
    result = False
    while (result == False) :
        card_title(filepath)
        card_info(filepath, node)
        print_board(board,player)
        front_options()
        result = front_prompt()
    return result

def card_back(node, board, player) :
    result = False
    while(result == False) :
        print_board(board,player)
        back_options(node)
        result = back_prompt(node)
    return result

def card_title(filepath) :
    clear()
    width = 18
    name = paths.item_name(filepath)
    print("TRAINING ITEM ->".ljust(width) + name)
    print("CATEGORY".ljust(width) + paths.category_name(filepath))
    print("COLLECTION".ljust(width)+paths.collection_name(filepath))
    print("")

def card_info(filepath, node) :
    string = status_string(node)
    string += remaining_string(filepath)
    string += "\n\n\n"
    print(string)

def status_string(node) :
    width = 18
    status = node.training.status    
    if (status == NEW) :
        string = "NEW".ljust(width)
    elif (status == FIRST_STEP or status == SECOND_STEP) :
        string = "LEARNING".ljust(width)
    elif (status == REVIEW) :
        string = "REVIEW".ljust(width)
    return string

def remaining_string(filepath) :
    info = stats.item_stats_full(filepath)        
    new = str(info[stats.STAT_NEW])
    learn = info[stats.STAT_FIRST_STEP]
    learn = str(learn + info[stats.STAT_SECOND_STEP])
    due = str(info[stats.STAT_DUE]) 
    return new + " | " + learn + " | " + due
    
def front_options() :
    print("\n\n<Enter> show solution")
    print("'p' pause session")

def front_prompt() :
    command = input("\n:")
    clear()
    if (command == "p") :
        return PAUSE
    elif (command == "") :
        return True
    else :
        return False

def back_options(node) :
    status = node.training.status
    if (status == NEW) :
        print("\n\n\n<enter> continue\n")
    else :
        print("\n'e'      easy")
        print("<enter>  okay")
        print("'h'      hard\n")

def back_prompt(node) :
    status = node.training.status
    command = input(":")
    clear()
    if (status == NEW) :
        if (command == "") :
            return OKAY
        else :
            return False
    else :
        if (command == "e") :
            return EASY
        elif (command == "") :
            return OKAY
        elif (command == "h") :
            return HARD
        else :
            return False

def generate_training_queue(node,board) :
    # the board must be returned as it was given
    queue = []    
    if (node.training) :
        handle_training_node(node, board, queue)
    # recursive part
    if (not node.is_end()) :
        if (node.player_to_move) :
            # search only the main variation
            child = node.variations[0]
            board.push(child.move)
            queue += generate_training_queue(child,board)
            board.pop()
        else :
            # search all variations
            for child in node.variations :
                board.push(child.move)
                queue += generate_training_queue(child,board)
                board.pop()
    return queue

def handle_training_node(node, board, queue) :
    status = node.training.status
    due_date = node.training.due_date
    today = datetime.date.today()
    if (status == NEW or
        status == FIRST_STEP or
        status == SECOND_STEP or
        (status == REVIEW and due_date <= today)) :
        # add a card to the queue
        add_card(node, board, queue)

def add_card(node, board, queue) :
    solution = board.pop()
    problem = board.pop()
    game = chess.pgn.Game()
    game.setup(board)
    new_node = game.add_variation(problem)
    new_node = new_node.add_variation(solution)
    board.push(problem)
    board.push(solution)
    queue.append([game,node])
        
def handle_card_result(result, card, queue, root) :
    problem = card[PROBLEM]
    node = card[NODE]
    status = node.training.status
    
    if (status == NEW) :
        reinsert_card(FIRST_STEP, card, queue)
                    
    elif (status == FIRST_STEP) :
        if (result == EASY) :
            schedule(node, result)
            root.meta.learning_data[1] += 1
        elif (result == OKAY) :
            reinsert_card(SECOND_STEP, card, queue)
        elif (result == HARD) :
            reinsert_card(FIRST_STEP, card, queue)            

    elif (status == SECOND_STEP) :
        if (result == EASY) :
            schedule(node, result)            
            root.meta.learning_data[1] += 1
        elif (result == OKAY) :
            schedule(node, result)
            root.meta.learning_data[1] += 1
        elif (result == HARD) :
            reinsert_card(FIRST_STEP, card, queue)
            
    elif (status == REVIEW) :
        if (result == EASY) :
            schedule(node, result)            
        elif (result == OKAY) :
            schedule(node, result)
        elif (result == HARD) :
            reinsert_card(FIRST_STEP, card, queue)
            root.meta.learning_data[1] -= 1

def schedule(node, result) :
    today = datetime.date.today()
    if (node.training.status == FIRST_STEP or
        node.training.status == SECOND_STEP) :
        node.training.due_date = first_due_date(node, result, today)
    else :
        node.training.due_date = new_due_date(node, result, today)
    node.training.last_date = today
    node.training.status = REVIEW

def first_due_date(node, result, today) :
    if (result != EASY) :
        wait = 1
    else :
        wait = 3
    return today + datetime.timedelta(days = wait)

def new_due_date(node, result, today) :
    if (result != EASY) :
        multiplier = 2
    else :
        multiplier = 4
    gap = (node.training.due_date - node.training.last_date).days
    wait = int(gap * (multiplier + random.random()))
    return today + datetime.timedelta(days = wait)    
    
def reinsert_card(new_status, card, queue) :
    node = card[NODE]
    node.training.status = new_status
    offset_low = 1
    offset_high = 4
    random_offset = get_offset(offset_low, offset_high)
    offset = min(random_offset,len(queue))
    queue.insert(offset,card)

def get_offset(lower_bound, upper_bound) :
    interval_width = upper_bound - lower_bound + 1
    offset = int(interval_width * random.random())
    return lower_bound + offset
