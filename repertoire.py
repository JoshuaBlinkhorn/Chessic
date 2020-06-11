import chess
import chess.pgn
import random

def uci_from_user(board) :
    while(True):
        uci = input("move:")
        if (uci == ""):
            return uci
        for move in board.legal_moves :
            if (uci == move.uci()) :
                return uci


def parse_node(node,player) :
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

def weigh_node(node) :
    size = 0
    if (not node.is_end()):
        if (node.board().turn == chess.WHITE):
            child = node.variation(0)
            size += weigh_node(child)
        if (node.board().turn == chess.BLACK):
            for child in node.variations:
                size += weigh_node(child)
    return size + 1 
    

def composer():
    print("N New")
    print("S Saved")
    print("B Back")

    choice = input(":")        
    
    while(choice != "B"):

        if (choice == "N"):
            
            print("Navigate to starting position.")
            board = chess.Board()
            print(board.unicode(invert_color = True, empty_square = "."))            
            print("M add move")
            print("D done")
            choice = input(":")

            while(choice != "D"):

                if (choice == "M"):
                    uci = uci_from_user(board)                                
                    board.push(chess.Move.from_uci(uci))
                    print(board.unicode(invert_color = True, empty_square = "."))

                print("M add move")
                print("D done")
                choice = input(":")
                    
                
                
            #game = chess.pgn.Game.from_board(board)
            game = chess.pgn.Game()
            game.setup(board)
            filename = input("filename:")
            print(game, file = open(filename,"w"), end = "\n\n")

        if (choice == "S"):
            filename = input("filename:")
            pgn = open(filename)
            repertoire = chess.pgn.read_game(pgn)
            pgn.close()

            board = repertoire.board()
            node = repertoire
            player = board.turn
            
            while (True):

                print(board.unicode(invert_color = True, empty_square = "."))
                if (board.turn == player):
                    print("Your move(s):")
                else :
                    print("Your opponents move(s):")
                for var in node.variations :
                    print(var.move.uci())
                
                print("M enter move")
                print("B go back")

                choice = input(":")
                
                if (choice == "M"):
                    uci = uci_from_user(board)                                
                    move = chess.Move.from_uci(uci)
                    if (not node.has_variation(move)) :
                        node.add_variation(move)
                    node = node.variation(move)
                    board.push(move)
                        
                if (choice == "B"):
                    if (node == repertoire):
                        break;
                    else :
                        node = node.parent
                        board.pop()

            print(repertoire, file = open(filename,"w"), end = "\n\n")
            
        print("N New")
        print("S Saved")
        print("B Back")

        choice = input(":")

def player():

    filename = input("filename:")        
    pgn = open(filename)
    repertoire = chess.pgn.read_game(pgn)
    pgn.close()

    if(len(repertoire.variations) == 0):
        print("Repertoire is empty.")
        return
    

    node = repertoire
    board = node.board()
    player = node.board().turn
    
    print(board.unicode(invert_color = True, empty_square = "."))

    while (True):
        
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
                
            current_weight = 0
            index = 0
                
            current_weight += weigh_node(node.variation(index))                        
            while(current_weight < target_weight) :
                index += 1
                current_weight += weigh_node(node.variation(index))                        
                
            node = node.variation(index)
            board.push(node.move)
                
            print(board.unicode(invert_color = True, empty_square = "."))

        if (node.is_end()):
            print("End of Line")
            print("New Game")
            node = repertoire
            board = node.board()
            print(board.unicode(invert_color = True, empty_square = "."))
            
def trainer():
    filename = input("filename:")        
    pgn = open(filename)
    repertoire = chess.pgn.read_game(pgn)
    pgn.close()

    print("Generating cards..")

    nodes = parse_node(repertoire,repertoire.board().turn)
    size = len(nodes)

    if (size == 0):
        print("This repertiore has no card nodes.")

    else :
        
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

    print("1 Composer")
    print("2 Player")
    print("3 Trainer")
    print("Q Quit")
    choice = input(":")
    
    while(choice != "Q"):

        if (choice == "1"):
            composer()
        if (choice == "2"):
            player()
        if (choice == "3"):
            trainer()

        print("1 Composer")
        print("2 Player")
        print("3 Trainer")
        print("Q Quit")
        choice = input(":")
            
main()

