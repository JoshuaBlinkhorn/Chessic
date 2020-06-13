import chess
import chess.pgn
import random
import time

# TODO - functions print_node and query_node where the test of node type is done within

def print_board(board) :
    print(board.unicode(invert_color = True, empty_square = "."))

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

def is_valid(uci,board) :

    validity = False
    
    for move in board.legal_moves :
        if (uci == move.uci()) :
            validity = True
            break

    return validity

def navigate_to_position(root) :

    position = root
    result = query_position(position)

    print("Navigate to position.")
    
    while (result != "SAVE") :
        if (result == "B") :
            if (position != root) :
                position = position.parent.parent
            result = query_position(position)
            
        elif (result == "INVALID") :
            result = query_position(position)
            
        else :
            move = chess.Move.from_uci(result)
            position = position.variation(move)
            position = position.variation(0)
            result = query_position(position)
    return position

def uci_from_user(board) :
    while(True):
        uci = input("move:")
        if (uci == ""):
            return uci
        for move in board.legal_moves :
            if (uci == move.uci()) :
                return uci

def open_repertoire(file_path) :
    pgn = open(file_path)
    repertoire = chess.pgn.read_game(pgn)
    pgn.close()
    return repertoire
            
def load() :
    file_path = input("filename:")
    try:
        pgn = open(file_path, "r")
    except:
        print("File error.")
        return
    repertoire = chess.pgn.read_game(pgn)
    pgn.close()
    print("Loaded repertoire `" + str(file_path) + "'.")
    return file_path

# TODO: improve this function - the navigation could be delegated
def new_repertoire() :
    
    choice = ""
    board = chess.Board()
    uci = "string"

    print("Choose starting position.")
    print(board.unicode(invert_color = True, empty_square = "."))            
    if (board.turn):
        print("You play as BLACK")
    else:
        print("You play as WHITE")
    print("Type move or [Enter] to choose")

    uci = input(":")
    while(uci != ""):
        
        if (uci == "B"):
            # TODO : check board is poppable
            board.pop()

            print("Choose starting position.")
            print(board.unicode(invert_color = True, empty_square = "."))            
            if (board.turn):
                print("You play as BLACK")
            else:
                print("You play as WHITE")
            print("Type move or [Enter] to choose or B to go Back")
            # TODO : if board is starting position delete the b option
            
        elif (is_valid(uci,board)):
            board.push(chess.Move.from_uci(uci))
                
            print("Choose starting position.")
            print(board.unicode(invert_color = True, empty_square = "."))            
            if (board.turn):
                print("You play as BLACK")
            else:
                print("You play as WHITE")
            print("Type move or [Enter] to choose or B to go Back")
            # TODO : if board is starting position delete the b option

        uci = input(":")
    rep = chess.pgn.Game()
    rep.setup(board)
    file_path = input("filename:")
    try:
        print(rep, file = open(file_path,"w"), end = "\n\n")
    except:
        print("Error writing file.")
        return
        
    return file_path

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

def get_end_nodes(node) :

    format_node(node) # removes candidate leaves    
    nodes = []

    if (node.is_end()) :
        nodes.append(node)
    else :
        for child in node.variations :
            nodes += get_end_nodes(child.variation(0))

    return nodes
    

def get_training_nodes(node) :

    nodes = []

    if (not node.is_end()) :
        for child in node.variations :
            nodes += [child,]
            nodes += get_training_nodes(child.variation(0))

    return nodes

def manage(file_path):

    root = open_repertoire(file_path)
    
    node = root
    board = node.board()
    player = board.turn

    result = query_position(node)
    
    while (result != "SAVE") :
        if (result == "BACK") :
            if (node != root) :
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

        if (node.board().turn == player) :
            result = query_position(node)
        else :
            result = query_candidate(node)

    # save
    print("Saving repertoire `" + str(file_path) + "'.")
    print(root, file = open(file_path,"w"), end = "\n\n")
        
