# rep.py -- the backend module for the repertoire.py script

# deck statuses

EMPTY = 0
CLEARED = 1
READY = 2

class Card :
    def __init__(self) :
        self.content = False
        self.last_date = False
        self.due_date = False
        
class Deck :
    def __init__(self) :
        self.new = []
        self.learning = []
        self.reviewing = []
        self.inactive = []
        self.unreachable = []

    def piles(self) :
        return (self.new, self.learning, self.reviewing, self.inactive, self.unreachable)

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
        if (lines.status() == READY or positions.status() == rREADY) :
            return SCHEDULED
        else :
            return UNSCHEDULED
