import os
import chess
import chess.pgn
import random
import time
import pickle
import datetime
import shutil
import rep

########
# misc #
########

# path to data directory
rep_path = "Repertoires"

# returns repertoire filepath (wrt root) from repertoire name
def rpt_path(name) :
    return rep_path + "/" + name + ".rpt"

# returns repertoire name from repertoire filepath (wrt rep_path)
def rpt_name(filename) :
    return filename[:-4]

def represents_int(string):
    try: 
        int(string)
        return True
    except ValueError:
        return False

# node maintenence

def is_training_node(node,player) :
    return (node.board().turn != player and node.parent != None)

# tells you whether a training node is the last training node in that line

def is_leaf(training_node) :
    if (is_end(tr_node)) :
        return True
    for child in training_node.variations :
        if (not child.is_end()) :
            return False
    return True

# returns the set of responses at or deeper than the given node
def get_responses(node,root) :
    responses = []
    if (is_response(node,root)) :
        responses.append(node)
    if (not is_end(node)) :
        for child in node.variations :
            responses += get_responses(child,root)
    return responses

# checks whether a string is a legal move in uci notation
def is_valid_uci(string,board) :
    validity = False
    for move in board.legal_moves :
        if (string == move.uci()) :
            validity = True
            break
    return validity

# `clears' the screen
def clear() :
    for x in range(40) :
        print("")

# prints the side to move
def print_turn(board) :
    print("")
    if (board.turn) :
        print("WHITE to play.")
    else :
        print("BLACK to play.")

# pretty prints the board
def print_board(board) :
    print("")
    print(board.unicode(invert_color = True, empty_square = "."))

# prints repertoire moves for the given node
def print_moves(node) :
    player = get_player(node.game())
    if (node.is_end()) :
        if (node.board().turn == player) :
            print("\nNo responses.")
        else :
            print("\nNo candidates.")
    else :
        if (node.board().turn == player) :
            print("\nResponses:")
            for response in node.variations :
                print(response.move.uci())
        else :
            print("\nCandidate moves:")
            for candidate in node.variations :
                print(candidate.move.uci())

#########
# new() #
#########

# creates a new repertoire
def new_repertoire() :
    
    # get user choices
    board = get_starting_position()
    clear()
    print_board(board)
    colour = input("\nYou play as:\n'w' for White\n'b' for  Black\n\n:")
    while (colour != "b" and colour != "w"):
        colour = input(":")
    name = input("\nName:")
    while (os.path.exists(rpt_path(name))) :
        name = input("That name is taken.\nChoose another:")

    # create the repertoire
    rpt = chess.pgn.Game()
    rpt.setup(board)
    rpt.meta = rep.MetaData(name, colour == "w")
    save_repertoire(rpt)
    clear()
    print(f"Repertoire {name} created.")

def delete_repertoire(filenames) :
    command = input("\nID to delete:")
    if (represents_int(command) and 1 <= int(command) <= len(filenames)) :
        index = int(command) - 1
        print (f"you are about to permanently delete `{names[index]}'.")
        check = input("are you sure:")
        if (check == "y") :
            os.remove(filenames[index])

def save_repertoire (repertoire) :
    filename = rpt_path(repertoire.meta.name)
    with open(filename, "wb") as file :
        pickle.dump(repertoire,file)

def open_repertoire (filename) :
    filepath = rep_path + "/" + filename
    with open(filepath, "rb") as file :
        return pickle.load(file)

# TODO - rewrite this function into the current style
# prompts user to choose starting position

def get_starting_position() :
    board = chess.Board()
    while(True) :
        clear()
        print("\nChoose starting position.")
        print_board(board)
        uci = input(":")

        if (uci == "Q") :
            return "QUIT"
        elif (uci == "B") :
            try:
                board.pop()
            except IndexError:
                print("Cannot go back from root position.")
        elif (is_valid_uci(uci,board)) :
            board.push(chess.Move.from_uci(uci))
            print("Choose starting position.")
            print_board(board)
        elif (uci == "") :
            return board

