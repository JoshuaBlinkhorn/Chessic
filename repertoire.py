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

failure_string = " "
data_path = "Repertoires/"

def represents_int(string):
    try: 
        int(string)
        return True
    except ValueError:
        return False

# filename `macros'
    
def folder_path(name) :
    return data_path + name + "/"

def rpt_path(name) :
    return folder_path(name) + name + ".rpt"

def pgn_path(name) :
    return folder_path(name) + name + ".pgn"

# node maintenence

def is_candidate(node,root) :
    return (node.board().turn == node.game().board().turn and node != root)

def is_response(node,root) :
    return (node.board().turn != node.game().board().turn and node != root)

def is_final(response) :
    if (is_end(response)) :
        return True
    for candidate in response.variations :
        if (not candidate.is_end()) :
            return False
    return True

# returns the set of responses deeper than the given node
def get_responses(node,root) :
    responses = []
    if (is_response(node,root)) :
        responses.append(node)
    if (not is_end(node)) :
        for child in node.variations :
            responses += get_responses(child,root)
    return responses

    

# `clears' the screen
def clear() :
    for x in range(40) :
        print("")

# checks whether a string is a legal move in uci notation
def is_valid(uci,board) :
    validity = False
    for move in board.legal_moves :
        if (uci == move.uci()) :
            validity = True
            break
    return validity
        
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

# returns the parsed repertoire from its file path
def get_pgn_game(repertoire) :
    game = chess.pgn.read_game(repertoire.pgn)
    return game

# returns the user's colour for a repertoire
def get_player(repertoire) :
    return (repertoire.headers["Site"] == "W")
                
#########
# new() #
#########

# creates a new repertoire
def new() :
    
    # get starting position
    result = get_starting_position()
    if (result == "QUIT") :
        return    
    board = result
    game = chess.pgn.Game()
    game.setup(board)
        
    # get colour
    clear()
    print_board(board)
    colour = input("\nYou play as:\n'W' for White\n'B' for  Black\n\n:")
    while (colour != "B" and colour != "W"):
        if (colour == "Q") :
            return        
        colour = input(":")
        
    # get name and build folder
    name = input("\nName:")
    while (os.path.exists(data_path + name)) :
        name = input("That name is taken.\nChoose another:")
        
    # make the folder
    os.mkdir(folder_path(name))
    # build and save the retertoire
    repertoire = rep.Repertoire(name, colour)
    with open(rpt_path(name), "wb") as file :
        pickle.dump(repertoire, file)
    # build and save the pgn
    print(game, file = open(pgn_path(name), "w"), end = "\n\n")

    clear()
    print("Repertoire '" + name + "' created.")
        
    
# prompts user to choose starting position
def get_starting_position() :
    board = chess.Board()
    while(True) :
        clear()
        print("\nChoose starting position.")
        print_board(board)
        uci = input(":")

        if (uci == "Q"):
            return "QUIT"
        elif (uci == "B") :
            try:
                board.pop()
            except IndexError:
                print("Cannot go back from root position.")
        elif (is_valid(uci,board)) :
            board.push(chess.Move.from_uci(uci))
            print("Choose starting position.")
            print_board(board)
        elif (uci == "") :
            return board

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

############
# manage() #
############


def print_node_overview(node) :

    print_turn(node.board())
    print_board(node.board())
    print_moves(node)

def print_node_options(node) :
    print("")
    if (node != node.game()) :
        print("'b' back")
    if (len(node.variations) != 0) :
        print("'d' delete")
    if (len(node.variations) > 1) :
        print("'p' promote")
    print ("'c' close")
    print ("<move> enter move")


def add_move(node,move,board,root,repertoire) :  

    # create the variation node
    node.add_variation(move)

    # handle cards:
    if (is_candidate(node,root)) :

        # we have a new position - build board and card
        new_board = chess.Board()
        for history_move in board.move_stack :
            new_board.push(history_move)
        new_board.push(move)
        new_card = rep.Card(new_board)

        # add card to both decks, in the correct pile
        if (node.variation(move).is_main_variation()) :
            repertoire.lines.inactive.append(new_card)
            repertoire.positions.inactive.append(new_card)
        else:
            repertoire.lines.unreachable.append(new_card)
            repertoire.positions.unreachable.append(new_card)
            
        if (is_response(node.parent,root)) :
            # we have a superceded line - build board
            new_board = chess.Board()
            for history_move in board.move_stack :
                new_board.push(history_move)
            new_board.pop()

            # remove superceded line
            for pile in repertoire.lines.piles() :
                for index, card in enumerate(pile) :
                    if (card.board == new_board) :
                        pile.pop(index)

# TODO: bug somewhere here

def is_stack_prefix(boardA, boardB) :
    stackA = boardA.move_stack
    stackB = boardB.move_stack
    if (len(stackA) > len(stackB)) :
        return False
    if (stackB[1:len(stackA)] == stackA[1:len(stackA)]) :
        return True
    return False

