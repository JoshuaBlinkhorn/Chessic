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

nodes = []
            
def parse_node(node) :
    if (not node.is_end()):
        if (node.board().turn == chess.WHITE):
            nodes.append(node)
            child = node.variation(0)
            parse_node(child)
        if (node.board().turn == chess.BLACK):
            for child in node.variations:
                parse_node(child)
            
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

            while (True):

                print(board.unicode(invert_color = True, empty_square = "."))
                if (board.turn == chess.WHITE):
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

    print("N New game")
    print("D Done")
    choice = input(":")

    while (choice != "D"):

        if (choice == "N"):
        
            board = repertoire.board()
            node = repertoire
        
            print(board.unicode(invert_color = True, empty_square = "."))
            
            while (not node.is_end()):
            
                if (board.turn == chess.WHITE):
                    
                    print("Your move")
                    move = chess.Move.from_uci(uci_from_user(board))
                    while (not (node.has_variation(move) and node.variation(move).is_main_variation())) :
                        move = chess.Move.from_uci(uci_from_user(board))
                        
                    node = node.variation(move)
                    board.push(move)
                        
                else :
                        
                    print("Selecting opponent's move")
                    num_vars = len(node.variations)
                    chosen_var = random.randint(0,num_vars - 1)
                    chosen_move = node.variations[chosen_var].move
                    node = node.variation(chosen_move)
                    board.push(chosen_move)

                print(board.unicode(invert_color = True, empty_square = "."))
                    
        print("N New game")
        print("D Done")
        choice = input(":")

def trainer():
    filename = input("filename:")        
    pgn = open(filename)
    repertoire = chess.pgn.read_game(pgn)
    pgn.close()

    print("Generating cards..")
    del nodes[:]
    parse_node(repertoire)
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

