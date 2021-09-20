# MODULE items.py

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
        normalise(repertoire,max_value)
    else :
        learning_threshold = max_value - learning_value
        normalise(repertoire,learning_threshold)

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

