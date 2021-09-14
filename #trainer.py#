import os
import chess
import chess.pgn
import random
import time
import pickle
import datetime
import time
import shutil
from colorama import Fore, Back, Style

NEW = 0
FIRST_STEP = 1
SECOND_STEP = 2
REVIEW = 3
INACTIVE = 4

class TrainingData :
    def __init__(self) :
        self.status = INACTIVE
        self.last_date = datetime.date.today()
        self.due_date = datetime.date.today()
        
class  MetaData:
    def __init__(self, name, player) :
        self.name = name
        self.player = player
        self.learning_data = [datetime.date.today(),0]
        self.learn_max = 10
        
########
# misc #
########

# permutation for flipping the board
board_flip = [63,62,61,60,59,58,57,56,55,54,53,52,51,50,49,48,47,46,45,44,43,42,41,40,39,38,37,36,35,34,33,32,31,30,29,28,27,26,25,24,23,22,21,20,19,18,17,16,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0]

# unicode values of pieces
white_pieces = ['\u2654','\u2655','\u2656','\u2657','\u2658','\u2659']
black_pieces = ['\u265a','\u265b','\u265c','\u265d','\u265e','\u265f']

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
    validity = False
    for move in board.legal_moves :
        if (string == move.uci()) :
            validity = True
            break
    return validity

############
# printing #
############

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
def print_board(board,player) :
    
    # convert python chess unicode board into array of 64 characters
    array = pack_string(board.unicode(invert_color = False, empty_square = " "))
    if (not player) :
        new_array = array.copy()
        for index in range(64) :
            new_array[index] = array[board_flip[index]]
        array = new_array

    board_string = ""
    for row in range(8) :
        for column in range(8) :
            index = (row * 8) + column
            # set piece colour
            if (array[index] in white_pieces) :
                piece_colour = Fore.WHITE
            else :
                piece_colour = Fore.BLACK

            # for uniform treatment of chess characters
            if (array[index] in black_pieces) :
                array[index] = white_pieces[black_pieces.index(array[index])]

            # set background colour
            case_1 = column % 2 == 1 and row % 2 == 1
            case_2 = column % 2 == 0 and row % 2 == 0
            if (case_1 or case_2) :
                square_colour = Back.CYAN
            else :
                square_colour = Back.GREEN

            # write square
            board_string += (square_colour + piece_colour + array[index] + ' ')
            
        board_string += (Style.RESET_ALL)
        if (row < 7) :
            board_string += '\n'

    print(board_string)

# places the python chess unicode string into 64-char array
def pack_string(string) :
    array = []
    for index in range(64) :
        array += string[index * 2]
    return array

    
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

def save_repertoire (variation_path, repertoire) :
    update(repertoire)
    with open(variation_path, "wb") as file :
        pickle.dump(repertoire,file)

def open_repertoire (variation_path) :
    with open(variation_path, "rb") as file :
        repertoire = pickle.load(file)
    update(repertoire)
    return repertoire

def update(repertoire) :
    learning_date = repertoire.meta.learning_data[0]
    learning_value = repertoire.meta.learning_data[1]
    max_value = repertoire.meta.learn_max
    today = datetime.date.today()
    # only normalise if today is a new day
    # normalise by the maximum value
    if (learning_date < today) :
        repertoire.meta.learning_data[0] = today
        repertoire.meta.learning_data[1] = 0
        normalise(repertoire,max_value)
    else :
        learning_threshold = max_value - learning_value
        normalise(repertoire,learning_threshold)

##############
# statistics #
##############

def get_scheduled_counts(node) :
    full_counts = get_counts(node)
    return [full_counts[0],full_counts[1]+full_counts[2],full_counts[5]]

def get_counts(node) :
    # new first second review inactive due reachable total
    counts = [0,0,0,0,0,0,0]
    if (node.training) :
        status = node.training.status
        due_date = node.training.due_date
        # first five counts' statuses are handled as integers
        for index in range(5) :
            if (status == index) :
                counts[index] += 1
        # due count
        if (status == REVIEW and due_date <= datetime.date.today()) :
            counts[5] += 1
        # increment reachable count
        counts[6] += 1

    # recursive part
    if (not node.is_end()) :
        if (node.player_to_move) :
            # search only the main variation
            child_counts = get_counts(node.variations[0])
            for index in range(7) :
                counts[index] += child_counts[index]
        else :
            # search all variations
            for child in node.variations :
                child_counts = get_counts(child)
                for index in range(7) :
                    counts[index] += child_counts[index]

    return counts

def get_total_count(node) :
    if (node.training) :
        count = 1
    else :
        count = 0
    if (not node.is_end()):
        for child in node.variations :
            count += get_total_count(child)                    
    return count
        
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
                repertoire = open_repertoire(repertoire_path)
                counts = get_counts(repertoire)
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
        for variation in os.listdir(opening_path) :
            variation_path = opening_path + "/" + variation
            repertoire = open_repertoire(variation_path)
            counts = get_counts(repertoire)
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
        info += str(waiting).ljust(9)
        info += str(learned).ljust(9)
        info += str(total).ljust(7)
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
        repertoire = open_repertoire(variation_path)
        counts = get_counts(repertoire)
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
        repertoire = open_repertoire(variation_path)
        counts = get_counts(repertoire)
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
    total = get_total_count(repertoire)
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
    save_repertoire(variation_path, repertoire)

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
    repertoire = open_repertoire(variation_path)
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
    #normalise(repertoire,)
    save_repertoire(variation_path, repertoire)    
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
        
