from random import shuffle

LIMIT = 21


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

    def draw(self):
        return self.cards.pop(0)

    def put_back(self, cards):
        # To simplify the logic we'll assume shuffling is continuous
        self.cards.extend(cards)
        shuffle(self.cards)


class Hand:
    def __init__(self):
        self.cards = []

    def total(self):
        amount = 0
        for card in self.cards:
            amount += card.value()
        return amount

    def is_bust(self):
        return self.total() > LIMIT

    def is_blackjack(self):
        return len(self.cards) == 2 and self.total() == LIMIT

    def add(self, card):
        self.cards.append(card)
        if self.total() > LIMIT:
            # see if revaluing any aces will save us
            for card in self.cards:
                card.switch_values()

    def compare(self, other):
        """
        Test how this hand compares to another.
        :param other: another hand
        :return: negative if this hand loses to other, 0 if they're tied, and positive if this hand beats other
        """
        if self.is_bust():
            if other.is_bust():
                return 0
            else:
                return -1
        elif self.is_blackjack():
            if other.is_blackjack():
                return 0
            else:
                return 1
        else:
            if other.is_bust():
                return 1
            elif other.is_blackjack():
                return -1
            else:
                return self.total() - other.total()


class Bankroll:
    def __init__(self, amount=0):
        self.amount = amount

    def add(self, amount):
        self.amount += amount
        return self.amount

    def subtract(self, amount):
        if self.amount < amount:
            raise ValueError(f'Can\'t subtract {amount} from balance of {self.amount}')
        else:
            self.amount -= amount
        return self.amount

    def place_bet(self, amount):
        self.subtract(amount)
        return Bet(amount)


class Bet:
    def __init__(self, stake):
        self.amount = stake

    def win(self, odds):
        winnings = self.amount * odds
        self.amount += winnings

    def lose(self):
        self.amount = 0

    def pay_out(self, bankroll):
        payout = self.amount
        bankroll.add(payout)
        self.amount = 0
        return payout

