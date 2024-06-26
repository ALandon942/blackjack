import unittest
import unittest.mock
import main
import builtins
from main import Card, Shoe, Hand, LIMIT, Bankroll, Bet


def build_hand(cards):
    hand = Hand()
    for card in cards:
        hand.add(card)
    return hand


class CardTest(unittest.TestCase):
    def test_stringify(self):
        card = Card("Hearts", "Nine")
        self.assertEqual("Nine of Hearts", str(card))

    def test_number_card_value(self):
        number_card = Card("Hearts", "Nine")
        self.assertEqual(9, number_card.value())

    def test_face_card_value(self):
        face_card = Card("Spades", "Queen")
        self.assertEqual(10, face_card.value())

    # ace value is covered by tests of hand totals


class DeckTest(unittest.TestCase):
    cards_in_order = [Card(suit, rank) for suit in Card.suits for rank in Card.ranks]

    def test_card_generation(self):
        deck = Shoe()

        def comparison_set(cards):
            return {(card.suit, card.rank) for card in cards}

        self.assertEqual(len(deck.cards), 52)
        self.assertEqual(comparison_set(self.cards_in_order), comparison_set(deck.cards))

    def test_shuffle_on_init(self):
        shoe = Shoe()

        def comparison_list(cards):
            return [(card.suit, card.rank) for card in cards]

        self.assertNotEqual(comparison_list(self.cards_in_order), comparison_list(shoe.cards), "Deck is not shuffled")

    def test_draw(self):
        shoe = Shoe()
        full = len(shoe.cards)
        top_card = shoe.cards[0]
        dealt_card = shoe.draw()
        self.assertEqual((top_card.suit, top_card.rank), (dealt_card.suit, dealt_card.rank))
        self.assertEqual(full - 1, len(shoe.cards))

    def test_put_back(self):
        shoe = Shoe()
        full = len(shoe.cards)
        discard = []
        for i in range(0, 10):
            discard.append(shoe.draw())
        shoe.put_back(discard)
        self.assertEqual(full, len(shoe.cards))
        # not going to test reshuffling


class HandTest(unittest.TestCase):
    def test_init(self):
        hand = Hand()
        self.assertEqual(0, hand.total())
        self.assertFalse(hand.is_blackjack(), "Blackjack on empty hand!")
        self.assertFalse(hand.is_bust(), "Bust on empty hand!")

    def test_add_one(self):
        card = Card("Hearts", "Four")
        hand = build_hand((card,))
        self.assertEqual(card.value(), hand.total())
        self.assertFalse(hand.is_blackjack(), "Blackjack declared falsely")
        self.assertFalse(hand.is_bust(), "Bust reached prematurely")

    def test_both_ace_values(self):
        # Hand where a player gets the best outcome with one ace valued at 11 and the other at 1:
        hand = build_hand([Card("Hearts", "Ace"), Card("Clubs", "Ace"), Card("Hearts", "Nine")])
        self.assertEqual(21, hand.total())

    def test_blackjack(self):
        hand = build_hand([Card("Diamonds", "King"), Card("Spades", "Ace")])
        self.assertEqual(LIMIT, hand.total())
        self.assertTrue(hand.is_blackjack(), "Failed to detect blackjack")
        self.assertFalse(hand.is_bust(), "Blackjack mistaken for bust")

    def test_21_with_ace_switch(self):
        hand = build_hand(
            [Card("Diamonds", "Six"), Card("Spades", "Ace"), Card("Clubs", "Five"), Card("Diamonds", "Nine")])
        self.assertEqual(LIMIT, hand.total())
        self.assertFalse(hand.is_blackjack(), "Non-blackjack 21 mistaken for blackjack")
        self.assertFalse(hand.is_bust(), "21 mistaken for bust")

    def test_bust(self):
        hand = build_hand([Card("Diamonds", "Ten"), Card("Hearts", "Seven"), Card("Hearts", "Five")])
        self.assertGreater(hand.total(), LIMIT)
        self.assertFalse(hand.is_blackjack(), "Bust mistaken for blackjack")
        self.assertTrue(hand.is_bust(), "Failed to detect bust")

    def test_compare_one_blackjack(self):
        hand1 = build_hand([Card("Diamonds", "Ace"), Card("Diamonds", "King")])
        # Make the other hand a plain old 21 to assert that blackjack beats it:
        hand2 = build_hand([Card("Hearts", "Nine"), Card("Clubs", "Nine"), Card("Clubs", "Three")])
        self.assertGreater(hand1.compare(hand2), 0)
        self.assertLess(hand2.compare(hand1), 0)

    def test_compare_two_blackjacks(self):
        hand1 = build_hand([Card("Diamonds", "Ace"), Card("Diamonds", "King")])
        hand2 = build_hand([Card("Spades", "Ace"), Card("Clubs", "Ten")])
        self.assertEqual(0, hand1.compare(hand2))
        self.assertEqual(0, hand2.compare(hand1))

    def test_compare_one_bust(self):
        hand1 = build_hand([Card("Hearts", "Nine"), Card("Clubs", "Nine"), Card("Clubs", "Four")])
        hand2 = build_hand([Card("Hearts", "Four"), Card("Clubs", "Two")])
        self.assertLess(hand1.compare(hand2), 0)
        self.assertGreater(hand2.compare(hand1), 0)

    def test_compare_two_busts(self):
        hand1 = build_hand([Card("Hearts", "Nine"), Card("Clubs", "Nine"), Card("Clubs", "Four")])
        hand2 = build_hand([Card("Spades", "King"), Card("Spades", "Ten"), Card("Diamonds", "Six")])
        self.assertEqual(0, hand1.compare(hand2))
        self.assertEqual(0, hand2.compare(hand1))

    def test_compare_no_blackjack_or_bust(self):
        hand1 = build_hand([Card("Hearts", "Nine"), Card("Clubs", "Four")])
        hand2 = build_hand([Card("Spades", "King"), Card("Diamonds", "Six")])
        self.assertLess(hand1.compare(hand2), 0)
        self.assertGreater(hand2.compare(hand1), 0)
        self.assertEqual(0, hand1.compare(hand1))


