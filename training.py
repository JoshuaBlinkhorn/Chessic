# MODULE training.py
# this file is part of Opening Trainer by Joshua Blinkhorn

# SYNOPSIS

import datetime
import chess
import random
from graphics import print_board, clear
from items import save_item, load_item, NEW, FIRST_STEP, SECOND_STEP, REVIEW, INACTIVE

NEW = 0
FIRST_STEP = 1
SECOND_STEP = 2
REVIEW = 3
INACTIVE = 4

# new first second review inactive due reachable total

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

def play_card(card,repertoire) :
    root = card[0]
    node = card[1]
    status = node.training.status
    player = repertoire.meta.player

    # front of card
    front = root.variations[0]
    if (status == 0) :
        print("\nNEW : this is a position you haven't seen before\n")
    if (status == 1 or status == 2) :
        print("\nLEARNING : this is a position you're currently learning\n")
    if (status == 3) :
        print("\nRECALL : this is a position you've learned, due for recall\n")

    print_board(front.board(),player)
    if (status == 0) :
        print("\nGuess the move..")
    else :
        print("\nRecall the move..")
    print(".. then hit [enter] or 'c' to close")
    uci = input("\n:")
    if (uci == "c") :
        return "CLOSE"

    # back of card
    back = front.variations[0]
    clear()    
    print("Solution:")
    print_board(back.board(),player)

    if (status == 0) :
        print("\nHit [enter] to continue.")
        input("\n\n:")
    if (status != 0) :
        print("\n'h' hard    [enter] ok    'e' easy\n")
        uci = input("\n:")
   
    while (True) :
        if (uci == "e") :
            return "EASY"
        if (uci == "h") :
            return "HARD"
        if (uci == "") :
            return "OK"
        if (uci == "c") :
            return "CLOSE"
        uci = input(":")
        
        
def handle_card_result(result,card,queue,repertoire) :
    root = card[0]
    node = card[1]
    status = node.training.status
    
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    
    if (status == NEW) :
        print("Here")
        node.training.status = FIRST_STEP
        increase = int(round(3 * random.random()))
        offset = min(1 + increase,len(queue))
        queue.insert(offset,card)
                    
    elif (status == FIRST_STEP) :
        if (result == "EASY") :
            node.training.status = REVIEW
            node.training.last_date = today
            node.training.due_date = tomorrow
            repertoire.meta.learning_data[1] += 1
        elif (result == "OK") :
            node.training.status = SECOND_STEP
            increase = int(round(3 * random.random()))
            offset = min(6 + increase,len(queue))
            queue.insert(offset,card)
        elif (result == "HARD") :
            node.training.status = FIRST_STEP            
            increase = int(round(3 * random.random()))
            offset = min(1 + increase,len(queue))
            queue.insert(offset,card)

    elif (status == SECOND_STEP) :
        if (result == "EASY") :
            node.training.status = REVIEW
            node.training.last_date = today
            node.training.due_date = today + datetime.timedelta(days=3)
            repertoire.meta.learning_data[1] += 1
        elif (result == "OK") :
            node.training.status = REVIEW
            node.training.last_date = today
            node.training.due_date = tomorrow
            repertoire.meta.learning_data[1] += 1
        elif (result == "HARD") :
            node.training.status = FIRST_STEP            
            increase = int(round(3 * random.random()))
            offset = min(1 + increase,len(queue))
            queue.insert(offset,card)
            
    elif (status == REVIEW) :
        previous_gap = (node.training.due_date - node.training.last_date).days

        if (result == "HARD") :
            node.training.status = FIRST_STEP
            offset = min(2,len(queue))
            queue.insert(offset,card)
            repertoire.meta.learning_data[1] -= 1

        else :
            if (result == "EASY") :
                multiplier = 3 + random.random()
            else :
                multiplier = 2 + random.random()
            new_gap = int(round(previous_gap * multiplier))
            node.training.status = REVIEW
            node.training.last_date = today
            node.training.due_date = today + datetime.timedelta(days=new_gap)

def generate_training_queue(node,board) :
    # the board must be returned as it was given
    queue = []    
    
    if (node.training) :
        status = node.training.status
        due_date = node.training.due_date
        today = datetime.date.today()
        if (status == 0 or status == 1 or status == 2 or (status == 3 and due_date <= today)) :
                # add a card to the queue
            solution = board.pop()
            problem = board.pop()
            game = chess.pgn.Game()
            game.setup(board)
            new_node = game.add_variation(problem)
            new_node = new_node.add_variation(solution)
            board.push(problem)
            board.push(solution)
            queue.append([game,node])

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


