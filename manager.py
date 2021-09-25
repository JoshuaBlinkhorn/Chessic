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
# MODULE manager.py

# SYNOPSIS
# Provides the functionality for managing a tree.
# Typically only the functions manage() and new_tree() will
# need to be imported.

import datetime
import chess
import os

import tree
import paths
from graphics import print_board, clear

# represents_int()
# Determines whether a string represents an integer.
def represents_int(string):
    try: 
        int(string)
        return True
    except ValueError:
        return False

# manage()
# Launches the dialogue for tree management.
def manage(filepath):
    root = tree.load(filepath)
    colour = root.meta.colour
    board = root.board()
    node = root       

    command = ""
    while(command != "c") :
        clear()
        print_turn(board)
        print_board(board,colour)
        print_moves(node, board)
        print_options(node)
        node, command = prompt(node, board, filepath)

# print_turn()
# Prints the player to move in the board position.
def print_turn(board) :
    print("")
    if (board.turn) :
        print("WHITE to play.\n")
    else :
        print("BLACK to play.\n")

# print_moves()        
# Prints moves of the variations of the given node.
def print_moves(node, board) :
    if (tree.is_raw_problem(node)) :
        if (node.is_end()) :
            print("No solutions.")
        else :
            print("Solutions:")
            for index, solution in enumerate(node.variations) :
                san = board.san(solution.move)
                print(str(index + 1).ljust(3) + san)
    else :
        if (node.is_end()) :
            print("No problems.")
        else :
            print("Problems:")
            for index, problem in enumerate(node.variations) :
                san = board.san(problem.move)                
                print(str(index + 1).ljust(3) + san)
    print("")

# print_options()
# Prints the user options for the given node.
def print_options(node) :
    print ("<move> add move")
    if (not node.is_end()) :
        print ("<ID> play move")            
        print("'d' delete")
    if (len(node.variations) > 1) :
        print("'p' promote")
    if (node.parent != None) :
        print("'b' back")
    print ("'c' close")

# prompt()
# Handles the user prompt at the bottom of the management dialogue.
def prompt(node, board, filepath) :
    command = input("\n:")
    if (command == "b" and not tree.is_root(node)) :
        node = pop_move(node, board)
    elif (command == "d" and len(node.variations) != 0) :
        delete_move(node, board, filepath)            
    elif (command == "p" and len(node.variations) > 1) :
        promote_move(node,board)
    elif (represents_int(command) and
          1 <= int(command) <= len(node.variations)) :
        node = play_move(node, board, int(command) - 1)
    elif (is_valid_uci(command, board) or
          is_valid_san(command, board)) :
        node = add_move(node, board, command, filepath)
    return node, command

# pop_move()
# Removes the current move from the stack.
def pop_move(node, board) :
    board.pop()
    return node.parent

# delete_move()
# Deletes a move from the tree.
# Statuses are updated and the tree is saved. This is best done
# here, not at the end of manage(), because updating statuses
# should be avoided when the tree is not modified.
def delete_move(node, board, filepath) :
    command = input("ID to delete: ")
    if (represents_int(command) and
        1 <= int(command) <= len(node.variations)) :
        index = int(command) - 1
        variation = node.variations[index]
        san = board.san(variation.move)        
        print(f"You are about to permanently delete '{san}'.")
        command = input("Are you sure? (y/n): ")
        if (command == "y") :
            node.remove_variation(variation)
            tree.update_statuses(node.game())
            tree.save(filepath, node.game())            

# promote_move()
# Promotes a move to the main variation. 
def promote_move(node,board) :
    command = input("ID to promote: ")
    if (represents_int(command) and
        1 <= int(command) <= len(node.variations)) :
        index = int(command) - 1
        node.promote_to_main(node.variations[index])

# play_move()
# Moves to the node reached by the given move.
def play_move(node, board, variation_index) :
    node = node.variations[variation_index]
    board.push(node.move)
    return node    

# add_move()
# Adds a move to the tree.
# Statuses are updated and the tree is saved. This is best done
# here, not at the end of manage(), because updating statuses
# should be avoided when the tree is not modified.
def add_move(node, board, command, filepath) :
    if (is_valid_uci(command, board)) :
        move = chess.Move.from_uci(command)
    else :
        move = board.parse_san(command)
    if (node.has_variation(move)) :
        print("\nMove already exists.")
        input("Hit [Enter] to continue :")
    else :
        tree.add_child(node, move)
        tree.update_statuses(node.game())
        tree.save(filepath, node.game())            
        board.push(move)        
        node = node.variation(move)
    return node

# is_valid_uci()
# Determines whether a string represents a move in the context
# of the board, specified in UCI notation.
def is_valid_uci(string, board) :
    for move in board.legal_moves :
        if (string == move.uci()) :
            return True
    return False

# is_valid_uci()
# Determines whether a string represents a move in the context
# of the board, specified in standard algebraic notation.
def is_valid_san(string,board) :
    for move in board.legal_moves :
        if (string == board.san(move)) :
            return True
    return False

# new_tree()
# Launches the dialogue to create a new tree.
def new_tree(filepath) :    
    colour = select_colour(filepath)
    board = select_position(filepath, colour)
    tree.create(filepath, board, colour)

# new_tree_title
# Prints details for the new tree dialogue.
def new_tree_title(filepath) :
    clear()
    width = 22
    name = paths.item_name(filepath)
    print("CREATING NEW ITEM ->".ljust(width) + name)
    print("")
    print("CATEGORY".ljust(width) + paths.category_name(filepath))
    print("COLLECTION".ljust(width) +paths.collection_name(filepath))
    print("")

# select_colour()
# Returns the `tree colour' (i.e. the colour of the player who
# trains with the tree) selected by the user.
def select_colour(filepath) :
    command = ""
    while (command != "w" and command != "b") :
        new_tree_title(filepath)
        command = input("Select playing colour (w/b): ")
    if (command == "w") :
        return True
    else :
        return False

# select_position()    
# Prompts user to select the initial position of the tree.
def select_position(filepath, colour) :
    board = chess.Board()
    command = "."
    while(command != "") :
        new_tree_title(filepath)
        print("Choose starting position.\n")
        print_board(board, colour)
        position_options(board)
        command = position_prompt(board)
    return board

# position_options()
# Prints options for the select_position() dialogue.
def position_options(board) :
    print("<move> play move")
    print("<Enter> select position")
    if (len(board.move_stack) != 0) :
        print("'b' backup")
    else :
        print("")

# position_prompt()
# Handles the prompt for the select_position() dialogue.
def position_prompt(board) :
    command = input("\n:")
    clear()
    if (command == "b" and len(board.move_stack) != 0) :
        board.pop()
    elif (is_valid_uci(command,board)) :
        board.push(chess.Move.from_uci(command))
    elif (is_valid_san(command,board)) :
        board.push(board.parse_san(command))
    return command

