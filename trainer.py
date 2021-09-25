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

class Result(enum.Enum) :
    EASY = 1
    OKAY = 2
    HARD = 3
    PAUSE = 4

def train(filepath):
    root = tree.load(filepath)
    colour = root.meta.colour
    queue = generate_queue(root)
    play_queue(queue, root, filepath)

def play_queue(queue, root, filepath) :
    while(len(queue) != 0) :
        node = queue.pop(0)
        result = play_node(node, filepath)
        if (result == Result.PAUSE) :
            break
        handle_result(result, node, queue)
        tree.save(filepath, root)                        

def play_node(node, filepath) :
    problem = copy.copy(node.parent)
    solution = copy.copy(node)
    if (pose_problem(filepath, problem) == Result.PAUSE) :
        return Result.PAUSE
    return show_solution(solution)

def pose_problem(filepath, problem) :
    result = False
    while (result == False) :
        problem_title(filepath)
        problem_info(problem)
        print_board(problem.board(), problem.game().meta.colour)
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

def problem_info(problem) :
    string = status_string(problem)
    string += remaining_string(problem.game())
    string += "\n\n\n"
    print(string)

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

def remaining_string(root) :
    info = stats.training_stats(root)        
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
        return Result.PAUSE
    elif (command == "") :
        return True
    else :
        return False

def show_solution(solution) :
    result = False
    while(result == False) :
        print_board(solution.board(), solution.game().meta.colour)
        solution_options(solution)
        result = solution_prompt(solution)
    return result
    
def solution_options(solution) :
    status = solution.training.status
    if (status == tree.Status.NEW) :
        print("\n\n\n<enter> continue\n")
    else :
        print("\n'e'      easy")
        print("<enter>  okay")
        print("'h'      hard\n")

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

def generate_queue(node) :
    queue = []    
    if (tree.is_solution(node)) :
        handle_solution(node, queue)
    if (not node.is_end()) :
        if (tree.is_solution(node.variations[0])) :
            child = node.variations[0]
            queue += generate_queue(child)
        else :
            for child in node.variations :
                queue += generate_queue(child)
    return queue

def handle_solution(node, queue) :
    status = node.training.status
    due_date = node.training.due
    today = datetime.date.today()
    if (status == tree.Status.NEW or
        status == tree.Status.FIRST_STEP or
        status == tree.Status.SECOND_STEP or
        (status == tree.Status.REVIEW and due_date <= today)) :
        queue.append(node)

def handle_result(result, node, queue) :
    status = node.training.status    
    root = node.game()
    if (status == tree.Status.NEW) :
        requeue(node, queue, tree.Status.FIRST_STEP)
                    
    elif (status == tree.Status.FIRST_STEP) :
        if (result == Result.EASY) :
            schedule(node, result)
            root.meta.new_remaining -= 1
        elif (result == Result.OKAY) :
            requeue(node, queue, tree.Status.SECOND_STEP)
        elif (result == Result.HARD) :
            requeue(node, queue, tree.Status.FIRST_STEP)            

    elif (status == tree.Status.SECOND_STEP) :
        if (result == Result.EASY) :
            schedule(node, result)            
            root.meta.new_remaining -= 1
        elif (result == Result.OKAY) :
            schedule(node, result)
            root.meta.new_remaining -= 1
        elif (result == Result.HARD) :
            requeue(node, queue, tree.Status.FIRST_STEP)
            
    elif (status == tree.Status.REVIEW) :
        if (result == Result.EASY) :
            schedule(node, result)            
        elif (result == Result.OKAY) :
            schedule(node, result)
        elif (result == HARD) :
            requeue(node, queue, tree.Status.FIRST_STEP)

def schedule(node, result) :
    today = datetime.date.today()
    if (node.training.status == tree.Status.FIRST_STEP or
        node.training.status == tree.Status.SECOND_STEP) :
        node.training.due = first_due_date(node, result, today)
    else :
        node.training.due = new_due_date(node, result, today)
    node.training.previous_due = today
    node.training.status = tree.Status.REVIEW

def first_due_date(node, result, today) :
    if (result != Result.EASY) :
        wait = 1
    else :
        wait = 3
    return today + datetime.timedelta(days = wait)

def new_due_date(node, result, today) :
    if (result != Result.EASY) :
        multiplier = 2
    else :
        multiplier = 4
    gap = (node.training.due - node.training.previous_due).days
    min_recall_wait = 365
    wait = min(min_recall_wait,
               int(gap * (multiplier + random.random())))
    return today + datetime.timedelta(days = wait)    
    
def requeue(node, queue, new_status) :
    node.training.status = new_status
    low_limit = min(1, len(queue))
    high_limit = min(4, len(queue))
    queue.insert(random_offset(low_limit, high_limit), node)

def random_offset(lower_bound, upper_bound) :
    interval_width = upper_bound - lower_bound + 1
    offset = int(interval_width * random.random())
    return lower_bound + offset