############
# manage() #
############

def print_node_overview(node) :

    print_turn(node.board())
    print_board(node.board())
    print_moves(node)

def print_node_options(node) :
    print("")
    if (node.parent != None) :
        print("'b' back")
    if (not is_end(node)) :
        print("'d' delete")
    if (len(node.variations) > 1) :
        print("'p' promote")
    print ("'c' close")
    print ("<move> enter move")

def delete_node(node,board) :
    command = input("delete move:")
    if (is_valid_uci(command,board)) :
        move = chess.Move.from_uci(command)
        if (node.has_variation(move)) :
            print(f"You are about to permanently delete the move '{command}'.")
            command = input("are you sure:")
            if (command == "y") :
                node.remove_variation(move)

def promote_node(node,board) :
    command = input("promote move:")
    if (is_valid_uci(command,board)) :
        move = chess.Move.from_uci(command)
        if (node.has_variation(move)) :
            node.promote(move)

def add_move(node) :
    move = chess.Move.from_uci(command)
    if (not node.has_variation(move)) :
        new_node = node.add_variation(move)
        if (is_training_node(new_node)) :
            new_node.training = rep.TrainingData()

# user management of repertoire as a pgn
def manage(filename):
    repertoire = open_repertoire(filename)
    node = repertoire        
        
    command = ""
    while(command != "c") :
        clear()
        print_node_overview(node)
        print_node_options(node)
        command = input("\n:")
        if (command == "b" and node.parent != None) :
            node = node.parent
        elif (command == "d" and len(node.variations) != 0) :
            delete_move(node,board)
        elif (command == "p" and len(node.variations) > 1) :
            promote_move(node,board)
        elif (is_valid_uci(command,board)) :
            add_move(node)
            node = node.variation(move)

    save_repertoire(repertoire)
    clear()
    print(f"Saved {rpt_name(filename)}.")


##########
# play() #
##########

# generates a queue of `lines'
def play(file_path) :
    repertoire = open_repertoire(file_path)
    start = navigate_to_node(repertoire)
    player = get_player(repertoire)
    nodes = get_end_nodes(start,player)
    if (len(nodes) == 0) :
        print("No lines generated.")
        return
    queue = []
    for end in nodes :
        # remove trivial lines
        print("\nFound end:")
        print_board(end.board())
        if (start != end and (start.board().turn == player or start.variation(0) != end)) :
            queue.append([start,end,player])
            print("\nAppended end:")
            print_board(end.board())

        random.shuffle(queue)
    play_session(queue)

# prompts user to choose a node in the repertoire subtree
# also used by train()
def navigate_to_node(repertoire) :
    node = repertoire
    while (True) :
        clear()
        print("Navigate to position.")
        result = query_node(node)

        if (result == "QUIT") :
            return "QUIT"
        elif (result == "BACK") :
            if (node != repertoire) :
                node = node.parent
        elif (result == "DELETE" or result == "PROMOTE" or result == "INVALID") :
            continue
        elif (result == "SAVE") :
            return node
        else :
            move = chess.Move.from_uci(result)
            node = node.variation(move)
    
# plays through the queue of lines
def play_session(queue):
    # train lines
    # `line' here is the end node                          
    while(len(queue) != 0) :
        clear()
        print("New line.")
        print("\nLines remaining: " + str(len(queue)))
        line = queue.pop(0)
        result = play_line(line)
        if (result == "QUIT") :
            return
        if (result == "FAILURE") :
            offset = min(2, len(queue) - 1)
            queue.insert(offset, line)
    # wrap up
    clear()
    print("Deck complete.")

# plays a line against the user
def play_line(line) :
    # setup
    start = line[0]
    end = line[1]
    player = line[2]
    
    # make main line
    node = end
    while (node != start) :
        move = node.move
        node = node.parent
        node.promote_to_main(move)
    board = node.board()

    # play line
    while (node != end) :
        if (node.board().turn == player) :
            # prompt for move and handle it
            print_turn(node.board())
            print_board(node.board())
            uci = input("\n:")
            node = node.variation(0)
            clear()
            print_board(node.board())
            uci = "\n:"
            while (uci != "") :
                if (uci == "Q") :
                    return "QUIT"
                if (uci == failure_string) :
                    return "FAILURE"
                clear()
                print_board(node.board())
                uci = input("\n:")
        else :
            node = node.variation(0)

