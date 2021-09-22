# MODULE UI.py
# this file is part of Opening Trainer by Joshua Blinkhorn

# SYNOPSIS
# Provides the user interface.
# This is a command line interface consisting largely of menus
# navigated by typed commands.

import os
import stats

import chess
import chess.pgn
import time
import pickle
import datetime
import time
import shutil

from graphics import print_board, clear
from training import TrainingData, MetaData, play_card, handle_card_result, generate_training_queue

def main_menu(dirpath):
    command = ""
    while(command != "c") :
        collections = os.listdir(dirpath)
        collections.sort()        
        num_collections = len(collections)
        clear()
        main_overview(dirpath, collections)
        main_options(collections)

        command = (input("\n:"))
        if (represents_int(command) and
            1 <= int(command) <= num_collections) :
            index = int(command) - 1
            collection_menu(dirpath + '/' + collections[index])
        elif (command == "n") :
            new_collection(dirpath)
        elif (command == "d" and num_collections != 0) :
            delete_collection(dirpath, collections)

def main_overview(dirpath, collections) :
    print("YOUR COLLECTIONS")
    print("")
    if (len(collections) == 0) :
        print("You have none!")
        return
    header()
    for index, collection in enumerate(collections) :
        col_path = dirpath + '/' + collection
        info_row(stats.collection_stats(col_path),
                 collection,
                 index + 1)

def info_row(info, name, index) :
    waiting = info[stats.STAT_WAITING]
    learned = info[stats.STAT_LEARNED]        
    size = info[stats.STAT_SIZE]
    if (size != 0) :
        coverage = int(round(learned / size * 100))
        coverage = (str(coverage) + "% ").rjust(5)
    else :
        coverage = "".ljust(5)
        
    info = str(index).ljust(3) + coverage
    info += name.ljust(20)
    info += str(waiting).ljust(9)
    info += str(learned).ljust(9)
    info += str(size).ljust(7)
    print(info)

def main_options(collections) :
    num_collections = len(collections)
    print ("")
    if (num_collections != 0) :
        print("[ID] select")
    print("'n' new")
    if (num_collections != 0) :
        print("'d' delete")
    print("'c' close")

# creates a new opening for the given colour
def new(dirpath) :    
    name = input("Name: ")
    new_path = dirpath + "/" + name
    while (os.path.exists(new_path)) :
        name = input("That name is taken.\nChoose another: ")
        new_path = dirpath + "/" + name
    os.mkdir(new_path)

def delete(dirpath, names) :
    command = input("ID to delete: ")
    if (represents_int(command) and
        1 <= int(command) <= len(names)) :
        index = int(command) - 1
        name = names[index]
        print (f"You are about to permanently delete `{name}'.")
        check = input("Are you sure? :")
        if (check == "y") :
            path = dirpath + "/" + name
            shutil.rmtree(path)

def collection_menu(dirpath):
    command = ""
    while(command != "c") :
        categories = os.listdir(dirpath)
        categories.sort()        
        num_categories = len(categories)
        clear()
        collection_overview(dirpath, categories)
        collection_options(dirpath, categories)

        command = (input("\n:"))
        if (represents_int(command) and
            1 <= int(command) <= num_categories) :
            index = int(command) - 1
            category_menu(dirpath + '/' + categories[index])
        elif (command == "n") :
            new_category(dirpath)
        elif (command == "d" and num_categories != 0) :
            delete_category(dirpath)

def collection_overview(dirpath, categories) :
    print("COLLECTION " + collection_name(dirpath))
    print("")
    if (len(categories) == 0) :
        print("There are no categories in this collection.")
        return
    collection_header()
    for index, category in enumerate(categories) :
        category_info(dirpath, category, index + 1)

def collection_header() :
    header = "ID".ljust(3) + "COV.".ljust(5) + "CATEGORY".ljust(20)
    header += "WAITING".ljust(9) + "LEARNED".ljust(9)
    header += "TOTAL".ljust(6)
    print(header)

