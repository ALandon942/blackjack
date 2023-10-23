from random import shuffle

LIMIT = 21
STARTING_BANKROLL = 100.0
BLACKJACK_BONUS_ODDS = 1.5
EVEN_ODDS = 1
DEALER_STAY_LIMIT = 17


class Card:
    suits = {'Clubs', 'Diamonds', 'Hearts', 'Spades'}
    ranks = {'Ace', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Jack', 'Queen', 'King'}
    values = {'Ace': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5, 'Six': 6, 'Seven': 7, 'Eight': 8, 'Nine': 9,
              'Ten': 10, 'Jack': 10, 'Queen': 10, 'King': 10}
    # aces valued at 11 will be handled separately when evaluating whole hand

    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def value(self):
        return self.values[self.rank]

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

    def total_and_ace_status(self):
        """
        Returns two values:
        - total: the total value of the hand
        - ace_status: true if this total includes any aces valued at 11
        :return: tuple of (total, ace_status)
        """
        amount = 0
        ace_count = 0
        ace_status = False
        for card in self.cards:
            value = card.value()
            amount += value
            if card.rank == "Ace":
                ace_count += 1
        # Promote aces to 11 as long as it won't cause a bust:
        for i in range(0, ace_count):
            if amount + 10 <= LIMIT:
                amount += 10
                ace_status = True
        return amount, ace_status

    def total(self):
        return self.total_and_ace_status()[0]

    def is_bust(self):
        return self.total() > LIMIT

    def is_blackjack(self):
        return len(self.cards) == 2 and self.total() == LIMIT

    def add(self, card):
        self.cards.append(card)

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


class Player:
    def __init__(self, starting_bankroll=STARTING_BANKROLL):
        self.bankroll = Bankroll(starting_bankroll)
        self.bet = None
        self.hand = None


def prompt_for_bet(bankroll):
    while True:
        entry = input('Enter your bet or Q to quit ')
        if entry.upper() == 'Q':
            print('Bye!')
            exit(0)
        try:
            return bankroll.place_bet(float(entry))
        except ValueError:
            print('Not a valid amount')


def deal_in(shoe, player):
    player.hand = deal(shoe)


def deal(shoe):
    hand = Hand()
    for i in range(0, 2):
        hand.add(shoe.draw())
    return hand


def format_hand(hand, hide_first_card=False):
    card_strings = [str(card) for card in hand.cards]
    if hide_first_card:
        card_strings[0] = '?'
    return ', '.join(card_strings)


def prompt_hit_or_stay():
    """
    Prompt user to hit or stay.
    :return: True if user opted to hit
    """
    entry = None
    while entry is None:
        entry = input('Hit or stay? (H/S) ').upper()
        if entry not in ('H', 'S'):
            entry = None
            print('Not a valid entry')
    return entry == 'H'


def player_turn(shoe, hand):
    # Dealing loop:
    # Prompt stay or hit til valid answer
    # Stop when player busts, hits limit or stays
    if hand.is_blackjack():
        print('Blackjack!')
        hitting = False
    else:
        hitting = True
    while hitting:
        hitting = prompt_hit_or_stay()
        if hitting:
            hand.add(shoe.draw())
            print('Your cards: ' + format_hand(hand))
            if hand.is_bust():
                print("Bust!")
                hitting = False
            elif hand.total() == LIMIT:
                print(f'You reached {LIMIT}')
                hitting = False


def dealer_hits(hand):
    total, ace_status = hand.total_and_ace_status()
    if total < DEALER_STAY_LIMIT:
        return True
    elif total == DEALER_STAY_LIMIT:
        # Dealer can draw on a "soft seventeen"
        return ace_status
    else:
        return False


def dealer_turn(shoe, hand):
    # Reveal hidden card
    print('Dealer cards: ' + format_hand(hand))
    while dealer_hits(hand):
        print('Dealer hits')
        hand.add(shoe.draw())
        print(format_hand(hand))
    if hand.is_bust():
        print('Dealer busts')
    else:
        print('Dealer stays')


def settle_bet(player, dealer_hand):
    # Compare hands
    # Calculate bet value
    # Pay out bet to player's payroll
    outcome = player.hand.compare(dealer_hand)
    if outcome > 0:
        player.bet.win(BLACKJACK_BONUS_ODDS if player.hand.is_blackjack() else EVEN_ODDS)
        print('You win!')
    elif outcome < 0:
        player.bet.lose()
        print('You lose!')
    else:
        print('Standoff!')
        pass  # player just gets their bet back
    player.bet.pay_out(player.bankroll)
    # ENHANCEMENT: if there exist options like split etc. then house recovers advantage by winning if both the dealer
    # and the player bust


def return_cards(shoe, hands):
    for hand in hands:
        shoe.put_back(hand.cards)
        hand.cards = []


def main():
    player = Player()
    shoe = Shoe()
    # Main loop
    while player.bankroll.amount > 0:
        print(f'You have ${player.bankroll.amount:.2f}')
        player.bet = prompt_for_bet(player.bankroll)
        print(f'${player.bet.amount:.2f} is on the table.')
        deal_in(shoe, player)
        print('Your cards: ' + format_hand(player.hand))
        dealer_hand = deal(shoe)
        print('Dealer cards: ' + format_hand(dealer_hand, hide_first_card=True))
        player_turn(shoe, player.hand)
        dealer_turn(shoe, dealer_hand)
        settle_bet(player, dealer_hand)
        if player.bankroll.amount <= 0:
            print('You are bankrupt! Game over')
        else:
            return_cards(shoe, (dealer_hand, player.hand))


if __name__ == '__main__':
    main()
