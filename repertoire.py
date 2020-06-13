import chess
import chess.pgn
import random
import time

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
    
def uci_from_user(board) :
    while(True):
        uci = input("move:")
        if (uci == ""):
            return uci
        for move in board.legal_moves :
            if (uci == move.uci()) :
                return uci


def load_repertoire() :
    
    # check whether file exists

    # check that it's a repertoire

    # return it (perhaps return it as a chess.pgn.Game? probably all calling functions will use it this way)

    # STUB CODE ONLY: this function still needs to be written
    
    file_path = input("filename:")
    pgn = open(file_path)
    repertoire = chess.pgn.read_game(pgn)
    pgn.close()
    
    print("Loaded repertoire `" + str(file_path) + "'.")
    return [repertoire,file_path]

def create_dialogue() :

    # Navigate to position
    board = chess.Board()
    position = navigate_to_position()
    
    # get repetitions
    repetitions = input("repetitions: ")

    # call player
    player(position,repetitions)


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
    print(rep, file = open(file_path,"w"), end = "\n\n")

    return [rep, file_path]
    


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
    
    nodes = []

    if (node.is_end()) :
        nodes.append(node)
    else :
        for child in node.variations :
            nodes += get_end_nodes(child.variation(0))

    return nodes
    
        
def manage(repertoire):

    root = repertoire[0]
    file_path = repertoire[1]
    
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
    format_node(root)
        
    print("Saving repertoire `" + str(file_path) + "'.")
    print(root, file = open(file_path,"w"), end = "\n\n")

        
"""        

        if (uci == "") :
            if (node == rep) :
                break
            else :
                node = node.parent
                board = node.board()                        

        elif (uci == "D") :
            uci = input("delete move:")
            if (is_valid(uci,board)) :
                move = chess.Move.from_uci(uci)
                if (node.has_variation(move)) :
                    node.remove_variation(move)

        elif (uci == "P") :
            uci = input("promote move:")
            if (is_valid(uci,board)) :
                move = chess.Move.from_uci(uci)
                if (node.has_variation(move)) :
                    node.promote_to_main(move)
                                
        elif (is_valid(uci,board)) :
            move = chess.Move.from_uci(uci)
            if (not node.has_variation(move)) :
                node.add_main_variation(move)
            node = node.variation(move)
            board = node.board()                        

        node_info(node,player)
        uci = input("move:")


"""

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
    time.sleep(2)
    
    print_board(board)
    uci = input("\n\n:")

    while (True) :
        
        if (uci == "") :
            return ""
    
        if (is_valid(uci,board)) :
            move = chess.Move.from_uci(uci)
            if (node.has_variation(move) and node.variation(move).is_main_variation()) :
                node = node.variation(move)
                board = node.board()
                if (node.is_end() or node.variation(0).is_end()) :
                    print("\n-------------")
                    print("GAME COMPLETE - WELL DONE!")
                    print("-------------\n")
                    time.sleep(2)
                    return "SUCCESS"
                else :
                    time.sleep(1)
                    print("")
                    print_board(board)
                    print("\nCORRECT! Making move..")
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

def print_moves(node) :
    if (len(node.variations) == 0) :
        print("End of line.")
    else :
        print("Your moves:")
        for var in node.variations :
            print(var.move.uci())

def navigate_to_position(rep) :

    position = rep
    result = query_position(position)

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
            
def player_dialogue(rep) :

    # Navigate to position
    position = navigate_to_position(rep)
    
    # get repetitions
    repetitions = input("repetitions: ")

    # call player
    player(position,repetitions)
    
"""
    
    # setup
    node = rep[0]
    board = node.board()

    # corner case
    if (node == node.game()) :
        print("Repertoire is empty.")
        return "NULL"

    # get starting position
    print("Navigate to starting position.")
    print_board(node.board())
    print_moves(node)
    print("type move or [Enter] to Go Back or 'S' to select starting position")
    uci = input("\n:")

    # navigate
    while (True) :

        if (uci != "S") :
            # return
            repetitions = input("repetitions:")
            player(node,repetitions)

        if (uci == "") :
            # go back
            if (node == node.game()) :
                return ""
            else :
                node = node.parent.parent
                print("type move or [Enter] to Go Back or 'S' to select starting position")
            uci = input("\n:")

        if (is_valid(uci,board)) :
            # check move and apply
            move = chess.Move.from_uci(uci)
            if (node.has_variation(move)) :
                node = node.variation(move)
                node = node.variation(0)
                board = node.board()
                print_board(board)                
                print("type move or [Enter] to Go Back or 'S' to select starting position")
            uci = input("\n:")
"""                
            
def player(node,repetitions):

    # put all nodes in a list
    end_nodes = get_end_nodes(node)
    size = len(end_nodes)

    # create queue
    queue = []
    for index in range(size) :
        queue.append([end_nodes[index],index,0])
    random.shuffle(queue)
    
    while(len(end_nodes) != 0) :
    
        card = queue.pop(0)
        node = card[0]
        index = card[1]
        iterations = card[2]

        result = play_end_node(card,node,deck_size,len(end_nodes))
        if (result == "") :
            return
        if (result == "SUCCESS") :
            if (iterations == repetitions) :
                continue
            else :
                iterations +=1
                offset = min(2 ** (iterations + 1), size - 1)
                queue.insert(offset, [node,index,weight])
    

def trainer(repertoire):

    rep = repertoire[0]
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

        
                
            
def main():

    print("C Create repertoire")
    print("L Load repertoire")
    print("M Manage")
    print("P Play")
    print("T Train")
    print("Q Quit")
    choice = input(":")

    rep = "NULL"

    while(choice != "Q"):

        if (choice == "C"):
            rep = new_repertoire()
            choice = "M"
            
        if (choice == "L"):
            rep = load_repertoire()

        
        if (choice == "M"):
            if (rep == "NULL"):
                choice = input(":")
                continue
            manage(rep)
            
        if (choice == "P"):
            if (rep == "NULL"):
                print("Create or Load repertoire first")
                choice = input(":")
                continue
            player_dialogue(rep)
            
        if (choice == "T"):
            if (rep == "NULL"):
                choice = input(":")
                continue
            trainer(rep)


        print("C Create repertoire")
        print("L Load repertoire")
        print("M Manage")
        print("P Play")
        print("T Train")
        print("Q Quit")
        choice = input(":")
        
main()