def category_info(dirpath, category, index) :
    filepath = dirpath + '/' + category
    info = stats.category_stats(filepath)
    waiting = info[stats.STAT_WAITING]
    learned = info[stats.STAT_LEARNED]        
    size = info[stats.STAT_SIZE]
    if (size != 0) :
        coverage = int(round(learned / size * 100))
        coverage = (str(coverage) + "% ").rjust(5)
    else :
        coverage = "".ljust(5)
        
    info = str(index).ljust(3) + coverage
    info += category.ljust(20)
    info += str(waiting).ljust(9)
    info += str(learned).ljust(9)
    info += str(size).ljust(7)
    print(info)
    
def collection_options(dirpath, categories) :
    num_categories = len(categories)
    print ("")
    if (num_categories != 0) :
        print("[ID] select")
    print("'n' new")
    if (num_categories != 0) :
        print("'d' delete")
    print("'c' close")

# creates a new opening for the given colour
def new_category(dirpath) :    
    name = input("Name: ")
    category_path = dirpath + "/" + name
    while (os.path.exists(category_path)) :
        name = input("That name is taken.\nChoose another: ")
        category_path = dirpath + "/" + name
    os.mkdir(category_path)

def delete_category(dirpath) :
    categories = os.listdir(dirpath)
    categories.sort()
    command = input("ID to delete: ")
    if (represents_int(command) and
        1 <= int(command) <= len(categories)) :
        index = int(command) - 1
        category = categories[index]
        print (f"You are about to permanently delete `{category}'.")
        check = input("Are you sure? :")
        if (check == "y") :
            category_path = dirpath + "/" + category
            shutil.rmtree(category_path)
    
#################
# category menu #
#################
            
def category_menu(dirpath):
    command = ""
    while(command != "c") :
        items = os.listdir(dirpath)
        items.sort()
        clear()
        category_overview(dirpath, items)
        category_options(items)
        
        command = (input("\n:"))        
        if (represents_int(command) and
            1 <= int(command) <= len(items)) :
            item_index = int(command) - 1
            filepath = dirpath + "/" + items[item_index]
            item_menu(filepath)
        elif (command == "n") :
            new_item(dirpath)
        elif (command == "d" and len(items) != 0) :
            delete_item(dirpath)

def category_overview(dirpath, items) :
    print("CATEGORY   " + category_name(dirpath))
    print("COLLECTION " + collection_name(dirpath))
    print("")
    if (len(items) == 0) :
        print("There no items in this category.")
        return
    header()
    for index, item in enumerate(items) :
        item_info(dirpath, item, index + 1)

def header() :
    string = "ID".ljust(3) + "COV.".ljust(5)
    string += "ITEM".ljust(20) + "WAITING".ljust(9) 
    string += "LEARNED".ljust(9) + "TOTAL".ljust(6)
    print(string)

def item_info(dirpath, item, index) :
    filepath = dirpath + '/' + item
    item_name = item[:-4]
    info = stats.item_stats(filepath)
    waiting = info[stats.STAT_WAITING]
    learned = info[stats.STAT_LEARNED]        
    size = info[stats.STAT_SIZE]
    if (size != 0) :
        coverage = int(round(learned / size * 100))
        coverage = (str(coverage) + "% ").rjust(5)
    else :
        coverage = "".ljust(5)
        
    info = str(index).ljust(3) + coverage
    info += item_name.ljust(20)
    info += str(waiting).ljust(9)
    info += str(learned).ljust(9)
    info += str(size).ljust(7)
    print(info)
    
def category_options(items) :
    print ("")
    if (len(items) != 0) :
        print("[ID] select")
    print("'n' new")
    if (len(items) != 0) :
        print("'d' delete")
    print("'c' close")

# creates an empty repertoire for a new variation
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

            
##################
# item menu #
##################

