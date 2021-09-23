# MODULE trainer.py
# this file is part of Opening Trainer by Joshua Blinkhorn

# SYNOPSIS

import datetime
import chess
import chess.pgn
import random
import copy

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
    queue = generate_training_queue(root)
    play_queue(queue, root, filepath)

def play_queue(queue, root, filepath) :
    while(len(queue) != 0) :
        node = queue.pop(0)
        result = play_position(node, filepath)
        if (result == PAUSE) :
            return 
        handle_result(result, node, queue)
        access.save_item(filepath, root)
            
def play_position(node, filepath) :
    problem = copy.copy(node.parent)
    solution = copy.copy(node)
    status = node.training.status
    player = node.game().meta.player
    if (pose_problem(filepath, problem) == PAUSE) :
        return PAUSE
    return show_solution(solution)

def pose_problem(filepath, problem) :
    result = False
    while (result == False) :
        problem_title(filepath)
        problem_info(filepath, problem)
        print_board(problem.board(), problem.game().meta.player)
        problem_options()
        result = problem_prompt()
    return result

def problem_title(filepath) :
    clear()
    width = 18
    name = paths.item_name(filepath)
    print("TRAINING ITEM ->".ljust(width) + name)
    print("CATEGORY".ljust(width) + paths.category_name(filepath))
    print("COLLECTION".ljust(width)+paths.collection_name(filepath))
    print("")

def problem_info(filepath, problem) :
    string = status_string(problem)
    string += remaining_string(filepath)
    string += "\n\n\n"
    print(string)

def status_string(problem) :
    width = 18
    solution = problem.variations[0]
    status = solution.training.status
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
    
def problem_options() :
    print("\n\n<Enter> show solution")
    print("'p' pause session")

def problem_prompt() :
    command = input("\n:")
    clear()
    if (command == "p") :
        return PAUSE
    elif (command == "") :
        return True
    else :
        return False

def show_solution(solution) :
    result = False
    while(result == False) :
        print_board(solution.board(), solution.game().meta.player)
        solution_options(solution)
        result = solution_prompt(solution)
    return result
    
def solution_options(solution) :
    status = solution.training.status
    if (status == NEW) :
        print("\n\n\n<enter> continue\n")
    else :
        print("\n'e'      easy")
        print("<enter>  okay")
        print("'h'      hard\n")

def solution_prompt(solution) :
    status = solution.training.status
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

def generate_training_queue(node) :
    # the board must be returned as it was given
    queue = []    
    if (node.training) :
        handle_training_node(node, queue)
    # recursive part
    if (not node.is_end()) :
        if (node.player_to_move) :
            # search only the main variation
            child = node.variations[0]
            queue += generate_training_queue(child)
        else :
            # search all variations
            for child in node.variations :
                queue += generate_training_queue(child)
    return queue

def handle_training_node(node, queue) :
    status = node.training.status
    due_date = node.training.due_date
    today = datetime.date.today()
    if (status == NEW or
        status == FIRST_STEP or
        status == SECOND_STEP or
        (status == REVIEW and due_date <= today)) :
        # add a card to the queue
        queue.append(node)
        #add_card(node, board, queue)

def handle_result(result, node, queue) :
    status = node.training.status    
    root = node.game()
    if (status == NEW) :
        requeue(node, queue, FIRST_STEP)
                    
    elif (status == FIRST_STEP) :
        if (result == EASY) :
            schedule(node, result)
            root.meta.learning_data[1] += 1
        elif (result == OKAY) :
            requeue(node, queue, SECOND_STEP)
        elif (result == HARD) :
            requeue(node, queue, FIRST_STEP)            

    elif (status == SECOND_STEP) :
        if (result == EASY) :
            schedule(node, result)            
            root.meta.learning_data[1] += 1
        elif (result == OKAY) :
            schedule(node, result)
            root.meta.learning_data[1] += 1
        elif (result == HARD) :
            requeue(node, queue, FIRST_STEP)
            
    elif (status == REVIEW) :
        if (result == EASY) :
            schedule(node, result)            
        elif (result == OKAY) :
            schedule(node, result)
        elif (result == HARD) :
            requeue(node, queue, FIRST_STEP)
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
    
def requeue(node, queue, new_status) :
    node.training.status = new_status
    low_limit = 1
    high_limit = 4
    rand = random_offset(low_limit, high_limit)
    offset = min(rand, len(queue))
    queue.insert(offset,node)

def random_offset(lower_bound, upper_bound) :
    interval_width = upper_bound - lower_bound + 1
    offset = int(interval_width * random.random())
    return lower_bound + offset
