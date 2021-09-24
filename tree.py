# MODULE tree.py
# this file is part of Opening Trainer by Joshua Blinkhorn

# SYNOPSIS
# Provides the definition and interface for training trees.

import pickle
import datetime
import chess
import enum
import copy

class Status(enum.Enum) :
    NEW = 1
    FIRST_STEP = 2
    SECOND_STEP = 3
    REVIEW = 4
    INACTIVE = 5

class TrainingData :
    def __init__(self) :
        today = datetime.date.today()        
        self.status = Status.INACTIVE
        self.due = today
        self.previous_due = today
        
class MetaData:
    def __init__(self, colour) :
        today = datetime.date.today()        
        self.colour = colour
        self.latest_access = today
        self.new_limit = 10
        self.new_remaining = self.new_limit
        self.new_marked = 0

def is_root(node) :
    return node.parent == None

def is_problem(node) :
    node_turn = copy.copy(node).board().turn
    colour = node.game().meta.colour
    return node_turn == colour

def is_solution(node) :
    return not is_root(node) and not is_problem(node)

def save(filepath, root) :
    with open(filepath, "wb") as file :
        pickle.dump(root,file)

def load(filepath) :
    with open(filepath, "rb") as file :
        root = pickle.load(file)
    if (root.meta.latest_access < datetime.date.today()) :
        update_meta(root)
        update_statuses(root)
        save(filepath, root)
    return root

def create(filepath, board, colour) :
    root = chess.pgn.Game()
    root.setup(board)
    root.meta = MetaData(colour)
    root.training = False
    save(filepath, root)

def update_statuses(root) :
    erase_incomplete_learning(root)
    reset_new_marked(root)        
    seek_new(root)
    
def add_child(node, move) :
    child = node.add_variation(move)
    if (is_solution(child)) :
        child.training = TrainingData()
    else :
        child.training = False

def reset_new_marked(root) :
    root.meta.new_marked = 0

def update_meta(root) :
    root.meta.latest_access = datetime.date.today()
    root.meta.new_remaining = root.meta.new_limit

def erase_incomplete_learning(node) :
    if (is_solution(node) and node.training.status != Status.REVIEW):
        node.training.status = Status.INACTIVE
    if (not node.is_end()) :
        if (is_problem(node)) :
            erase_incomplete_learning(node.variations[0])
        else :
            for child in node.variations :
                erase_incomplete_learning(child)                

def seek_new(node) :
    remaining = node.game().meta.new_remaining
    marked = node.game().meta.new_marked
    if (remaining <= marked) :
        return
    if (is_solution(node) and
        node.training.status == Status.INACTIVE) :
        node.training.status = Status.NEW
        node.game().meta.new_marked += 1
    if (not node.is_end()) :
        if (is_problem(node)) :
            seek_new(node.variations[0])
        else :
            for child in node.variations :
                seek_new(child)                

"""
def set_statuses(node, num_remaining) :
    if (node.training) :
        num_remaining = configure_training_node(node, num_remaining)
    if (not node.is_end()) :
        if (node.player_to_move) :
            num_remaining = set_statuses(node.next(),
                                         num_remaining)
        else :
            for child in node.variations :
                num_remaining = set_statuses(child,
                                             num_remaining)
    return num_remaining

def configure_training_node(node, num_remaining) :
    if (num_remaining <= 0) :            
        if (node.training.status in [Status.NEW,
                                     Status.FIRST_STEP,
                                     Status.SECOND_STEP]) :
            node.training.status = Status.INACTIVE
    else :
        if (node.training.status == Status.INACTIVE) :
            node.training.status = Status.NEW
        if (node.training.status in [Status.NEW,
                                     Status.FIRST_STEP,
                                     Status.SECOND_STEP]) :
            num_remaining -= 1    
"""
