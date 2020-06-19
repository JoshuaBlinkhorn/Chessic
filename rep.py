# rep.py -- the backend module for the repertoire.py script

# deck statuses

EMPTY = 0
CLEARED = 1
READY = 2

class Card :
    def __init__(self,board) :
        self.board = board
        self.last_date = False
        self.due_date = False
        
class Deck :

    def __init__(self) :
        self.new = []
        self.learning = []
        self.reviewing = []
        self.inactive = []
        self.unreachable = []
        self.new_daily = 10

    def piles(self) :
        return [self.new, self.learning, self.reviewing, self.inactive, self.unreachable]

    def due_pile(self) :
        cards = []
        for card in self.reviewing :
            if (card.due_date <= date.today()):
                cards.append(card)
        return cards

    def status(self) :
        playable_pile = self.new+self.learning+self.reviewing+self.inactive
        if (len(playable_pile) == 0) :
            return INSUFFICIENT
        scheduled_pile = self.new + self.learning + self.due_pile()
        if (len(scheduled_pile) == 0) :
            return CLEARED            
        else :
            return READY

    def get_card(self,board) :
        for pile in self.piles() :
            for index, card in enumerate(pile) :
                if (card.board == board) :
                    return pile.pop(index)
        return False

        
# repertoire statuses

INSUFFICIENT = 0
SCHEDULED = 1
UNSCHEDULED = 2

class Repertoire :
    def __init__(self,name,colour) :
        self.name = name
        self.colour = colour
        self.lines = Deck()
        self.positions = Deck()

    def status(self) :
        if (self.lines.status() == EMPTY and self.positions.status() == EMPTY) :
            return INSUFFICIENT
        if (self.lines.status() == READY or self.positions.status() == READY) :
            return SCHEDULED
        else :
            return UNSCHEDULED
