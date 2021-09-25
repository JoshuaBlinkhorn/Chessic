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
# MODULE trainer.py

# SYNOPSIS
# Provides the interface and implementation of the training module.

import datetime
import chess
import chess.pgn
import random
import copy
import enum

import tree
import stats
import paths
from graphics import print_board, clear

# constants for results of training problems
class Result(enum.Enum) :
    EASY = 1
    OKAY = 2
    HARD = 3
    PAUSE = 4

# train()
# Launches the training dialogue for the given tree.
def train(filepath):
    root = tree.load(filepath)
    colour = root.meta.colour
    queue = generate_queue(root)
    play_queue(queue, root, filepath)

# play_queue()
# Plays through the given a training queue.
# The tree is saved at the close of this function, and never
# before; i.e. functions called by this function should not save
# the tree.
def play_queue(queue, root, filepath) :
    while(len(queue) != 0) :
        node = queue.pop(0)
        result = play_node(node, filepath)
        if (result == Result.PAUSE) :
            break
        handle_result(result, node, queue)
        tree.save(filepath, root)                        

# play_node()
# Challenges the user to solve a problem and returns the result.
def play_node(node, filepath) :
    problem = copy.copy(node.parent)
    solution = copy.copy(node)
    if (pose_problem(filepath, problem) == Result.PAUSE) :
        return Result.PAUSE
    return show_solution(solution)

# pose_problem()
# Shows the user the problem.
def pose_problem(filepath, problem) :
    result = False
    while (result == False) :
        problem_title(filepath)
        info_line(problem)
        print_board(problem.board(), problem.game().meta.colour)
        problem_options()
        result = problem_prompt()
    return result

# problem_title()
# Prints the problem title.
def problem_title(filepath) :
    clear()
    width = 18
    name = paths.item_name(filepath)
    print("TRAINING ITEM ->".ljust(width) + name)
    print("CATEGORY".ljust(width) + paths.category_name(filepath))
    print("COLLECTION".ljust(width)+paths.collection_name(filepath))
    print("")

# info_line()
# Prints user information for the problem and the session.
def info_line(problem) :
    string = status_string(problem)
    string += remaining_string(problem.game())
    string += "\n\n\n"
    print(string)

# status_string()
# Prints the `status' of a problem, for the user's information.
# This status is either NEW, LEARNING or REVIEW.
def status_string(problem) :
    width = 18
    solution = problem.variations[0]
    status = solution.training.status
    if (status == tree.Status.NEW) :
        string = "NEW".ljust(width)
    elif (status == tree.Status.FIRST_STEP or
          status == tree.Status.SECOND_STEP) :
        string = "LEARNING".ljust(width)
    elif (status == tree.Status.REVIEW) :
        string = "REVIEW".ljust(width)
    return string

# remaining_string()
# Prints the number of problems remaining in the session in the
# form <NEW> | <LEARNING> | <REVIEW>.
def remaining_string(root) :
    info = stats.training_stats(root)        
    new = str(info[stats.STAT_NEW])
    learn = info[stats.STAT_FIRST_STEP]
    learn = str(learn + info[stats.STAT_SECOND_STEP])
    due = str(info[stats.STAT_DUE]) 
    return new + " | " + learn + " | " + due

# problem_options()
# Prints the options for the below the problem.
def problem_options() :
    print("\n\n<Enter> show solution")
    print("'p' pause session")

# problem_prompt()
# Handles the prompt for the problem.
def problem_prompt() :
    command = input("\n:")
    clear()
    if (command == "p") :
        return Result.PAUSE
    elif (command == "") :
        return True
    else :
        return False

# show_solution()
# Presents a solution to the user.
def show_solution(solution) :
    result = False
    while(result == False) :
        print_board(solution.board(), solution.game().meta.colour)
        solution_options(solution)
        result = solution_prompt(solution)
    return result

# solution_options()
# Prints user options for supplying the training result.
# If a problem is NEW there are no options; otherwise the
# user chooses between `easy,' `okay' or `hard'.
def solution_options(solution) :
    status = solution.training.status
    if (status == tree.Status.NEW) :
        print("\n\n\n<enter> continue\n")
    else :
        print("\n'e'      easy")
        print("<enter>  okay")
        print("'h'      hard\n")

# solution_prompt()
# Handles the solution prompt and returns the result.
def solution_prompt(solution) :
    status = solution.training.status
    command = input(":")
    clear()
    if (status == tree.Status.NEW) :
        if (command == "") :
            return Result.OKAY
        else :
            return False
    else :
        if (command == "e") :
            return Result.EASY
        elif (command == "") :
            return Result.OKAY
        elif (command == "h") :
            return Result.HARD
        else :
            return False

