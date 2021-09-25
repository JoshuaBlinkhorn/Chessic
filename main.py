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
# MODULE main.py

# SYNOPSIS
# Provides the main user interface.

import os
import shutil
import enum
import stats
import manager
import paths
from graphics import clear
import trainer

# Enumeration for the Chessic hierarchy;
# In this hierarchy, training trees are called `items';
# groups of items are called `categories';
# groups of categories are called `collections'.
# The only purpose of defining this enumeration is to avoid
# repeating code -- for example, the collection and category menus
# are essentially identical.
class Asset(enum.Enum) :
    MAIN = 0
    COLLECTION = 1
    CATEGORY = 2
    ITEM = 3

# represents_int()
# Determines whether a string represents an integer.
def represents_int(string):
    try: 
        int(string)
        return True
    except ValueError:
        return False

# options()
# Prints options for the typical menu.
def options(names) :
    num_names = len(names)
    print ("")
    if (num_names != 0) :
        print("[ID] select")
    print("'n' new")
    if (num_names != 0) :
        print("'d' delete")
    print("'b' back")

# new()
# Creates a new asset (i.e. collection, category etc.).
def new(dirpath, asset) :    
    name = input("Name: ")
    while (True) :
        new_path = dirpath + "/" + name
        if (asset == Asset.ITEM) :
            new_path += '.rpt'
        if (not os.path.exists(new_path)) :
            break
        name = input("That name is taken.\nChoose another: ")        
    
    if (asset != Asset.ITEM) :
        os.mkdir(new_path)
    else :
        manager.new_tree(new_path)

# new()
# Creates a new asset (i.e. collection, category etc.)..        
def delete(dirpath, names, asset) :
    command = input("ID to delete: ")
    if (represents_int(command) and
        1 <= int(command) <= len(names)) :
        index = int(command) - 1
        name = names[index]
        print (f"You are about to permanently delete `{name}'.")
        check = input("Are you sure? (y/n):")
        if (check == "y") :
            path = dirpath + "/" + name
            if (asset == Asset.ITEM) :
                os.remove(path)
            else :
                shutil.rmtree(path)

# menu()
# Prints the typical menu for the given asset.
# The item menu is significantly different; this function launches
# the menu for the other assets (`main', `collection', and
# `category').
def menu(dirpath, asset):
    command = ""
    while(command != "b") :
        names = os.listdir(dirpath)
        names.sort()        
        title(dirpath, asset)
        table(dirpath, names, asset)
        options(names)
        command = prompt(dirpath, names, asset)

# title()
# Prints the menu title.
def title(dirpath, asset) :
    clear()
    if (asset == Asset.MAIN) :
        print("YOUR COLLECTIONS")
    elif (asset == Asset.COLLECTION) :
        print("COLLECTION " + paths.collection_name(dirpath))
    elif (asset == Asset.CATEGORY) :
        print("CATEGORY   " + paths.category_name(dirpath))
        print("COLLECTION " + paths.collection_name(dirpath))
    print("")

# table()
# Prints the whole table for the typical menu.
def table(dirpath, names, asset) :
    if (len(names) == 0) :
        if (asset == Asset.MAIN) :
            print("You have no collections.")
        elif (asset == Asset.COLLECTION) :
            print("There are no categories in this collection.")
        elif (asset == Asset.CATEGORY) :
            print("There are no items in this collection.")
        return

    header_row()
    for index, name in enumerate(names) :
        path = dirpath + '/' + name
        if (asset == Asset.MAIN) :
            info = stats.collection_stats(path)
        elif (asset == Asset.COLLECTION) :
            info = stats.category_stats(path)
        elif (asset == Asset.CATEGORY) :
            info = stats.item_stats(path)
            name = name[:-4]
        info_row(info, name, index + 1)

# header_row()
# Prints the table header for the typical menu.
def header_row() :
    string = "ID".ljust(3) + "COV.".ljust(5)
    string += "ITEM".ljust(20) + "WAITING".ljust(9) 
    string += "LEARNED".ljust(9) + "TOTAL".ljust(6)
    print(string)

