# MODULE manager.py
# this file is part of Opening Trainer by Joshua Blinkhorn

# SYNOPSIS
# Provides the functionality for managing a PGN item.

import datetime
import chess
import os

import access
import paths
from training import TrainingData, MetaData
from graphics import print_board, clear

def represents_int(string):
    try: 
        int(string)
        return True
    except ValueError:
        return False

def manage(filepath):
    root = access.load_item(filepath)
    player = root.meta.player
    board = root.board()
    node = root        

    command = ""
    while(command != "c") :

        clear()
        print_turn(board)
        print_board(board,player)
        print_moves(node, board)
        print_options(node)
        node, command = prompt(node, board)

    access.save_item(filepath, root)    

def print_turn(board) :
    print("")
    if (board.turn) :
        print("WHITE to play.\n")
    else :
        print("BLACK to play.\n")

# prints repertoire moves for the given node
def print_moves(node, board) :
    if (node.player_to_move) :
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

def prompt(node, board) :
    command = input("\n:")    
    if (command == "b" and node.parent != None) :
        node = pop_move(node,board)
    elif (command == "d" and len(node.variations) != 0) :
        delete_move(node,board)            
    elif (command == "p" and len(node.variations) > 1) :
        promote_move(node,board)
    elif (represents_int(command) and
          1 <= int(command) <= len(node.variations)) :
        node = play_move(node, board, int(command) - 1)
    elif (is_valid_uci(command, board) or
          is_valid_san(command, board)) :
        node = add_move(node, board, command)
    return node, command

def pop_move(node, board) :
    board.pop()
    return node.parent

def delete_move(node,board) :
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

def promote_move(node,board) :
    command = input("ID to promote: ")
    if (represents_int(command) and
        1 <= int(command) <= len(node.variations)) :
        index = int(command) - 1
        node.promote_to_main(node.variations[index])

def play_move(node, board, variation_index) :
    node = node.variations[variation_index]
    board.push(node.move)
    return node    

def add_move(node, board, command) :
    if (is_valid_uci(command, board)) :
        move = chess.Move.from_uci(command)
    else :
        move = board.parse_san(command)
    if (node.has_variation(move)) :
        print("\nMove already exists.")
        input("Hit [Enter] to continue :")
    else :
        add_node(node,move)
        board.push(move)        
        node = node.variation(move)
    return node
    
def add_node(node, move) :
    new_node = node.add_variation(move)
    new_node.player_to_move = not node.player_to_move    
    if (new_node.player_to_move) :
        new_node.training = False        
    else :
        new_node.training = TrainingData()

def is_valid_uci(string,board) :
    for move in board.legal_moves :
        if (string == move.uci()) :
            return True
    return False

def is_valid_san(string,board) :
    for move in board.legal_moves :
        if (string == board.san(move)) :
            return True
    return False

def new_item(filepath) :    
    colour = select_colour(filepath)
    position = select_position(filepath, colour)
    create_item(filepath, position, colour)
    
def new_item_title(filepath) :
    clear()
    width = 22
    name = paths.item_name(filepath)
    print("CREATING NEW ITEM ->".ljust(width) + name)
    print("")
    print("CATEGORY".ljust(width) + paths.category_name(filepath))
    print("COLLECTION".ljust(width) +paths.collection_name(filepath))
    print("")
    
def select_colour(filepath) :
    command = ""
    while (command != "w" and command != "b") :
        new_item_title(filepath)
        command = input("Select playing colour (w/b): ")
    if (command == "w") :
        return True
    else :
        return False

def create_item(filepath, position, colour) :
    root = chess.pgn.Game()
    root.setup(position)
    root.meta = MetaData("Meta-name-is-deprecated", colour)
    root.training = False
    root.player_to_move = (colour == position.turn)
    access.save_item(filepath, root)

    
# prompts user to choose starting position
def select_position(filepath, colour) :
    board = chess.Board()
    command = "."
    while(command != "") :
        new_item_title(filepath)
        print("Choose starting position.\n")
        print_board(board, colour)
        position_options(board)
        command = position_prompt(board)
    return board

def position_options(board) :
    print("<move> play move")
    print("<Enter> select position")
    if (len(board.move_stack) != 0) :
        print("'b' backup")
    else :
        print("")
        
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