# plucks the leaf nodes from node's subtree
# leaves in which the user is to move are ignored --
# such leaves have no user response
def get_end_nodes(node,player) :

    nodes = []
    if (node.is_end()) :
        if (node.board().turn != player) :
            nodes.append(node)
    else :
        if (node.board().turn != player) :
            is_effective_end = True
            for child in node.variations :
                if (not child.is_end()) :
                    is_effective_end = False
            if (is_effective_end) :
                nodes.append(node)

        for child in node.variations :
            nodes += get_end_nodes(child,player)
    return nodes

###########
# train() #
###########

# prompts user to select starting position, then invokes training session
def train(file_path) :
    repertoire = open_repertoire(file_path)
    node = navigate_to_node(repertoire)
    queue = get_training_nodes(node,get_player(repertoire))
    if (len(queue) == 0) :
        print("No training positions generated.")
        return
    random.shuffle(queue)
    train_session(queue)
    
# generates cards and trains them until the deck is complete
def train_session(queue):

    # create card queue
    # train cards
    while(len(queue) != 0) :
        clear()
        print("Cards remaining: " + str(len(queue)) + "\n")
        card = queue.pop(0)
        result = train_card(card)
        if (result == "QUIT") :
            return
        if (result == "FAILURE") :
            offset = min(2, len(queue) - 1)
            queue.insert(offset, card)

    # wrap up
    clear()
    print("Deck complete.")

# basic flash card recognition routine
    
def train_card(card) :    
    front = card
    print_turn(front.board())
    print_board(front.board())
    uci = input("\n:")
    back = front.variation(0)
    clear()
    print_board(back.board())
    uci = input("\n:")
    while (uci != "") :
        if (uci == "Q") :
            return "QUIT"
        if (uci == failure_string) :
            return "FAILURE"
        uci = input(":")

# plucks the training positions from node's subtree
def get_training_nodes(node,player) :

    nodes = []
    if (not node.is_end()) :
        if (node.board().turn == player) :
            nodes.append(node)
            print("appended node:")
            print_board(node.board())
            print("")
        for child in node.variations :
            nodes += get_training_nodes(child,player)

    return nodes

##########
# main() #
##########


# displays the overview of the given repertoire `name'

def print_repertoire_overview(repertoire) :
    # setup
    deck_width = 14
    info_width = 11
    status_descriptors = ["insufficient for training","training available","up to date"]    
    lines = repertoire.lines
    positions = repertoire.positions

    # pretty printing
    print("Repertoire: " + repertoire.name)
    print("Status    : " + status_descriptors[repertoire.status()])
    header = "\n" + "".ljust(deck_width) + "new".ljust(info_width)
    header += ("learning".ljust(info_width) + "due".ljust(info_width))
    header += ("inactive".ljust(info_width) + "unreachable".ljust(info_width))
    print(header)
    info = "Lines".ljust(deck_width) + str(len(lines.new)).ljust(info_width)
    info += str(len(lines.learning)).ljust(info_width)
    info += str(len(lines.due_pile())).ljust(info_width)
    info += str(len(lines.inactive)).ljust(info_width)
    info += str(len(lines.unreachable)).ljust(info_width)
    print(info)
    info = "Positions".ljust(deck_width) + str(len(positions.new)).ljust(info_width)
    info += str(len(positions.learning)).ljust(info_width)
    info += str(len(positions.due_pile())).ljust(info_width)
    info += str(len(positions.inactive)).ljust(info_width)
    info += str(len(positions.unreachable)).ljust(info_width)
    print(info)

def print_repertoire_options(repertoire) :
    status = repertoire.status()
    print("\n'm' manage")
    if (status == rep.SCHEDULED) :
        print("'t' train")
    print("'c' close")
    