def play_end_node(card,root,deck_size,queue_length) :

    node = card[0]
    index = card[1] 
    
    success = True
    
    # make main line
    while (node != root) :
        move = node.move
        node = node.parent
        node.promote_to_main(move)

    board = node.board()
    player = board.turn

    print("\n--------")    
    print("NEW GAME: line " + str(index) + " / " + str(deck_size) + " " + str(queue_length) + " / " + str(deck_size))
    print("--------\n")        
    print_board(board)

    time.sleep(2)

    print("\nMaking move..")
    node = node.variation(0)
    board = node.board()
    print("")
    print_board(board)
    uci = input("\n\n:")
    
    while (not node.is_end()) :
        
        if (uci == "") :
            return "QUIT"
    
        if (is_valid(uci,board)) :
            move = chess.Move.from_uci(uci)
            if (node.has_variation(move) and node.variation(move).is_main_variation()) :
                node = node.variation(move)
                board = node.board()
                if (node.is_end()):
                    break
                time.sleep(1)
                print("")
                print_board(board)
                print("\nCORRECT! Making move..", end="")
                time.sleep(2)

                node = node.variation(0)
                board = node.board()
                print("")
                print_board(board)
                uci = input("\n\n:")
                            
            else :
                time.sleep(1)
                print("\nINCORRECT! Correct was '" + str(move.uci()) + "'.\n")
                node = node.variation(0)
                move = node.move
                print_board(node.board())
                input("\n\n[Enter] to Continue\n")                
                return "FAILURE"

        else :
            uci = input("\n\n:")
            print("")

    print("\n-------------")
    print("GAME COMPLETE - WELL DONE!")
    print("-------------\n")
    time.sleep(2)
    return "SUCCESS"
            
def play(file_path) :

    root = open_repertoire(file_path)
    
    # Navigate to position
    position = navigate_to_position(root)
    
    # get repetitions
    repetitions = input("repetitions: ")

    # call player
    play_session(position,repetitions)
    
def play_session(position,repetitions):

    # put all nodes in a list
    format_node(position)
    end_nodes = get_end_nodes(position)
    deck_size = len(end_nodes)

    # create queue
    queue = []
    for index in range(deck_size) :
        queue.append([end_nodes[index],index,0])
    random.shuffle(queue)
    
    while(len(queue) != 0) :
    
        card = queue.pop(0)
        node = card[0]
        index = card[1]
        iterations = card[2]

        result = play_end_node(card,position,deck_size,len(queue))
        if (result == "QUIT") :
            return
        if (result == "SUCCESS") :
            if (iterations == repetitions) :
                continue
            else :
                iterations +=1
                offset = min(2 ** (iterations + 1), len(queue) - 1)
                queue.insert(offset, [node,index,weight])
    
def train(file_path) :

    root = open_repertoire(file_path)
    
    # Navigate to position
    position = navigate_to_position(root)
    
    # get repetitions
    repetitions = input("repetitions: ")

    # call trainer
    train_session(position,repetitions)

def play_training_card(card,deck_size,queue_length) :    

    candidate = card[0]
    print_board(candidate.board())
    print("Your move or [Return] to Quit")

    uci = input(":")
    while (uci != "") :
        if (is_valid(uci,candidate.board())) :
            move = chess.Move.from_uci(uci)
            if (candidate.has_variation(move) and candidate.variation(move).is_main_variation()) :
                print("Correct")
                return("Success")
            else :
                node = candidate.variation(0)
                print("Incorrect: correct was " + node.move.uci())
                print_board(node.board())
                return("Failure")
        uci = input(":")
    return "QUIT"
        
def train_session(position,repetitions):

    # put all nodes in a list
    format_node(position)
    training_nodes = get_training_nodes(position)
    deck_size = len(training_nodes)

    # create queue
    queue = []
    for index in range(deck_size) :
        queue.append([training_nodes[index],index,0])
    random.shuffle(queue)
    
    while(len(queue) != 0) :
    
        card = queue.pop(0)
        node = card[0]
        index = card[1]
        iterations = card[2]

        result = play_training_card(card,deck_size,len(queue))
        if (result == "QUIT") :
            return
        if (result == "SUCCESS") :
            if (iterations == repetitions) :
                continue
            else :
                iterations +=1
                offset = min(2 ** (iterations + 1), len(queue) - 1)
                queue.insert(offset, [node,index,weight])

                
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

        
def open_file_msg() :
    print("Please create or load a repertoire first.")
            
def main():

    print("C Create repertoire")
    print("L Load repertoire")
    print("M Manage")
    print("P Play")
    print("T Train")
    print("Q Quit")
    choice = input(":")

    file_is_open = False

    while(choice != "Q"):

        if (choice == "C"):
            file_path = new_repertoire()
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

        print("C Create repertoire")
        print("L Load repertoire")
        print("M Manage")
        print("P Play")
        print("T Train")
        print("Q Quit")
        choice = input(":")
        
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