class BankrollTest(unittest.TestCase):
    def test_init(self):
        bankroll = Bankroll(500)
        self.assertEqual(500, bankroll.amount)

    def test_add(self):
        bankroll = Bankroll(500)
        self.assertEqual(501, bankroll.add(1))
        self.assertEqual(501, bankroll.amount)

    def test_subtract(self):
        bankroll = Bankroll(500)
        self.assertEqual(0, bankroll.subtract(500))
        self.assertEqual(0, bankroll.amount)

    def test_overdraw(self):
        bankroll = Bankroll(500)
        try:
            bankroll.subtract(501)
        except ValueError:
            pass
        else:
            self.fail("ValueError not raised on overdraft")
        self.assertEqual(500, bankroll.amount)

    def test_bet(self):
        bankroll = Bankroll(500)
        bet = bankroll.place_bet(50)
        self.assertEqual(bet.amount, 50)
        self.assertEqual(450, bankroll.amount)

    def test_overdraft_bet(self):
        bankroll = Bankroll(500)
        try:
            bet = bankroll.place_bet(600)
        except ValueError:
            pass
        else:
            self.fail("Excessive bet placed")

    class BetTest(unittest.TestCase):
        def test_init(self):
            bet = Bet(50)
            self.assertEqual(50, bet.amount)

        def test_win(self):
            bet = Bet(50)
            bet.win(0.5)
            self.assertEqual(75, bet.amount)

        def test_lose(self):
            bet = Bet(50)
            bet.lose()
            self.assertEqual(0, bet.amount)

        def test_pay_out(self):
            bet = Bet(50)
            bankroll = Bankroll()
            bet.pay_out(bankroll)
            self.assertEqual(0, bet.amount)
            self.assertEqual(50, bankroll.amount)


