"""
Copyright Joshua Blinkhorn 2021

This file is part of Chessic.

Chessic is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Chessic is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Chessic.  If not, see <https://www.gnu.org/licenses/>.
"""

# Chessic v1.0
# MODULE tree.py

# SYNOPSIS
# Provides the definition and interface for Chessic training trees.

# A training tree is a python chess game (i.e. a tree of nodes),
# with training data appended to particular nodes - those identified
# as `solutions' to `problems'.
# Every tree has a `colour' - the training player plays the pieces
# of that colour.
# A problem is a position (i.e. node) in which the training player
# does not have the move; a solution is a position whose parent
# is a problem.
# The root node, by definition, is never a solution, but it may
# be a problem.

# Trees are saved and loaded using pickle. An implementation
# based on a custom filetype is envisaged for future releases.

import pickle
import datetime
import chess
import enum
import copy

# Enumeration for training statuses.
# Every solution in a tree has one of the following statuses.
class Status(enum.Enum) :
    NEW = 1
    FIRST_STEP = 2
    SECOND_STEP = 3
    REVIEW = 4
    INACTIVE = 5

# Training data appended to a solution.
class TrainingData :
    def __init__(self) :
        today = datetime.date.today()        
        self.status = Status.INACTIVE
        self.due = today
        self.previous_due = today

# Meta data appended to the root node of a tree.        
# new_limit specifies the maximum number of learning actions
# for the tree, per day. The number remaining for the date of
# last access is recorded by new_remaining.
# Note that currently the new_limit is fixed; should it be
# user-defined and modifiable, new_remaining should be calculated
# by counting the number of learning actions (not the number
# remaining, which depends on the limit).
class MetaData:
    def __init__(self, colour) :
        today = datetime.date.today()        
        self.colour = colour
        self.latest_access = today
        self.new_limit = 10
        self.new_remaining = self.new_limit
        self.new_marked = 0

# is_root()
# Returns true if the given node is the root of the tree, false
# otherwise.
def is_root(node) :
    return node.parent == None

# is_raw_solution()
# Returns true if the given node is a solution, false otherwise.
# `Raw' refers to the fact that this function can be called
# if the TrainingData has not been appended; if the TrainingData
# has been appended, use is_solution(), which is much quicker.
def is_raw_solution(node) :
    return (not is_root(node)) and (not is_raw_problem(node))

# is_raw_problem()
# Returns true if the given node is a problem, false otherwise.
def is_raw_problem(node) :
    node_turn = copy.copy(node).board().turn
    colour = node.game().meta.colour
    return node_turn == colour

# is_solution()
# Returns true if the given node is a solution, false otherwise.
# Performs much faster than is_raw_solution()
def is_solution(node) :
    return node.training != None

# save()
# Saves a tree.
def save(filepath, root) :
    with open(filepath, "wb") as file :
        pickle.dump(root,file)

# load()
# Loads a tree, returning its root node.
# Upon loading, statuses are metadata are updated if the tree
# was not accessed today already.
def load(filepath) :
    with open(filepath, "rb") as file :
        root = pickle.load(file)
    if (root.meta.latest_access < datetime.date.today()) :
        update_meta(root)
        update_statuses(root)
        save(filepath, root)
    return root

# create()
# Creates a new tree.
# Colour is the tree colour; the root node takes the initial
# position specified by board.
def create(filepath, board, colour) :
    root = chess.pgn.Game()
    root.setup(board)
    root.meta = MetaData(colour)
    root.training = None
    save(filepath, root)

# update_statuses()
# Updates the statuses of all solutions in the tree.
# Any incomplete learning is ignored, and the first n INACTIVE nodes
# are marked new, where n is the number of learning actions remaining
# today. The maximum number of learning actions is set by
# MetaData.new_limit, and the number remaining by
# MetaData.new_remaining
def update_statuses(root) :
    erase_incomplete_learning(root)
    reset_new_marked(root)        
    seek_new(root)

# add_child()
# Adds a new node to the tree.
def add_child(node, move) :
    child = node.add_variation(move)
    if (is_raw_solution(child)) :
        child.training = TrainingData()
    else :
        child.training = None

# reset_new_marked()
# Sets Meta.new_marked to zero.
# The value new_marked is only used by the function seek_new().
def reset_new_marked(root) :
    root.meta.new_marked = 0

# update_meta()
# Updates the meta data under the impression that this is the first
# access of the tree today -- i.e. this function is only called
# when that is the case.
def update_meta(root) :
    root.meta.latest_access = datetime.date.today()
    root.meta.new_remaining = root.meta.new_limit

# erase_incomplete_learning()
# Sets all `learning' statuses (i.e. NEW, FIRST_STEP and SECOND_STEP)
# to INACTIVE.
def erase_incomplete_learning(node) :
    if (is_solution(node) and node.training.status != Status.REVIEW):
        node.training.status = Status.INACTIVE
    if (not node.is_end()) :
        if (is_solution(node.variations[0])) :
            erase_incomplete_learning(node.variations[0])
        else :
            for child in node.variations :
                erase_incomplete_learning(child)                

# seek_new()
# As long as there are learning actions remaining for today,
# finds inactive nodes and sets their status as NEW.
# Assumes that there is no incomplete learning.
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
        if (is_solution(node.variations[0])) :
            seek_new(node.variations[0])
        else :
            for child in node.variations :
                seek_new(child)                
