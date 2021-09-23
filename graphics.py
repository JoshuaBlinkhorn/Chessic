# MODULE graphics.py
# this file is part of Opening Trainer by Joshua Blinkhorn

# SYNOPSIS 
# This module implements a basic graphical chess board.
# Typically only the functions clear() and print_board()
# will be imported.

# module imports
from colorama import Fore, Back, Style # handles coloured printing

# unicode values of chess pieces
white_pieces = ['\u2654','\u2655','\u2656',
                '\u2657','\u2658','\u2659']
black_pieces = ['\u265a','\u265b','\u265c',
                '\u265d','\u265e','\u265f']

# clear()
# `clears' the terminal screen
def clear() :
    height = 40
    for x in range(height) :
        print("")

# print_board()        
# Pretty prints the board given as a unicode string from
# the python chess module.
# Argument 'player' is a Boolean value; if 'true' ('false'), the
# board is printed from white's (black's) perspective.
# .unicode is a python chess method that returns a unicode
# string representation of the board
def print_board(board,player) :        
    board_string = board.unicode(invert_color = False,
                                 empty_square = " ")
    board_string = remove_spaces(board_string)
    if (player == False) :
        board_string = flip(board_string)

    print_string = ""
    board_height = 8
    for row in range(board_height) :
        print_string += row_string(row, board_string)
    print(print_string)    

# board_whitespace()    
# Removes whitespace in the chess board string.
# Python chess inserts whitespace as pretty print formatting.
# This function removes it by deleting every second character.
def remove_spaces(board_string) :
    new_string = []
    for index in range(64) :
        new_string += board_string[index * 2]
    return new_string

# flip()
# Flips the board.
# Accomplished by reversing the order of the string's 64 characters.
def flip(board_string) :
    flip_permutation = [63,62,61,60,59,58,57,56,
                        55,54,53,52,51,50,49,48,
                        47,46,45,44,43,42,41,40,
                        39,38,37,36,35,34,33,32,
                        31,30,29,28,27,26,25,24,
                        23,22,21,20,19,18,17,16,
                        15,14,13,12,11,10,9,8,7,
                        6,5,4,3,2,1,0]
    new_string = board_string.copy()
    for index in range(64) :
        new_string[index] = board_string[flip_permutation[index]]
    return new_string    

# row_string()
# Produces the coloured string for the given row of the board.
def row_string(row, board_string) :
    board_width = 8
    print_string = "    "
    for column in range(board_width) :
        char_index = (row * board_width) + column
        char = board_string[char_index]
        piece_colour = get_piece_colour(char)        
        piece_char = get_piece_char(char)
        square_colour = get_square_colour(column, row)
        print_string += (square_colour + piece_colour +
                         piece_char + ' ')            
    print_string += (Style.RESET_ALL + '\n')
    return print_string

# get_piece_colour()
# Returns the colorama directive to set the piece colour.
def get_piece_colour(char) :
    if (char in white_pieces) :
       return Fore.WHITE
    else :
        return Fore.BLACK

# get_piece_char()
# Returns the actual printed character given the unicode character
# from the python chess board string.
# If the given character is a black piece, the corresponding white
# piece is returned - this is because some typefaces render black
# and white pieces differently. We render the same characters
# and colour them with colorama.
def get_piece_char(char) :
    if (char in black_pieces) :
        return white_pieces[black_pieces.index(char)]
    else :
        return char

# get_square_colour()
# Returns the colorama directive for the background colour
# of the square defined by column and row.
def get_square_colour(column, row) :
    case_1 = (column % 2 == 1) and (row % 2 == 1)
    case_2 = (column % 2 == 0) and (row % 2 == 0)
    if (case_1 or case_2) :
        return Back.CYAN
    else :
        return Back.GREEN
