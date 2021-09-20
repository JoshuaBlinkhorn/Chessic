import os
import chess
import chess.pgn

import time
import pickle
import datetime
import time
import shutil

import stats
import items

from graphics import print_board, clear
from training import TrainingData, MetaData, play_card, handle_card_result, generate_training_queue
        
########
# misc #
########

# path to data directory
rep_path = "Repertoires"

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

############
# printing #
############

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

###########################################
# creating / saving / opening repertoires #
###########################################

def rpt_path(name) :
    return rep_path + "/" + name + ".rpt"

def rpt_name(filename) :
    return filename[:-4]

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

##############
# statistics #
##############

        
#############
# main menu #
#############

def main_menu():
    command = ""
    while(command != "q") :
        white_openings = os.listdir("Repertoires/White")
        black_openings = os.listdir("Repertoires/Black")
        filenames = os.listdir(rep_path)
        clear()
        print_main_overview()
        print_main_options()
        command = (input("\n:"))
        
        if (command == "w") :
            colour_menu("White")
        elif (command == "b") :
            colour_menu("Black")

def print_main_overview() :

    # print header
    header = "COV.".ljust(5) + "COLOUR".ljust(10)
    header += "WAITING".ljust(9) + "LEARNED".ljust(9)
    header += "TOTAL".ljust(6)
    print(header)
    
    # print the stats for each colour
    for colour in ["White","Black"] :
        waiting = learned = total = 0
        colour_path = "Repertoires/" + colour
        for opening in os.listdir(colour_path) :
            opening_path = colour_path + "/" + opening
            for filename in os.listdir(opening_path) :
                repertoire_path = opening_path + "/" + filename
                repertoire = items.load_item(repertoire_path)
                counts = stats.training_stats(repertoire)
                waiting += counts[0] + counts[1] + counts[2] + counts[5]
                learned += counts[3]
                total += counts[6]
        if (total != 0) :
            coverage = int(round(learned / total * 100))
            info = (str(coverage) + "% ").rjust(5)
        else :
            info = "".ljust(5)
        info += colour.ljust(10)
        info += str(waiting).ljust(9)
        info += str(learned).ljust(9)
        info += str(total).ljust(7)
        print(info)

def print_main_options() :
    print ("")
    print("'w' white")
    print("'b' black")
    print("'q' quit")

###############
# colour menu #
###############

def colour_menu(colour):

    colour_path = "Repertoires/" + colour
    command = ""
    while(command != "c") :
        openings = os.listdir(colour_path)
        openings.sort()
        clear()
        print_colour_overview(colour,openings)
        print_colour_options(openings)
        command = (input("\n:"))
        
        if (represents_int(command) and 1 <= int(command) <= len(openings)) :
            index = int(command) - 1
            opening_menu(colour, openings[index])
        elif (command == "n") :
            new_opening(colour)
        elif (command == "d" and len(openings) != 0) :
            delete_opening(colour, openings)

def print_colour_overview(colour,openings) :

    opening_width = 20

    if (len(openings) == 0) :
        print("You currently have no openings here.")
        return

    # print header
    header = "ID".ljust(3) + "COV.".ljust(5) + "OPENING".ljust(opening_width)
    header += "WAITING".ljust(9) + "LEARNED".ljust(9)
    header += "TOTAL".ljust(6)
    print(header)
    
    # print the stats for each repertoire
    for index, opening in enumerate(openings) :
        opening_path = "Repertoires/" + colour + "/" + opening
        waiting = learned = total = 0
        category_stats = stats.category_stats(opening_path)
        for variation in os.listdir(opening_path) :
            variation_path = opening_path + "/" + variation
            repertoire = items.load_item(variation_path)
            counts = stats.training_stats(repertoire)
            waiting += counts[0] + counts[1] + counts[2] + counts[5]
            learned += counts[3]
            total += counts[6]

        id = index + 1
        info = str(id).ljust(3)
        if (total != 0) :
            coverage = int(round(learned / total * 100))
            info += (str(coverage) + "% ").rjust(5)
        else :
            info += "".ljust(5)
        info += str(opening).ljust(opening_width)
        info += str(category_stats[stats.STAT_WAITING]).ljust(9)
        info += str(category_stats[stats.STAT_LEARNED]).ljust(9)
        info += str(category_stats[stats.STAT_SIZE]).ljust(7)
        print(info)

def print_colour_options(openings) :

    print ("")
    if (len(openings) != 0) :
        print("[ID] select")
    print("'n' new")
    if (len(openings) != 0) :
        print("'d' delete")
    print("'c' close")

################
# opening menu #
################
            
def opening_menu(colour, opening):

    opening_path = "Repertoires/" + colour + "/" + opening
    command = ""
    while(command != "c") :
        variations = os.listdir(opening_path)
        variations.sort()
        clear()
        print_opening_overview(colour, opening, variations)
        print_opening_options(variations)
        command = (input("\n:"))
        
        if (represents_int(command) and 1 <= int(command) <= len(variations)) :
            index = int(command) - 1
            variation_path = opening_path + "/" + variations[index]
            variation_menu(variation_path)
        elif (command == "n") :
            new_variation(colour, opening)
        elif (command == "d" and len(variations) != 0) :
            delete_variation(colour, opening, variations)

