# MODULE paths.py
# this file is part of Opening Trainer by Joshua Blinkhorn

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

