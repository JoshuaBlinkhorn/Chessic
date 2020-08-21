import chess
import chess.pgn
import rep
import datetime
import pickle

rep_path = "Repertoires"

def process_node(node,player_to_move) :
    if (node == game) :
        node.training = False
        node.player_to_move = False
    else :
        if (player_to_move == False) :
            node.training = rep.TrainingData()
        else :
            node.training = False
        node.player_to_move = player_to_move
    if (not node.is_end()) :
        for child in node.variations :
            process_node(child, not player_to_move)

def save_repertoire (repertoire) :
    filename = rpt_path(repertoire.meta.name)
    update(repertoire)
    with open(filename, "wb") as file :
        pickle.dump(repertoire,file)

def rpt_path(name) :
    return rep_path + "/" + name + ".rpt"

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
            for status in [rep.NEW,rep.FIRST_STEP,rep.SECOND_STEP] :
                if (node.training.status == status) :
                    node.training.status = rep.INACTIVE
        else : # threshold exceeds 0
            if (node.training.status == rep.INACTIVE) :
                node.training.status = rep.NEW
            for status in [rep.NEW,rep.FIRST_STEP,rep.SECOND_STEP] :
                if (node.training.status == status) :
                    threshold -= 1

        
pgn = open("trax-1.rpt")
game = chess.pgn.read_game(pgn)
            
# add root node data
game.meta = rep.MetaData("traxler", False)

# add training node data
process_node(game,False)

# pickle it
save_repertoire(game)

        
