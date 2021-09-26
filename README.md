Chessic v1.0
Copyright Joshua Blinkhorn 2021

To start Chessic, open a terminal, navigate to the home directory
(Chessic/) and type:

	   python3 chessic.py	

Chessic requires Python version 3 with the module python-chess
installed. For installations instructions, see the python
and python-chess documenation.

To convert a PGN into a Chessic item (i.e. an opening variation),
use the packaged script `convert-pgn.py' as follows:

    python3 convert-pgn.py <source-dir> <destination-dir> <w|b>    

All files in `source-dir' are treated ad PGNs,
converted to Chessic variations and saved in `destination-dir',
and treated as variations to be played by white ('w') or black ('b').
Variations for training must be moved into a category in a
collection, stored in the directory `Chessic/Collections'.

For further information, see the packaged Chessic manual
(Documentation/manual.pdf).