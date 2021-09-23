import os
import shutil

import stats
import manager
import paths
from graphics import clear
import training
from training import TrainingData, MetaData

MAIN = 0
COLLECTION = 1
CATEGORY = 2
ITEM = 3

def represents_int(string):
    try: 
        int(string)
        return True
    except ValueError:
        return False

def header_row() :
    string = "ID".ljust(3) + "COV.".ljust(5)
    string += "ITEM".ljust(20) + "WAITING".ljust(9) 
    string += "LEARNED".ljust(9) + "TOTAL".ljust(6)
    print(string)

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

def options(names) :
    num_names = len(names)
    print ("")
    if (num_names != 0) :
        print("[ID] select")
    print("'n' new")
    if (num_names != 0) :
        print("'d' delete")
    print("'b' back")

def new(dirpath, asset) :    
    name = input("Name: ")
    while (True) :
        new_path = dirpath + "/" + name
        if (asset == ITEM) :
            new_path += '.rpt'
        if (not os.path.exists(new_path)) :
            break
        name = input("That name is taken.\nChoose another: ")        
    
    if (asset != ITEM) :
        os.mkdir(new_path)
    else :
        manager.new_item(new_path)
        
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
            if (asset == ITEM) :
                os.remove(path)
            else :
                shutil.rmtree(path)

def menu(dirpath, asset):
    command = ""
    while(command != "b") :
        names = os.listdir(dirpath)
        names.sort()        
        title(dirpath, asset)
        table(dirpath, names, asset)
        options(names)
        command = prompt(dirpath, names, asset)

def title(dirpath, asset) :
    clear()
    if (asset == MAIN) :
        print("YOUR COLLECTIONS")
    elif (asset == COLLECTION) :
        print("COLLECTION " + paths.collection_name(dirpath))
    elif (asset == CATEGORY) :
        print("CATEGORY   " + paths.category_name(dirpath))
        print("COLLECTION " + paths.collection_name(dirpath))
    print("")

def table(dirpath, names, asset) :
    if (len(names) == 0) :
        if (asset == MAIN) :
            print("You have no collections.")
        elif (asset == COLLECTION) :
            print("There are no categories in this collection.")
        elif (asset == CATEGORY) :
            print("There are no items in this collection.")
        return

    header_row()
    for index, name in enumerate(names) :
        path = dirpath + '/' + name
        if (asset == MAIN) :
            info = stats.collection_stats(path)
        elif (asset == COLLECTION) :
            info = stats.category_stats(path)
        elif (asset == CATEGORY) :
            info = stats.item_stats(path)
            name = name[:-4]
        info_row(info, name, index + 1)

def prompt(dirpath, names, asset) :
    new_asset = next_asset(asset)
    command = (input("\n:"))
    if (represents_int(command) and
        1 <= int(command) <= len(names)) :
        index = int(command) - 1
        name_path = dirpath + '/' + names[index]
        if (asset == MAIN or asset == COLLECTION) :
            menu(name_path, new_asset)
        elif (asset == CATEGORY) :
            item_menu(name_path)                
    elif (command == "n") :
        new(dirpath, new_asset)
    elif (command == "d" and len(names) != 0) :
        delete(dirpath, names, new_asset)
    return command

def next_asset(asset) :
    if (asset == MAIN) :
        return COLLECTION
    elif (asset == COLLECTION) :
        return CATEGORY
    elif (asset == CATEGORY) :
        return ITEM

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
            training.train(filepath)

def item_header(filepath, info) :
    width = 14
    waiting = info[stats.STAT_NEW] + info[stats.STAT_FIRST_STEP]
    waiting += info[stats.STAT_SECOND_STEP] + info[stats.STAT_DUE]  
    if (waiting > 0) :
        status_msg = "training available"
    else :
        status_msg = "up to date"    
    print("ITEM".ljust(width) + paths.item_name(filepath))
    print("CATEGORY".ljust(width) + paths.category_name(filepath))
    print("COLLECTION".ljust(width) +paths.collection_name(filepath))
    print("STATUS".ljust(width) + status_msg)


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

def item_options(info) :
    waiting = info[stats.STAT_NEW] + info[stats.STAT_FIRST_STEP]
    waiting += info[stats.STAT_SECOND_STEP] + info[stats.STAT_DUE]
    print("")
    if (waiting > 0) :
        print("'t' train")
    print("'m' manage")
    print("'b' back")
    

repertoires_path = "Repertoires"
menu(repertoires_path, MAIN)