# generate_queue()
# Produces the training queue for the given tree.
# The queue is a list of `solutions', each of which is a node in the
# tree, whose parent is the corresponding `problem'.
# This is recursive function.
# A queue of at most one solution is produced for each node, and
# added to the queue obtained by the recursive call to children.
# All problems are searched, but only the first solution is
# searched; this is why the main variation in the list of solutions
# is the only solution trained.
def generate_queue(node) :
    queue = []    
    if (tree.is_solution(node) and is_queueable(node)) :
        queue.append(node)
    if (not node.is_end()) :
        if (tree.is_solution(node.variations[0])) :
            child = node.variations[0]
            queue += generate_queue(child)
        else :
            for child in node.variations :
                queue += generate_queue(child)
    return queue

# is_queueable()
# Determines whether a solution should be queued.
# Those marked as NEW, FIRST_STEP or SECOND_STEP are queued, along
# with those marked REVIEW whose due date is on or before today.
def is_queueable(solution) :
    status = solution.training.status
    due_date = solution.training.due
    today = datetime.date.today()
    if (status == tree.Status.NEW or
        status == tree.Status.FIRST_STEP or
        status == tree.Status.SECOND_STEP or
        (status == tree.Status.REVIEW and due_date <= today)) :
        return True
    else :
        return False

# handle_result()
# Given the result of a problem and its previous status, one of
# two things happens after the solution is seen:
# 1) the problem is requeued;
# 2) the problem is scheduled for a later date.
# In both cases the status (almost always) changes.
# This function covers all cases.
# It could be rewritten with switch statements, but it is debatable
# whether this 'pythonic' syntax is any better.
def handle_result(result, solution, queue) :
    status = solution.training.status    
    root = solution.game()
    if (status == tree.Status.NEW) :
        requeue(solution, queue, tree.Status.FIRST_STEP)
                    
    elif (status == tree.Status.FIRST_STEP) :
        if (result == Result.EASY) :
            schedule(solution, result)
            root.meta.new_remaining -= 1
        elif (result == Result.OKAY or result == RESULT.HARD) :
            requeue(solution, queue, tree.Status.SECOND_STEP)
        elif (result == Result.HARD) :
            requeue(solution, queue, tree.Status.FIRST_STEP)            

    elif (status == tree.Status.SECOND_STEP) :
        if (result == Result.EASY) :
            schedule(solution, result)            
            root.meta.new_remaining -= 1
        elif (result == Result.OKAY) :
            schedule(solution, result)
            root.meta.new_remaining -= 1
        elif (result == Result.HARD) :
            requeue(solution, queue, tree.Status.FIRST_STEP)
            
    elif (status == tree.Status.REVIEW) :
        if (result == Result.EASY) :
            schedule(solution, result)            
        elif (result == Result.OKAY) :
            schedule(solution, result)
        elif (result == HARD) :
            requeue(solution, queue, tree.Status.FIRST_STEP)

# schedule()
# Schedules a solution based on the status, result, and previous
# due date.
def schedule(solution, result) :
    today = datetime.date.today()
    if (solution.training.status == tree.Status.FIRST_STEP or
        solution.training.status == tree.Status.SECOND_STEP) :
        solution.training.due = first_due_date(solution,
                                               result,
                                               today)
    else :
        solution.training.due = new_due_date(solution, result, today)
    solution.training.previous_due = today
    solution.training.status = tree.Status.REVIEW

# first_due_date()
# Determines the scheduled date for a solution which has been
# successfully learned. 
def first_due_date(result, today) :
    if (result != Result.EASY) :
        wait = 1
    else :
        wait = 3
    return today + datetime.timedelta(days = wait)

# new_due_date()
# Determines the scheduled date for a solution which has been
# successfully recalled. 
def new_due_date(solution, result, today) :
    if (result != Result.EASY) :
        multiplier = 2
    else :
        multiplier = 4
    gap = (solution.training.due -
           solution.training.previous_due).days
    min_recall_wait = 365
    wait = min(min_recall_wait,
               int(gap * (multiplier + random.random())))
    return today + datetime.timedelta(days = wait)    

# requeue()
# Inserts a solution back into the queue. The position of
# insertion does not depend on the status
def requeue(solution, queue, new_status) :
    solution.training.status = new_status
    low_limit = min(1, len(queue))
    high_limit = min(4, len(queue))
    queue.insert(random_int(low_limit, high_limit), solution)

# random_offset()
# Returns a random integer n uniformly distributed in the range
# lower_bound <= n <= upper_bound
def random_int(lower_bound, upper_bound) :
    interval_width = upper_bound - lower_bound + 1
    offset = int(interval_width * random.random())
    return lower_bound + offset
