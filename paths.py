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
# MODULE paths.py

# SYNOPSIS
# Provides functions for maniputaing file and directory paths for
# user collections.

def item_name(filepath) :
    path = filepath.split('/')
    return path[3][:-4]

def category_name(filepath) :
    path = filepath.split('/')
    return path[2]

def collection_name(filepath) :
    path = filepath.split('/')
    return path[1]

