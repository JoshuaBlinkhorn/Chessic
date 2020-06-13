import chess
import chess.pgn
import random
import time

def print_board(board) :
    print(board.unicode(invert_color = True, empty_square = "."))

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
    
def new_repertoire() :

    choice = ""
    board = chess.Board()
    uci = "string"

    print("Choose starting position.")
    print(board.unicode(invert_color = True, empty_square = "."))            
    if (board.turn):
        print("You play as WHITE")
    else:
        print("You play as BLACK")
    print("Type move or [Enter] to choose")

    uci = input(":")
    while(uci != ""):
        
        if (uci == "B"):
            # TODO : check board is poppable
            board.pop()

            print("Choose starting position.")
            print(board.unicode(invert_color = True, empty_square = "."))            
            if (board.turn):
                print("You play as WHITE")
            else:
                print("You play as BLACK")
            print("Type move or [Enter] to choose or B to go Back")
            # TODO : if board is starting position delete the b option
            
        elif (is_valid(uci,board)):
            board.push(chess.Move.from_uci(uci))
                
            print("Choose starting position.")
            print(board.unicode(invert_color = True, empty_square = "."))            
            if (board.turn):
                print("You play as WHITE")
            else:
                print("You play as BLACK")
            print("Type move or [Enter] to choose or B to go Back")
            # TODO : if board is starting position delete the b option

        uci = input(":")
    rep = chess.pgn.Game()
    rep.setup(board)
    file_path = input("filename:")
    print(rep, file = open(file_path,"w"), end = "\n\n")

    return [rep, file_path]
    
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


def parse_node(node, player) :
    nodes = []
    if (not node.is_end()):
        if (node.board().turn == player):
            child = node.variation(0)
            nodes += [node]
            nodes += parse_node(child,player)
        else :
            for child in node.variations:
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
        
def composer(repertoire):

    rep = repertoire[0]
    file_path = repertoire[1]
    
    node = rep
    board = node.board()
    player = board.turn
    
    node_info(node,player)
    uci = input("move:")
    
    while (True) :

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
                
    print("Saving repertoire `" + str(file_path) + "'.")
    print(rep, file = open(file_path,"w"), end = "\n\n")

def get_end_nodes(node,player) :
    
    rep = node
    nodes = []

    if (node.is_end()) :
        if (node.board().turn == player) :
            node = node.parent()
        if (node != node.game()) :
            nodes.append(node)

    else :
        for child in node.variations:
            nodes += get_end_nodes(child,player)

    return nodes
    
def play_end_node(card,size) :

    node = card[0]
    index = card[1] 
    
    success = True
    
    # make main line
    while (node != node.game()) :
        move = node.move
        node = node.parent
        node.promote_to_main(move)

    board = node.board()
    player = board.turn

    print("\n--------")    
    print("NEW GAME: line " + str(index) + " / " + str(size))
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
            
def player(repertoire):

    rep = repertoire[0]
    player = rep.board().turn
    queue = []

    # put all nodes in a list
    end_nodes = get_end_nodes(rep,player)
    size = len(end_nodes)
    if (size == 0) :
        print("No lines in repertoire")
        return

    while (True) :
        # create queue
        for index in range(size) :
            queue.append([end_nodes[index],index,1])
        random.shuffle(queue)
    
        card = queue.pop(0)
        node = card[0]
        index = card[1]
        weight = card[2]


        result = play_end_node(card,size)
        if (result == "") :
            return
        if (result == "SUCCESS") :
            weight += 1
        else :
            weight = 1
        offset = 2**weight
        if (offset < size - 1) :
            queue.insert(offset, [node,index,weight])
        else :
            queue.append([node,index,weight])
    
"""

    # let fly with game
    
    # find all end nodes and order randomly ina queue
    
    if(len(rep.variations) == 0):
        print("Repertoire is empty.")
        return
    
    node = rep
    board = node.board()
    player = node.board().turn
    
    print(board.unicode(invert_color = True, empty_square = "."))

    while (True):
        print("board.turn:" + str(board.turn) + " node.board().turn: " +  str(node.board().turn) + " player: " + str(player))
        if (board.turn == player):
            
            print("Your move or [Return] to Quit")
            uci = uci_from_user(board)
            if (uci == ""):
                return
            move = chess.Move.from_uci(uci)
            
            while (not (node.has_variation(move) and node.variation(move).is_main_variation())) :
                uci = uci_from_user(board)
                if (uci == ""):
                    return
                move = chess.Move.from_uci(uci)
                
            node = node.variation(move)
            board.push(move)
                
        else :

            total_weight = weigh_node(node, player) - 1
            target_weight = random.randint(0,total_weight - 1)
            current_weight = 0
            index = 0
                
            current_weight += weigh_node(node.variation(index),player)
            #print("weight of node.variation(" + str(index) + "): " + str(weigh_node(node.variation(index), player)))
            #print("total_weight:" + str(total_weight) +" current_weight:" + str(current_weight) + " target_weight:" + str(target_weight) + " index:" + str(index))
            
            while(current_weight < target_weight) :
                index += 1
                current_weight += weigh_node(node.variation(index), player)                        
                #print("total_weight:" + str(total_weight) +" current_weight:" + str(current_weight) + " target_weight:" + str(target_weight) + "index:" + str(index))
                
            node = node.variation(index)
            board.push(node.move)
                
            print(board.unicode(invert_color = True, empty_square = "."))

        if (node.is_end()):
            print("End of Line")
            print("New Game")
            node = rep
            board = node.board()
            print(board.unicode(invert_color = True, empty_square = "."))

"""
            
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
            composer(rep)
            
        if (choice == "P"):
            if (rep == "NULL"):
                choice = input(":")
                continue
            player(rep)
            
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

