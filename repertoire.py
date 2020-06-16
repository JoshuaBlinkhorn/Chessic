import chess
import chess.pgn
import random
import time

########
# misc #
########

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
def open_repertoire(file_path) :
    pgn = open(file_path)
    repertoire = chess.pgn.read_game(pgn)
    pgn.close()
    return repertoire

# returns the user's colour for a repertoire
def get_player(repertoire) :
    return (repertoire.headers["Site"] == "W")
                
#########
# new() #
#########

# creates a new repertoire
def new() :
    # navigate to starting position
    result = get_starting_position()
    if (result == "QUIT") :
        return    
    board = result
    clear()
    print_board(board)
    # obtain colour
    
    colour = input("\nYou play as:\n'W' for White\n'B' for  Black\n:")
    while (colour != "B" and colour != "W"):
        if (colour = "Q") :
            return        
        colour = input(":")
        
    # create pgn
    repertoire = chess.pgn.Game()
    repertoire.setup(board)
    repertoire.headers["Event"] = colour
    file_path = input("filename:")
    try:
        print(repertoire, file = open(file_path,"w"), end = "\n\n")
    except:
        print("Error writing file.")
        return

    return file_path

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

# user management of repertoire as a pgn
def manage(file_path):

    repertoire = open_repertoire(file_path)
    
    node = repertoire
    board = node.board()
    player = board.turn

    result = query_node(node)
    
    while (result != "SAVE") :
        if (result == "BACK") :
            if (node != repertoire) :
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

    # save
    print("Saving repertoire `" + str(file_path) + "'.")
    print(repertoire, file = open(file_path,"w"), end = "\n\n")

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
    player = board.turn

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
                if (uci == "F") :
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
    queue = get_training_nodes(node,get_payer(repertoire))
    if (lend(queue) == 0) :
        print("No training positions generated.")
        return
    random.shuffle(queue)

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
        if (uci == "F") :
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

def main():
    clear()
    print("N New repertoire")
    print("L Load repertoire")
    print("M Manage")
    print("P Play")
    print("T Train")
    print("Q Quit")
    choice = input("\n:")

    file_is_open = False

    while(choice != "Q"):

        if (choice == "N"):
            file_path = new()
            file_is_open = True
            choice = "M"
            
        elif (choice == "L"):
            file_path = load()
            file_is_open = True
        
        elif (choice == "M"):
            if (file_is_open == False):
                open_file_msg()
                choice = input(":")
                continue
            else :
                manage(file_path)

        elif (choice == "P"):
            if (file_is_open == False):
                open_file_msg()
                choice = input(":")
                continue
            else :
                play(file_path)
            
        elif (choice == "T"):
            if (file_is_open == False):
                open_file_msg()
                choice = input(":")
                continue
            else :
                train(file_path)

        print("\nC Create repertoire")
        print("L Load repertoire")
        print("M Manage")
        print("P Play")
        print("T Train")
        print("Q Quit")
        choice = input("\n:")

def open_file_msg() :
    print("Please create or load a repertoire first.")
            
############### 
# entry point #
###############

main()

# REDUNDANT

def weigh_node(node, player) :
    size = 0
    if (not node.is_end()):
        if (node.board().turn == player):
            child = node.variation(0)
            size += weigh_node(child, player)
        else :
            for child in node.variations:
                size += weigh_node(child, player)
    return size + 1 
    
def node_info(node,player) :
    board = node.board()
    print_board(board)
    if (board.turn == player) :
        print("Your moves:")
    else :
        print("Opponents moves:")
    for var in node.variations :
        print(var.move.uci())
    if (board.turn == player) :
        print ("D to Delete, P to Promote, [Enter] to Go Back")
    else :
        print ("D to Delete, [Enter] to Go Back")

def print_moves(node) :
    if (len(node.variations) == 0) :
        print("End of line.")
    else :
        print("Your moves:")
        for var in node.variations :
            print(var.move.uci())

def trainer(position,repetitions):

    print("Generating cards..")

    nodes = parse_node(rep,rep.board().turn)
    size = len(nodes)

    if (size == 0):
        print("This repertoire has no card nodes.")

    else :

        print("Generated " + str(size) + " cards.")
        
        while(True):
            pos = random.randint(0,size-1)
            chosen_node = nodes[pos]
            print(chosen_node.board().unicode(invert_color = True, empty_square = "."))
            
            print("Your move or [Return] to Quit")
            uci = uci_from_user(chosen_node.board())
            if (uci == ""):
                return
            move = chess.Move.from_uci(uci)

            while (not (chosen_node.has_variation(move) and chosen_node.variation(move).is_main_variation())) :
                uci = uci_from_user(chosen_node.board())
                if (uci == ""):
                    return
                move = chess.Move.from_uci(uci)
                
            print(chosen_node.variation(move).board().unicode(invert_color = True, empty_square = "."))
            print("Correct")                

def print_position(position) :
    print_board(position.board())
    if (position.is_end()) :
        print("No candidates.")
    else :
        print("Candidate moves:")
        for candidate in position.variations :
            print(candidate.move.uci())

            
def query_position(position) :    
    print_position(position)
    uci = input(":")
    if (uci == "B") :
        return "BACK"
    if (uci == "D") :
        return "DELETE"
    if (uci == "P") :
        return "PROMOTE"
    if (uci == "") :
        return "SAVE"
    if (is_valid(uci,position.board())) :
        return uci
    return "INVALID"
    
def print_candidate(candidate) :
    print_board(candidate.board())
    if (candidate.is_end()) :
        print("No responses.")
    else :
        print("Responses:")
        for response in candidate.variations :
            print(response.move.uci())
            
def query_candidate(candidate) :    
    print_candidate(candidate)
    uci = input(":")
    if (uci == "B") :
        return "BACK"
    if (uci == "D") :
        return "DELETE"
    if (uci == "") :
        return "SAVE"
    if (is_valid(uci,candidate.board())) :
        return uci
    return "INVALID"
            
def parse_node(node, player) :
    nodes = []
    if (not node.is_end()):
        if (node.board().turn == player):
            child = node.variation(0)
            nodes += [node]
            nodes += parse_node(child,player)
        else :
            for child in node.variations :
                nodes += parse_node(child,player)
    return nodes

def format_node(position) :

    print("formatting position")
    if (not position.is_end()) :
        for candidate in position.variations :
            if (candidate.is_end()) :                
                candidate.parent.remove_variation(candidate.move)
                print("removing candidate leaf.")
            else :
                for pos in candidate.variations :
                    format_node(pos)