def delete_move(node, move, board, root, repertoire) :

    board.push(move)
    for pile in repertoire.lines.piles() :
        for card_index, card in enumerate(pile) :
            if (is_stack_prefix(board, card.board)) :
                pile.pop(card_index)

    for pile in repertoire.positions.piles() :
        for card_index, card in enumerate(pile) :
            if (is_stack_prefix(board, card.board)) :
                pile.pop(card_index)

    board.pop()
    node.remove_variation(move)

def promote_move(node) :

    True
    
# user management of repertoire as a pgn
def manage(name):

    with open(pgn_path(name), "r", encoding = "utf-8-sig") as pgn :
        root = chess.pgn.read_game(pgn)
    with open(rpt_path(name), "rb") as file :
        repertoire = pickle.load(file)

    board = root.board()
    node = root
        
    command = ""
    while(command != "c") :
        clear()
        print_node_overview(node)
        print_node_options(node)
        command = input("\n:")
        if (command == "b" and node != root) :
            node = node.parent
            board.pop()
        elif (command == "d" and len(node.variations) != 0) :
            command = input("delete move:")
            if (is_valid(command,board)) :
                move = chess.Move.from_uci(command)
                if (node.has_variation(move)) :
                    print(f"You are about to permanently delete the move '{command}' and all of its variations and associated data.")
                    command = input("are you sure:")
                    if (command == "y") :
                        delete_move(node, move, board, root, repertoire)

        elif (command == "p" and len(node.variations) > 1) :
            command = input("promote move:")
            if (is_valid(command,board)) :
                move = chess.Move.from_uci(command)
                if (node.has_variation(move)) :
                    promote_move(node.variation(move))

        elif (is_valid(command,board)) :
            move = chess.Move.from_uci(command)
            if (not node.has_variation(move)) :
                add_move(node,move,board,root,repertoire)
            node = node.variation(move)
            board.push(move)
            
    # save repertoire
    print("Saving repertoire `" + str(name) + "'.")
    with open(rpt_path(name), "wb") as file :
        pickle.dump(repertoire, file)
    print(root, file = open(pgn_path(name), "w"), end = "\n\n")

def delete_card(board,deck) :
    card = deck.get_card(board)
    
# prompts user for input                
def get_input(node) :
    uci = input(":")
    if (uci == "Q") :
        return "QUIT"
    if (uci == "B") :
        return "BACK"
    if (uci == "D") :
        return "DELETE"
    if (uci == "P") :
        return "PROMOTE"
    if (uci == "") :
        return "SAVE"
    if (is_valid(uci,node.board())) :
        return uci
    return "INVALID"

# prompts user for input at the given node
def query_node(node):
    print_turn(node.board())
    print_board(node.board())
    print_moves(node)
    return get_input(node)

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
    
def repertoire_menu(name) :
    command = ""
    while(command != "c") :
        with open(rpt_path(name), "rb") as file :
            repertoire = pickle.load(file)
        clear()
        print_repertoire_overview(repertoire)
        print_repertoire_options(repertoire)
        command = input("\n:")
        if (command == "m") :
            manage(name)
        elif (command == "t") :
            True
            #train(name)

def print_overview(names) :

    id_width = 3
    name_width = 20
    info_width = 12

    if (len(names) == 0) :
        print("You currently have no repertoires.")
        return
        
    print("ID".ljust(id_width) + "NAME".ljust(name_width) + "LINES".ljust(info_width) + "POSITIONS".ljust(info_width))
    
    # print the stats for each repertoire
    for index, name in enumerate(names) :
        with open(rpt_path(name), "rb") as file :
            repertoire = pickle.load(file)
        line = str(index + 1).ljust(id_width) + repertoire.name.ljust(name_width)
        for deck in [repertoire.lines,repertoire.positions] :
            line += f"{len(deck.new)} {len(deck.learning)} {len(deck.due_pile())}".ljust(info_width)
        print(line)
            
def print_options(names) :
    print ("")
    if (len(names) != 0) :
        print("[ID] select")
    print("'n' new")
    if (len(names) != 0) :
        print("'d' delete")
    print("'q' quit")
            
def main():
    command = ""
    while(command != "q") :
        names = os.listdir(data_path)    
        clear()
        print_overview(names)
        print_options(names)
        command = (input("\n:"))
        
        if (represents_int(command) and 1 <= int(command) <= len(names)) :
            index = int(command) - 1
            repertoire_menu(names[index])
        elif (command == "n") :
            new()
        elif (len(names) != 0 and command == "d") :
            clear()
            print_overview(names)
            print_options(names)
            command = input("\nID to delete:")
            if (represents_int(command) and 1 <= int(command) <= len(names)) :
                index = int(command) - 1
                print (f"you are about to permanently delete `{names[index]}'.")
                check = input("are you sure:")
                if (check == "y") :
                    shutil.rmtree(folder_path(names[index]))
        
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
            if (is_valid(uci,node.board())) :
                move = chess.Move.from_uci(uci)
                if (node.has_variation(move)) :
                    node.remove_variation(move)

        elif (result == "PROMOTE") :
            uci = input("promote move:")
            if (is_valid(uci,node.board())) :
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