class TestMain(unittest.TestCase):
    def test_prompt_for_bet(self):
        with unittest.mock.patch.object(builtins, 'input', lambda _: '1'):
            bankroll = Bankroll(50)
            bet = main.prompt_for_bet(bankroll)
            self.assertEqual(1, bet.amount)
            self.assertEqual(49, bankroll.amount)

    def test_prompt_hit(self):
        with unittest.mock.patch.object(builtins, 'input', lambda _: 'H'):
            self.assertTrue(main.prompt_hit_or_stay())

    def test_prompt_stay(self):
        with unittest.mock.patch.object(builtins, 'input', lambda _: 'S'):
            self.assertFalse(main.prompt_hit_or_stay())

    def test_format_hand(self):
        hand = build_hand([Card("Hearts", "Three"), Card("Diamonds", "Ace")])
        self.assertEqual("Three of Hearts, Ace of Diamonds", main.format_hand(hand))
        self.assertEqual("?, Ace of Diamonds", main.format_hand(hand, True))

    def test_player_turn_on_blackjack(self):
        with unittest.mock.patch.object(builtins, 'print', lambda output: self.assertEqual('Blackjack!', output)):
            hand = build_hand([Card("Spades", "Ace"), Card("Clubs", "King")])
            main.player_turn(Shoe(), hand)

    def test_dealer_doesnt_hit_hard_seventeen(self):
        hand = build_hand([Card("Spades", "Ten"), Card("Spades", "Seven")])
        self.assertFalse(main.dealer_hits(hand))

    def test_dealer_hits_soft_seventeen(self):
        hand = build_hand([Card("Spades", "Six"), Card("Spades", "Ace")])
        self.assertTrue(main.dealer_hits(hand))

    def test_dealer_hits_below_seventeen(self):
        hand = build_hand([Card("Spades", "Six"), Card("Spades", "Ten")])
        self.assertTrue(main.dealer_hits(hand))

    def test_dealer_doesnt_hit_above_seventeen(self):
        hand = build_hand([Card("Spades", "Eight"), Card("Spades", "Ten")])

    def test_dealer_hits_hard_seventeen(self):
        hand = build_hand([Card("Spades", "Ten"), Card("Spades", "Seven")])
        self.assertFalse(main.dealer_hits(hand))

    def test_return_cards(self):
        shoe = Shoe()
        hand = Hand()
        hand.add(shoe.draw())
        main.return_cards(shoe, (hand,))
        self.assertEqual(len(shoe.cards), 52)
        self.assertEqual(len(hand.cards), 0)

    def test_settle_bet_tied_blackjack(self):
        player = main.Player()
        player.bet = Bet(10)
        player.bankroll = Bankroll(20)
        player.hand = build_hand([Card("Clubs", "Ace"), Card("Clubs", "Queen")])
        dealer_hand = build_hand([Card("Clubs", "Ace"), Card("Clubs", "Queen")])
        main.settle_bet(player, dealer_hand)
        self.assertEqual(player.bankroll.amount, 30)  # get back the 10

    def test_settle_bet_player_blackjack(self):
        player = main.Player()
        player.bet = Bet(10)
        player.bankroll = Bankroll(20)
        player.hand = build_hand([Card("Clubs", "Ace"), Card("Clubs", "Queen")])
        dealer_hand = build_hand([Card("Clubs", "Ace"), Card("Clubs", "Four")])
        main.settle_bet(player, dealer_hand)
        self.assertEqual(player.bankroll.amount, 45)  # get back the 10 and win 15 from 3-2 odds

    def test_settle_bet_player_wins(self):
        player = main.Player()
        player.bet = Bet(10)
        player.bankroll = Bankroll(20)
        player.hand = build_hand([Card("Clubs", "Ace"), Card("Clubs", "Nine")])
        dealer_hand = build_hand([Card("Clubs", "Ace"), Card("Clubs", "Four")])
        main.settle_bet(player, dealer_hand)
        self.assertEqual(player.bankroll.amount, 40)  # get back the 10 and win 10 from even odds

    def test_settle_bet_player_loses(self):
        player = main.Player()
        player.bet = Bet(10)
        player.bankroll = Bankroll(20)
        player.hand = build_hand([Card("Clubs", "Ace"), Card("Clubs", "Three")])
        dealer_hand = build_hand([Card("Clubs", "Ace"), Card("Clubs", "Four")])
        main.settle_bet(player, dealer_hand)
        self.assertEqual(player.bankroll.amount, 20)  # get back nothing


if __name__ == "__main__":
    unittest.main()
