"""
Copyright Joshua Blinkhorn 2021

This file is part of Chessic.

Chessic is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Chessic is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Chessic.  If not, see <https://www.gnu.org/licenses/>.
"""

# Chessic v1.0
# convert_pgn.py

# SYNOPSIS
# An ad hoc script that converts a PGN file into a Chessic tree.

import os
import sys
import chess
import chess.pgn
import tree

# process()
# Adds default training data to a solution; sets node.training
# to None for all non-solution nodes when called on the root.
def process(node) :
    if (tree.is_raw_solution(node)) :
        node.training = tree.TrainingData()
    else :
        node.training = None
    if (not node.is_end()) :
        for child in node.variations :
            process(child)

# check_usage()
# Checks that the command line paramaters make sense
def check_usage(args) :
    if (len(args) != 4 or
        (agrs[3] != "w" and args[3] != "b")) :
        help_string = "usage: python3 convert-pgn.py"
        help_string += " <source-dir> <destination-dir> <w|b>"
        print(help_string)
        quit()

# entry point
check_args(sys.argv)

# setup
source_dir = sys.argv[1]
PGNs = os.listdir(source_dir)
destination_dir = sys.argv[2]
colour = (sys.argv[3] == "w")

# cycle through PGNs and convert each
for PGN in PGNs :
    PGN_path = source_dir + '/' + PGN
    RPT_path = destination_dir + '/' + PGN[:-4] + ".rpt"
    pgn = open(PGN_path)
    root = chess.pgn.read_game(pgn)
    root.meta = tree.MetaData(colour)
    root.training = None
    process(root) # processes the whole tree
    tree.update_statuses(root)
    tree.save(RPT_path, root)
