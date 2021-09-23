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
    print("'c' close")

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
    while(command != "c") :
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
        command = (input("\n:"))

        if (represents_int(command) and
            1 <= int(command) <= len(names)) :
            index = int(command) - 1
            name_path = dirpath + '/' + names[index]
            if (asset == MAIN) :
                menu(name_path, COLLECTION)
            elif (asset == COLLECTION) :
                menu(name_path, CATEGORY)
            elif (asset == CATEGORY) :
                item_menu(name_path)                

        elif (command == "n") :
            if (asset == MAIN) :
                new(dirpath, COLLECTION)
            elif (asset == COLLECTION) :
                new(dirpath, CATEGORY)
            elif (asset == CATEGORY) :
                new(dirpath, ITEM)                

        elif (command == "d" and len(names) != 0) :
            if (asset == MAIN) :
                delete(dirpath, names, COLLECTION)
            elif (asset == COLLECTION) :
                delete(dirpath, names, CATEGORY)
            elif (asset == CATEGORY) :
                delete(dirpath, names, ITEM)                

        return command

def item_menu(filepath) :
    command = ""
    while(command != "c") :
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
    print("'c' close")
    

repertoires_path = "Repertoires"
menu(repertoires_path, MAIN)

"""
def category_info(dirpath, category, index) :
    filepath = dirpath + '/' + category
    info = stats.category_stats(filepath)
    waiting = info[stats.STAT_WAITING]
    learned = info[stats.STAT_LEARNED]        
    size = info[stats.STAT_SIZE]
    if (size != 0) :
        coverage = int(round(learned / size * 100))
        coverage = (str(coverage) + "% ").rjust(5)
    else :
        coverage = "".ljust(5)
        
    info = str(index).ljust(3) + coverage
    info += category.ljust(20)
    info += str(waiting).ljust(9)
    info += str(learned).ljust(9)
    info += str(size).ljust(7)
    print(info)
    
def collection_options(dirpath, categories) :
    num_categories = len(categories)
    print ("")
    if (num_categories != 0) :
        print("[ID] select")
    print("'n' new")
    if (num_categories != 0) :
        print("'d' delete")
    print("'c' close")

# creates a new opening for the given colour
def new_category(dirpath) :    
    name = input("Name: ")
    category_path = dirpath + "/" + name
    while (os.path.exists(category_path)) :
        name = input("That name is taken.\nChoose another: ")
        category_path = dirpath + "/" + name
    os.mkdir(category_path)

def delete_category(dirpath) :
    categories = os.listdir(dirpath)
    categories.sort()
    command = input("ID to delete: ")
    if (represents_int(command) and
        1 <= int(command) <= len(categories)) :
        index = int(command) - 1
        category = categories[index]
        print (f"You are about to permanently delete `{category}'.")
        check = input("Are you sure? :")
        if (check == "y") :
            category_path = dirpath + "/" + category
            shutil.rmtree(category_path)

def collection_header() :
    header = "ID".ljust(3) + "COV.".ljust(5) + "CATEGORY".ljust(20)
    header += "WAITING".ljust(9) + "LEARNED".ljust(9)
    header += "TOTAL".ljust(6)
    print(header)

def item_info(dirpath, item, index) :
    filepath = dirpath + '/' + item
    item_name = item[:-4]
    info = stats.item_stats(filepath)
    waiting = info[stats.STAT_WAITING]
    learned = info[stats.STAT_LEARNED]        
    size = info[stats.STAT_SIZE]
    if (size != 0) :
        coverage = int(round(learned / size * 100))
        coverage = (str(coverage) + "% ").rjust(5)
    else :
        coverage = "".ljust(5)
        
    info = str(index).ljust(3) + coverage
    info += item_name.ljust(20)
    info += str(waiting).ljust(9)
    info += str(learned).ljust(9)
    info += str(size).ljust(7)
    print(info)
    
def category_options(items) :
    print ("")
    if (len(items) != 0) :
        print("[ID] select")
    print("'n' new")
    if (len(items) != 0) :
        print("'d' delete")
    print("'c' close")

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

# checks whether a string is a legal move in uci notation
def is_valid_uci(string,board) :
    for move in board.legal_moves :
        if (string == move.uci()) :
            return True
    return False

"""

"""
def main_menu(dirpath):
    command = ""
    while(command != "c") :
        collections = os.listdir(dirpath)
        collections.sort()        
        num_collections = len(collections)
        clear()
        main_overview(dirpath, collections)
        options(collections)

        command = (input("\n:"))
        if (represents_int(command) and
            1 <= int(command) <= num_collections) :
            index = int(command) - 1
            collection_menu(dirpath + '/' + collections[index])
        elif (command == "n") :
            new(dirpath, COLLECTION)
        elif (command == "d" and num_collections != 0) :
            delete(dirpath, collections, COLLECTION)

def main_overview(dirpath, collections) :
    print("YOUR COLLECTIONS")
    print("")
    if (len(collections) == 0) :
        print("You have none!")
        return
    header_row()
    for index, collection in enumerate(collections) :
        col_path = dirpath + '/' + collection
        info_row(stats.collection_stats(col_path),
                 collection,
                 index + 1)
            
def collection_menu(dirpath):
    command = ""
    while(command != "c") :
        categories = os.listdir(dirpath)
        categories.sort()        
        num_categories = len(categories)
        clear()
        collection_overview(dirpath, categories)
        options(categories)

        command = (input("\n:"))
        if (represents_int(command) and
            1 <= int(command) <= num_categories) :
            index = int(command) - 1
            category_menu(dirpath + '/' + categories[index])
        elif (command == "n") :
            new(dirpath, CATEGORY)
        elif (command == "d" and num_categories != 0) :
            delete(dirpath, categories, CATEGORY)

def collection_overview(dirpath, categories) :
    print("COLLECTION " + collection_name(dirpath))
    print("")
    if (len(categories) == 0) :
        print("There are no categories in this collection.")
        return
    header_row()
    for index, category in enumerate(categories) :
        cat_path = dirpath + '/' + category
        info_row(stats.category_stats(cat_path),
                 category,
                 index + 1)


def category_menu(dirpath):
    command = ""
    while(command != "c") :
        items = os.listdir(dirpath)
        items.sort()
        clear()
        category_overview(dirpath, items)
        options(items)
        
        command = (input("\n:"))        
        if (represents_int(command) and
            1 <= int(command) <= len(items)) :
            item_index = int(command) - 1
            filepath = dirpath + "/" + items[item_index]
            item_menu(filepath)
        elif (command == "n") :
            new(dirpath, ITEM)
        elif (command == "d" and len(items) != 0) :
            delete(dirpath, items, ITEM)

def category_overview(dirpath, items) :
    print("CATEGORY   " + category_name(dirpath))
    print("COLLECTION " + collection_name(dirpath))
    print("")
    if (len(items) == 0) :
        print("There no items in this category.")
        return
    header_row()
    for index, item in enumerate(items) :
        item_path = dirpath + '/' + item
        info_row(stats.item_stats(item_path),
                 item[:-4],
                 index + 1)


"""            