def normalise(node,threshold) :
    # configure training data
    if (node.training) :
        if (threshold <= 0) :
            for status in [NEW,FIRST_STEP,SECOND_STEP] :
                if (node.training.status == status) :
                    node.training.status = INACTIVE
        else : # threshold exceeds 0
            if (node.training.status == INACTIVE) :
                node.training.status = NEW
            for status in [NEW,FIRST_STEP,SECOND_STEP] :
                if (node.training.status == status) :
                    threshold -= 1

    if (not node.is_end()) :
        if (node.player_to_move) : # call all children recursively
            threshold = normalise(node.variations[0],threshold)
        else : # call only the main variation
            for child in node.variations :
                threshold = normalise(child,threshold)
                
    return threshold

##############
# train menu #
##############

def train(variation_path):
    repertoire = open_repertoire(variation_path)
    player = repertoire.meta.player
    board = repertoire.board()
    node = repertoire        

    # generate queue
    queue = generate_training_queue(repertoire,board)
    # play queue

    command = ""
    while(len(queue) != 0) :
        card = queue.pop(0)
        counts = get_counts(repertoire)
        clear()
        print(f"{counts[0]} {counts[1]} {counts[2]} {counts[5]}")
        result = play_card(card,repertoire)
        if (result == "CLOSE") :
            break
        handle_card_result(result,card,queue,repertoire)

    # save and quit trainer
    save_repertoire(variation_path, repertoire)

def play_card(card,repertoire) :
    root = card[0]
    node = card[1]
    status = node.training.status
    player = repertoire.meta.player

    # front of card
    front = root.variations[0]
    if (status == 0) :
        print("\nNEW : this is a position you haven't seen before\n")
    if (status == 1 or status == 2) :
        print("\nLEARNING : this is a position you're currently learning\n")
    if (status == 3) :
        print("\nRECALL : this is a position you've learned, due for recall\n")

    print_board(front.board(),player)
    if (status == 0) :
        print("\nGuess the move..")
    else :
        print("\nRecall the move..")
    print(".. then hit [enter] or 'c' to close")
    uci = input("\n:")
    if (uci == "c") :
        return "CLOSE"

    # back of card
    back = front.variations[0]
    clear()    
    print("Solution:")
    print_board(back.board(),player)

    if (status == 0) :
        print("\nHit [enter] to continue.")
        input("\n\n:")
    if (status != 0) :
        print("\n'h' hard    [enter] ok    'e' easy\n")
        uci = input("\n:")
   
    while (True) :
        if (uci == "e") :
            return "EASY"
        if (uci == "h") :
            return "HARD"
        if (uci == "") :
            return "OK"
        if (uci == "c") :
            return "CLOSE"
        uci = input(":")
        
        
def handle_card_result(result,card,queue,repertoire) :
    root = card[0]
    node = card[1]
    status = node.training.status
    
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    
    if (status == NEW) :
        print("Here")
        node.training.status = FIRST_STEP
        increase = int(round(3 * random.random()))
        offset = min(1 + increase,len(queue))
        queue.insert(offset,card)
                    
    elif (status == FIRST_STEP) :
        if (result == "EASY") :
            node.training.status = REVIEW
            node.training.last_date = today
            node.training.due_date = tomorrow
            repertoire.meta.learning_data[1] += 1
        elif (result == "OK") :
            node.training.status = SECOND_STEP
            increase = int(round(3 * random.random()))
            offset = min(6 + increase,len(queue))
            queue.insert(offset,card)
        elif (result == "HARD") :
            node.training.status = FIRST_STEP            
            increase = int(round(3 * random.random()))
            offset = min(1 + increase,len(queue))
            queue.insert(offset,card)

    elif (status == SECOND_STEP) :
        if (result == "EASY") :
            node.training.status = REVIEW
            node.training.last_date = today
            node.training.due_date = today + datetime.timedelta(days=3)
            repertoire.meta.learning_data[1] += 1
        elif (result == "OK") :
            node.training.status = REVIEW
            node.training.last_date = today
            node.training.due_date = tomorrow
            repertoire.meta.learning_data[1] += 1
        elif (result == "HARD") :
            node.training.status = FIRST_STEP            
            increase = int(round(3 * random.random()))
            offset = min(1 + increase,len(queue))
            queue.insert(offset,card)
            
    elif (status == REVIEW) :
        previous_gap = (node.training.due_date - node.training.last_date).days

        if (result == "HARD") :
            node.training.status = FIRST_STEP
            offset = min(2,len(queue))
            queue.insert(offset,card)
            repertoire.meta.learning_data[1] -= 1

        else :
            if (result == "EASY") :
                multiplier = 3 + random.random()
            else :
                multiplier = 2 + random.random()
            new_gap = int(round(previous_gap * multiplier))
            node.training.status = REVIEW
            node.training.last_date = today
            node.training.due_date = today + datetime.timedelta(days=new_gap)

def generate_training_queue(node,board) :
    # the board must be returned as it was given
    queue = []    
    
    if (node.training) :
        status = node.training.status
        due_date = node.training.due_date
        today = datetime.date.today()
        if (status == 0 or status == 1 or status == 2 or (status == 3 and due_date <= today)) :
                # add a card to the queue
            solution = board.pop()
            problem = board.pop()
            game = chess.pgn.Game()
            game.setup(board)
            new_node = game.add_variation(problem)
            new_node = new_node.add_variation(solution)
            board.push(problem)
            board.push(solution)
            queue.append([game,node])

    # recursive part
    if (not node.is_end()) :
        if (node.player_to_move) :
            # search only the main variation
            child = node.variations[0]
            board.push(child.move)
            queue += generate_training_queue(child,board)
            board.pop()

        else :
            # search all variations
            for child in node.variations :
                board.push(child.move)
                queue += generate_training_queue(child,board)
                board.pop()

    return queue

    
############### 
# entry point #
###############

main_menu()