def repertoire_menu(filename) :
    command = ""
    while(command != "c") :
        repertoire = open_repertoire(filename)
        clear()
        print_repertoire_overview(repertoire)
        print_repertoire_options(repertoire)
        command = input("\n:")
        if (command == "m") :
            manage(name)
        elif (command == "t") :
            True

def print_overview(names) :

    id_width = 3
    name_width = 20
    info_width = 12

    if (len(names) == 0) :
        print("You currently have no repertoires.")
        return

    # print header
    header = "ID".ljust(id_width) + "NAME".ljust(name_width)
    header += "LINES".ljust(info_width) + "POSITIONS".ljust(info_width)
    print(header)
    
    # print the stats for each repertoire
    #for index, name in enumerate(names) :
    #   repertoire = open_repertoire(filename)
    #   line = str(index + 1).ljust(id_width) + repertoire.name.ljust(name_width)
        #for deck in [repertoire.lines,repertoire.positions] :
        #    line += f"{len(deck.new)} {len(deck.learning)} {len(deck.due_pile())}".ljust(info_width)
        #print(line)
            
def print_options(filenames) :
    print ("")
    if (len(filenames) != 0) :
        print("[ID] select")
    print("'n' new")
    if (len(filenames) != 0) :
        print("'d' delete")
    print("'q' quit")
            
def main():
    command = ""
    while(command != "q") :
        filenames = os.listdir(rep_path)    
        clear()
        print_overview(filenames)
        print_options(filenames)
        command = (input("\n:"))
        
        if (represents_int(command) and 1 <= int(command) <= len(filenames)) :
            index = int(command) - 1
            repertoire_menu(filenames[index])
        elif (command == "n") :
            new_repertoire()
        elif (command == "d" and len(filenames) != 0) :
            delete_repertoire(filenames)

def open_file_msg() :
    print("Please create or load a repertoire first.")
            
############### 
# entry point #
###############

main()


# temp copied code

"""        
    node = game
    board = node.board()
    player = board.turn

    result = query_node(node)
    
    while (result != "SAVE") :
        if (result == "BACK") :
            if (node != game) :
                node = node.parent
                
        elif (result == "DELETE") :
            uci = input("delete move:")
            if (is_valid_uci(uci,node.board())) :
                move = chess.Move.from_uci(uci)
                if (node.has_variation(move)) :
                    node.remove_variation(move)

        elif (result == "PROMOTE") :
            uci = input("promote move:")
            if (is_valid_uci(uci,node.board())) :
                move = chess.Move.from_uci(uci)
                if (node.has_variation(move)) :
                    node.promote_to_main(move)
                           
        elif (result != "INVALID") :
            move = chess.Move.from_uci(result)
            if (not node.has_variation(move)) :
                node.add_main_variation(move)
            node = node.variation(move)
            board = node.board()                        

        result = query_node(node)
"""

def folder_path(name) :
    return data_path + name + "/"
def pgn_path(name) :
    return folder_path(name) + name + ".pgn"
failure_string = " "

data_path = "Repertoires/"

##########
# load() #
##########

# loads a saved repertoire
# checks that the file exists and can be opened as a pgn by python-chess
# return the path to the loaded repertoire file
def load() :
    clear()
    file_path = input("filename:")
    try:
        pgn = open(file_path, "r")
    except:
        clear()
        print("\nFile error.")
        return
    repertoire = chess.pgn.read_game(pgn)
    pgn.close()
    clear()
    print("Loaded repertoire `" + str(file_path) + "'.")
    return file_path


# prompts user for input at the given node
def query_node(node):
    print_turn(node.board())
    print_board(node.board())
    print_moves(node)
    return get_input(node)

# returns the parsed repertoire from its file path
def get_pgn_game(repertoire) :
    game = chess.pgn.read_game(repertoire.pgn)
    return game

def is_candidate(node,player) :
    return (node.board().turn == player and node.parent != None)

def is_response(node,player) :
    return (node.board().turn != player and node.parent != None)