def print_opening_overview(colour, opening, variations) :

    name_width = 20

    if (len(variations) == 0) :
        print("You currently have no variations here.")
        return

    # print header
    header = "ID".ljust(3) + "COV.".ljust(5) + "VARIATION".ljust(name_width)
    header += "WAITING".ljust(9) + "LEARNED".ljust(9)
    header += "TOTAL".ljust(6)
    print(header)
    
    # print the stats for each repertoire
    for index, variation in enumerate(variations) :
        variation_path = "Repertoires/" + colour + "/" + opening + "/" + variation
        repertoire = items.load_item(variation_path)
        counts = stats.training_stats(repertoire)
        waiting = counts[0] + counts[1] + counts[2] + counts[5]
        learned = counts[3]
        total = counts[6]

        id = index + 1
        info = str(id).ljust(3)
        if (total != 0) :
            coverage = int(round(learned / total * 100))
            info += (str(coverage) + "% ").rjust(5)
        else :
            info += "".ljust(5)
        info += str(variation.split('.')[0]).ljust(name_width)
        info += str(waiting).ljust(9)
        info += str(learned).ljust(9)
        info += str(total).ljust(7)
        print(info)

def print_opening_options(variations) :
    print ("")
    if (len(variations) != 0) :
        print("[ID] select")
    print("'n' new")
    if (len(variations) != 0) :
        print("'d' delete")
    print("'c' close")

# creates a new opening for the given colour
def new_opening(colour) :
    
    colour_path = "Repertoires/" + colour
    name = input("\nName:")
    opening_path = colour_path + "/" + name
    while (os.path.exists(opening_path)) :
        name = input("That name is taken.\nChoose another:")
        opening_path = colour_path + "/" + name
    os.mkdir(opening_path)

def delete_opening(colour, openings) :
    # TODO: the prompting should go in the calling function
    command = input("\nID to delete:")
    if (represents_int(command) and 1 <= int(command) <= len(openings)) :
        index = int(command) - 1
        opening = openings[index]
        print (f"you are about to permanently delete `{opening}'.")
        check = input("are you sure:")
        if (check == "y") :
            opening_path = "Repertoires/" + colour + "/" + opening
            shutil.rmtree(opening_path)
    
##################
# variation menu #
##################

# displays the overview of the given repertoire `name'

def variation_menu(variation_path) :
    command = ""
    while(command != "c") :
        repertoire = items.load_item(variation_path)
        counts = stats.item_stats_full(variation_path)
        clear()
        print_variation_overview(repertoire,counts)
        print_variation_options(repertoire,counts)
        command = input("\n:")
        if (command == "m") :
            manage(variation_path)
        elif (command == "t") :
            train(variation_path)

def print_variation_overview(repertoire,counts) :
    # setup
    tag_width = 14
    if (counts[0] + counts[1] + counts[2] + counts[5] > 0) :
        status_msg = "training available"
    else :
        status_msg = "up to date"
    
    # print header
    print("Repertoire: " + repertoire.meta.name)
    print("Status    : " + status_msg)

    # print sceduled counts
    print("")
    print("New".ljust(tag_width) + str(counts[0]))
    print("Learning".ljust(tag_width) + str(counts[1] + counts[2]))
    print("Due".ljust(tag_width) + str(counts[5]))

    # print remaining counts    
    total = stats.total_training_positions(repertoire)
    print("")
    print("In review".ljust(tag_width) + str(counts[3]))
    print("Inactive".ljust(tag_width) + str(counts[4]))
    print("Reachable".ljust(tag_width) + str(counts[6]))
    print("Total".ljust(tag_width) + str(total))

def print_variation_options(repertoire,counts) :
    print("\n'm' manage")
    if (counts[0] + counts[1] + counts[2] + counts[5] > 0) :
        print("\n't' train")
    print("'c' close")

# creates an empty repertoire for a new variation
def new_variation(colour, opening) :
    
    player = colour == "White"
    opening_path = "Repertoires/" + colour + "/" + opening
    # get user choices
    board = get_starting_position()
    if (board == "CLOSE") :
        return
    clear()
    print_board(board,True)
    #colour = input("\nYou play as:\n'w' for White\n'b' for Black\n\n:")
    #while (colour != "b" and colour != "w"):
    #    colour = input(":")
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
    items.save_item(variation_path, repertoire)

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
    
###############
# manage menu #
###############

# user management of repertoire as a pgn
def manage(variation_path):
    repertoire = items.load_item(variation_path)
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
    items.save_item(variation_path, repertoire)    
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
    repertoire = items.load_item(variation_path)
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
    items.save_item(variation_path, repertoire)

    
############### 
# entry point #
###############

main_menu()