# displays the overview of the given repertoire `name'

def item_menu(filepath) :
    command = ""
    while(command != "c") :
        info = stats.item_stats_full(filepath)        
        clear()
        item_header(filepath, info)
        item_overview(info)
        item_options(info)
        command = input("\n:")
        if (command == "m") :
            manage(filepath)
        elif (command == "t") :
            train(filepath)

def item_header(filepath, info) :
    width = 14
    waiting = info[stats.STAT_NEW] + info[stats.STAT_FIRST_STEP]
    waiting += info[stats.STAT_SECOND_STEP] + info[stats.STAT_DUE]  
    if (waiting > 0) :
        status_msg = "training available"
    else :
        status_msg = "up to date"    
    print("ITEM".ljust(width) + item_name(filepath))
    print("CATEGORY".ljust(width) + category_name(filepath))
    print("COLLECTION".ljust(width) + collection_name(filepath))
    print("STATUS".ljust(width) + status_msg)

def item_name(filepath) :
    path = filepath.split('/')
    return path[3][:-4]

def category_name(filepath) :
    path = filepath.split('/')
    return path[2]

def collection_name(filepath) :
    path = filepath.split('/')
    return path[1]

def item_overview(info) :
    width = 14
    learning = info[stats.STAT_FIRST_STEP]
    learning += info[stats.STAT_SECOND_STEP]

    print("")
    print("New".ljust(width) + str(info[stats.STAT_NEW]))
    print("Learning".ljust(width) + str(learning))
    print("Due".ljust(width) + str(info[stats.STAT_DUE]))
    print("")
    print("In review".ljust(width) + str(info[stats.STAT_REVIEW]))
    print("Inactive".ljust(width) + str(info[stats.STAT_INACTIVE]))
    print("Reachable".ljust(width) + str(info[stats.STAT_REACHABLE]))
    print("Total".ljust(width) + str(info[stats.STAT_TOTAL]))

def item_options(info) :
    waiting = info[stats.STAT_NEW] + info[stats.STAT_FIRST_STEP]
    waiting += info[stats.STAT_SECOND_STEP] + info[stats.STAT_DUE]
    print("")
    if (waiting > 0) :
        print("'t' train")
    print("'m' manage")
    print("'c' close")
    
###############
# manage menu #
###############

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

# sets the card statuses based on the current environment
        

##############
# train menu #
##############

def train(variation_path):
    repertoire = access.load_item(variation_path)
    player = repertoire.meta.player
    board = repertoire.board()
    node = repertoire        

    # generate queue
    queue = generate_training_queue(repertoire,board)
    # play queue

    command = ""
    while(len(queue) != 0) :
        card = queue.pop(0)
        counts = stats.training_stats(repertoire)
        clear()
        print(f"{counts[0]} {counts[1]} {counts[2]} {counts[5]}")
        result = play_card(card,repertoire)
        if (result == "CLOSE") :
            break
        handle_card_result(result,card,queue,repertoire)

    # save and quit trainer
    access.save_item(variation_path, repertoire)


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

def delete_variation(colour, opening, variations) :
    # TODO: the prompting should go in the calling function
    command = input("\nID to delete:")
    if (represents_int(command) and 1 <= int(command) <= len(variations)) :
        index = int(command) - 1
        variation = variations[index]
        print (f"you are about to permanently delete `{variation}'.")
        check = input("are you sure:")
        if (check == "y") :
            variation_path = "Repertoires/" + colour + "/" + opening + "/" + variation
            os.remove(variation_path)

def rpt_path(name) :
    return rep_path + "/" + name + ".rpt"
    
def represents_int(string):
    try: 
        int(string)
        return True
    except ValueError:
        return False

# checks whether a string is a legal move in uci notation
def is_valid_uci(string,board) :
    for move in board.legal_moves :
        if (string == move.uci()) :
            return True
    return False
    
