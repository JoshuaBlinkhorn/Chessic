# MODULE manager.py
# this file is part of Opening Trainer by Joshua Blinkhorn

# SYNOPSIS
# Provides the functionality for managing a PGN item.

import datetime
# import training
import access
import os
import chess

from graphics import print_board, clear

# user management of repertoire as a pgn
def manage(variation_path):
    repertoire = access.load_item(variation_path)
    player = repertoire.meta.player
    board = repertoire.board()
    node = repertoire        

    command = ""
    while(command != "c") :

        clear()
        print_node_overview(node,player,board)
        print_node_options(node)
        command = input("\n:")
        if (command == "b" and node.parent != None) :
            node = node.parent
            board.pop()
        elif (command == "d" and len(node.variations) != 0) :
            delete_move(node,board)
            
        elif (command == "p" and len(node.variations) > 1) :
            promote_move(node,board)
            
        elif (is_valid_uci(command,board)) :
            move = chess.Move.from_uci(command)
            if (not node.has_variation(move)) :
                add_move(node,move)
            node = node.variation(move)
            board.push(move)

    #threshold = compute_learning_threshold(repertoire)
    access.save_item(variation_path, repertoire)    
    clear()

def print_node_overview(node,player,board) :
    print_turn(board)
    print_board(board,player)
    print_moves(node)

def print_node_options(node) :
    print("")
    if (node.parent != None) :
        print("'b' back")
    if (not node.is_end()) :
        print("'d' delete")
    if (len(node.variations) > 1) :
        print("'p' promote")
    print ("'c' close")
    print ("<move> enter move")

def delete_move(node,board) :
    command = input("delete move:")
    if (is_valid_uci(command,board)) :
        move = chess.Move.from_uci(command)
        if (node.has_variation(move)) :
            print(f"You are about to permanently delete the move '{command}'.")
            command = input("are you sure:")
            if (command == "y") :
                node.remove_variation(move)

def promote_move(node,board) :
    command = input("promote move:")
    if (is_valid_uci(command,board)) :
        move = chess.Move.from_uci(command)
        if (node.has_variation(move)) :
            node.promote(move)

def add_move(node,move) :
    new_node = node.add_variation(move)
    new_node.player_to_move = not node.player_to_move
    if (node.parent == None or new_node.player_to_move) :
        new_node.training = False        
    else :
        new_node.training = TrainingData()

def is_valid_uci(string,board) :
    for move in board.legal_moves :
        if (string == move.uci()) :
            return True
    return False
        
# prints the side to move
def print_turn(board) :
    print("")
    if (board.turn) :
        print("WHITE to play.")
    else :
        print("BLACK to play.")

# prints repertoire moves for the given node
def print_moves(node) :
    if (node.player_to_move) :
        if (node.is_end()) :
            print("\nNo solutions.")
        else :
            print("\nSolutions:")
            for solution in node.variations :
                print(solution.move.uci())
    else :
        if (node.is_end()) :
            print("\nNo problems.")
        else :
            print("\nProblems:")
            for problem in node.variations :
                print(problem.move.uci())

# creates an empty repertoire for a new variation

def new_item(dirpath) :
    print(dirpath)
    input(":")

"""
def new_item(colour, opening) :
    
    player = colour == "White"
    opening_path = "Repertoires/" + colour + "/" + opening
    # get user choices
    board = get_starting_position()
    if (board == "CLOSE") :
        return
    clear()
    print_board(board,True)
    name = input("\nName:")
    while (os.path.exists(rpt_path(name))) :
        name = input("That name is taken.\nChoose another:")
    variation_path = opening_path + "/" + name + ".rpt"
        
    # create the repertoire
    repertoire = chess.pgn.Game()
    repertoire.setup(board)
    repertoire.meta = MetaData(name, player)
    repertoire.training = False
    repertoire.player_to_move = player == board.turn
    access.save_item(variation_path, repertoire)
"""

# TODO - rewrite this function into the current style
# prompts user to choose starting position
def get_starting_position() :
    board = chess.Board()
    while(True) :
        clear()
        print("\nChoose starting position.")
        print_board(board,True)
        print("\nEnter a move or hit [Enter] to select this position.")
        print("'b' to go back one move")
        print("'c' to close.")
        uci = input("\n:")

        if (uci == "c") :
            return "CLOSE"
        elif (uci == "b") :
            try:
                board.pop()
            except IndexError:
                print("Cannot go back from root position.")
        elif (is_valid_uci(uci,board)) :
            board.push(chess.Move.from_uci(uci))
        elif (uci == "") :
            return board

def rpt_path(name) :
    return rep_path + "/" + name + ".rpt"
