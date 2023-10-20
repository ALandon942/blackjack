from random import shuffle


class Card:
    suits = {'Clubs', 'Diamonds', 'Hearts', 'Spades'}
    ranks = {'Ace', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Jack', 'Queen', 'King'}
    values = {'Ace': (11, 1), 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5, 'Six': 6, 'Seven': 7, 'Eight': 8, 'Nine': 9,
              'Ten': 10, 'Jack': 10, 'Queen': 10, 'King': 10}

    # values of ace are handled in the order they'll be used

    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        self._value_index = 0

    def value(self):
        value = self.values[self.rank]
        if isinstance(value, tuple):
            return value[self._value_index]
        else:
            return value

    def switch_values(self):
        value = self.values[self.rank]
        if isinstance(value, tuple):
            self._value_index = (self._value_index + 1) % len(value)
            # if we try to switch the ace while already bust, we'll wrap around to the higher value - keep running
            # and stay bust

    def __str__(self):
        return f'{self.rank} of {self.suit}'


class Shoe:
    # Future enhancement: multiple decks in shoe
    def __init__(self):
        self.cards = [Card(suit, rank) for suit in Card.suits for rank in Card.ranks]
        shuffle(self.cards)

    def hit(self):  # Stop hitting yourself! *rimshot*
        return self.cards.pop(0)

    def put_back(self, cards):
        # To simplify the logic we'll assume shuffling is continuous
        self.cards.extend(cards)
        shuffle(self.cards)