# info_row()
# Prints an internal table row for the typical menu.
def info_row(info, name, index) :
    waiting = info[stats.STAT_WAITING]
    learned = info[stats.STAT_LEARNED]        
    size = info[stats.STAT_SIZE]
    if (size != 0) :
        coverage = int(round(learned / size * 100))
        coverage = (str(coverage) + "% ").rjust(5)
    else :
        coverage = "".ljust(5)
        
    info_string = str(index).ljust(3) + coverage
    info_string += name.ljust(20) + str(waiting).ljust(9)
    info_string += str(learned).ljust(9) + str(size).ljust(7)
    print(info_string)

# prompt()
# Handles the typical menu prompt.
# Returns the user's command.
def prompt(dirpath, names, asset) :
    new_asset = next_asset(asset)
    command = (input("\n:"))
    if (represents_int(command) and
        1 <= int(command) <= len(names)) :
        index = int(command) - 1
        name_path = dirpath + '/' + names[index]
        if (asset == Asset.MAIN or asset == Asset.COLLECTION) :
            menu(name_path, new_asset)
        elif (asset == Asset.CATEGORY) :
            item_menu(name_path)                
    elif (command == "n") :
        new(dirpath, new_asset)
    elif (command == "d" and len(names) != 0) :
        delete(dirpath, names, new_asset)
    return command

# next_asset()
# Returns the next asset down in the hierarchy
def next_asset(asset) :
    if (asset == Asset.MAIN) :
        return Asset.COLLECTION
    elif (asset == Asset.COLLECTION) :
        return Asset.CATEGORY
    elif (asset == Asset.CATEGORY) :
        return Asset.ITEM

# item_menu()
# Launches the menu for the item asset.
def item_menu(filepath) :
    command = ""
    while(command != "b") :
        info = stats.item_stats_full(filepath)        
        clear()
        item_header(filepath, info)
        item_overview(info)
        item_options(info)
        command = input("\n:")
        if (command == "m") :
            manager.manage(filepath)
        elif (command == "t") :
            trainer.train(filepath)

# item_header()
# Prints the header for the item menu.
def item_header(filepath, info) :
    width = 14
    waiting = info[stats.STAT_NEW] + info[stats.STAT_FIRST_STEP]
    waiting += info[stats.STAT_SECOND_STEP] + info[stats.STAT_DUE]  
    if (waiting > 0) :
        status_msg = "Training available"
    else :
        status_msg = "Up to date"    
    print("ITEM".ljust(width) + paths.item_name(filepath))
    print("CATEGORY".ljust(width) + paths.category_name(filepath))
    print("COLLECTION".ljust(width) +paths.collection_name(filepath))
    print("STATUS".ljust(width) + status_msg)

# item_overview()
# Prints information for the tree.
def item_overview(info) :
    width = 14
    learning = info[stats.STAT_FIRST_STEP]
    learning += info[stats.STAT_SECOND_STEP]
    print("")
    print("New".ljust(width) + str(info[stats.STAT_NEW]))
    print("Learning".ljust(width) + str(learning))
    print("Due".ljust(width) + str(info[stats.STAT_DUE]))
    print("")
    print("In review".ljust(width) + str(info[stats.STAT_REVIEW]))
    print("Inactive".ljust(width) + str(info[stats.STAT_INACTIVE]))
    print("Reachable".ljust(width) + str(info[stats.STAT_REACHABLE]))
    print("Total".ljust(width) + str(info[stats.STAT_TOTAL]))

# item_options()
# Prints the options for the item menu.
def item_options(info) :
    waiting = info[stats.STAT_NEW] + info[stats.STAT_FIRST_STEP]
    waiting += info[stats.STAT_SECOND_STEP] + info[stats.STAT_DUE]
    print("")
    if (waiting > 0) :
        print("'t' train")
    print("'m' manage")
    print("'b' back")
    
# entry point
repertoires_path = "Collections"
menu(repertoires_path, Asset.MAIN)

