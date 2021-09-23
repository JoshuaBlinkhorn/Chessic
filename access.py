# MODULE access.py

#SYNOPSIS


import pickle
import datetime
import chess

NEW = 0
FIRST_STEP = 1
SECOND_STEP = 2
REVIEW = 3
INACTIVE = 4

def save_item (filepath, item) :
    update(item)
    with open(filepath, "wb") as file :
        pickle.dump(item,file)

def load_item (filepath) :
    with open(filepath, "rb") as file :
        item = pickle.load(file)
    update(item)
    return item

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
        set_statuses(repertoire,max_value)
    else :
        num_remaining = max_value - learning_value
        set_statuses(repertoire, num_remaining)

def set_statuses(node, num_remaining) :
    # configure training data
    if (node.training) :
        if (num_remaining <= 0) :
            for status in [NEW,FIRST_STEP,SECOND_STEP] :
                if (node.training.status == status) :
                    node.training.status = INACTIVE
        else : # threshold exceeds 0
            if (node.training.status == INACTIVE) :
                node.training.status = NEW
            for status in [NEW,FIRST_STEP,SECOND_STEP] :
                if (node.training.status == status) :
                    num_remaining -= 1

    if (not node.is_end()) :
        if (node.player_to_move) : # call all children recursively
            num_remaining = set_statuses(node.variations[0],
                                         num_remaining)
        else : # call only the main variation
            for child in node.variations :
                num_remaining = set_statuses(child,
                                             num_remaining)
                
    return num_remaining

