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
# MODULE stats.py

# SYNOPSIS
# Provides functions calculating statistics.

import datetime
import trainer
import tree
import os

STAT_NEW = 0
STAT_FIRST_STEP = 1
STAT_SECOND_STEP = 2
STAT_REVIEW = 3
STAT_INACTIVE = 4
STAT_DUE = 5
STAT_REACHABLE = 6
STAT_TOTAL = 7

STAT_WAITING = 0
STAT_LEARNED = 1
STAT_SIZE = 2

# training_stats()
# Should be called on the root node of a PGN.
# Produces a tuple consiting of seven integers:
# The number of positions with status NEW, FIRST_STEP, SECOND_STEP,
# REVIEW, INACTIVE; the number of positions due for recall; the
# number of positions reachable.
def training_stats(node) :
    stats = [0,0,0,0,0,0,0]
    if (tree.is_solution(node)) :
        status = node.training.status
        due_date = node.training.due
        if (status == tree.Status.NEW) :
            stats[STAT_NEW] += 1
        elif (status == tree.Status.FIRST_STEP) :
            stats[STAT_FIRST_STEP] += 1            
        elif (status == tree.Status.SECOND_STEP) :
            stats[STAT_SECOND_STEP] += 1            
        elif (status == tree.Status.REVIEW) :
            stats[STAT_REVIEW] += 1            
        elif (status == tree.Status.INACTIVE) :
            stats[STAT_INACTIVE] += 1            
        if (status == tree.Status.REVIEW and
            due_date <= datetime.date.today()) :
            stats[STAT_DUE] += 1
        stats[STAT_REACHABLE] += 1

    # recursive part
    if (not node.is_end()) :
        if (tree.is_solution(node.variations[0])) :
            # search only the main variation
            child_stats = training_stats(node.variations[0])
            for index in range(len(stats)) :
                stats[index] += child_stats[index]
        else :
            # search all variations
            for child in node.variations :
                child_stats = training_stats(child)
                for index in range(len(stats)) :
                    stats[index] += child_stats[index]
    return stats

# total_training_positions()
# Should be called on the root node of a PGN.
def total_training_positions(node) :
    if (tree.is_solution(node)) :
        count = 1
    else :
        count = 0
    if (not node.is_end()):
        for child in node.variations :
            count += total_training_positions(child)                 
    return count

# item_stats()
# Compact statistics.
# Returns a triple of statistics for the given item: the number
# of positions waiting; of positions learned; and positions in total.
def item_stats(filepath) :
    root = tree.load(filepath)
    stats = training_stats(root)
    waiting = stats[STAT_NEW] + stats[STAT_FIRST_STEP]
    waiting += stats[STAT_SECOND_STEP] + stats[STAT_DUE]
    learned = stats[STAT_REVIEW]
    size = stats[STAT_REACHABLE]
    return [waiting, learned, size]

# item_stats_full()
# Full set of statistics.
# Returns the training_stats() list with the total number of
# positions appended.
def item_stats_full(filepath) :
    root = tree.load(filepath)    
    return training_stats(root) + [total_training_positions(root)]

# category_stats()
# Returns compact statistics for the given category.
def category_stats(dirpath) :
    stats = [0,0,0]
    items = os.listdir(dirpath)
    for item in items :
        temp_stats = item_stats(dirpath + '/' + item)
        stats = list(sum(stat) for stat in zip(stats, temp_stats))
    return stats

# category_stats()
# Returns compact statistics for the given collection.
def collection_stats(dirpath) :
    stats = [0,0,0]
    categories = os.listdir(dirpath)
    for category in categories :
        temp_stats = category_stats(dirpath + '/' + category)
        stats = list(sum(stat) for stat in zip(stats, temp_stats))
    return stats
