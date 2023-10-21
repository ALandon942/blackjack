import unittest
from main import Card, Shoe, Hand, LIMIT


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

    # Value of ace is tested with switch_value

    def test_switch_normal_card_value(self):
        normal_card = Card("Diamonds", "Two")
        value_before = normal_card.value()
        normal_card.switch_values()
        value_after = normal_card.value()
        self.assertEqual(value_before, value_after)

    def test_switch_ace_value(self):
        ace = Card("Clubs", "Ace")
        self.assertEqual(11, ace.value())
        ace.switch_values()
        self.assertEqual(1, ace.value())
        ace.switch_values()
        self.assertGreater(ace.value(), 1)  # switching extra mustn't undo a bust


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

    def test_hit(self):
        shoe = Shoe()
        full = len(shoe.cards)
        top_card = shoe.cards[0]
        dealt_card = shoe.hit()
        self.assertEqual((top_card.suit, top_card.rank), (dealt_card.suit, dealt_card.rank))
        self.assertEqual(full - 1, len(shoe.cards))

    def test_put_back(self):
        shoe = Shoe()
        full = len(shoe.cards)
        discard = []
        for i in range(0, 10):
            discard.append(shoe.hit())
        shoe.put_back(discard)
        self.assertEqual(full, len(shoe.cards))
        # not going to test reshuffling


class HandTest(unittest.TestCase):
    @staticmethod
    def build_hand(cards):
        hand = Hand()
        for card in cards:
            hand.add(card)
        return hand

    def test_init(self):
        hand = Hand()
        self.assertEqual(0, hand.total())
        self.assertFalse(hand.is_blackjack(), "Blackjack on empty hand!")
        self.assertFalse(hand.is_bust(), "Bust on empty hand!")

    def test_add_one(self):
        card = Card("Hearts", "Four")
        hand = self.build_hand((card,))
        self.assertEqual(card.value(), hand.total())
        self.assertFalse(hand.is_blackjack(), "Blackjack declared falsely")
        self.assertFalse(hand.is_bust(), "Bust reached prematurely")

    def test_blackjack(self):
        hand = self.build_hand([Card("Diamonds", "King"), Card("Spades", "Ace")])
        self.assertEqual(LIMIT, hand.total())
        self.assertTrue(hand.is_blackjack(), "Failed to detect blackjack")
        self.assertFalse(hand.is_bust(), "Blackjack mistaken for bust")

    def test_21_with_ace_switch(self):
        hand = self.build_hand(
            [Card("Diamonds", "Six"), Card("Spades", "Ace"), Card("Clubs", "Five"), Card("Diamonds", "Nine")])
        self.assertEqual(LIMIT, hand.total())
        self.assertFalse(hand.is_blackjack(), "Non-blackjack 21 mistaken for blackjack")
        self.assertFalse(hand.is_bust(), "21 mistaken for bust")

    def test_bust(self):
        hand = self.build_hand([Card("Diamonds", "Ten"), Card("Hearts", "Seven"), Card("Hearts", "Five")])
        self.assertGreater(hand.total(), LIMIT)
        self.assertFalse(hand.is_blackjack(), "Bust mistaken for blackjack")
        self.assertTrue(hand.is_bust(), "Failed to detect bust")

    def test_compare_one_blackjack(self):
        hand1 = self.build_hand([Card("Diamonds", "Ace"), Card("Diamonds", "King")])
        # Make the other hand a plain old 21 to assert that blackjack beats it:
        hand2 = self.build_hand([Card("Hearts", "Nine"), Card("Clubs", "Nine"), Card("Clubs", "Three")])
        self.assertGreater(hand1.compare(hand2), 0)
        self.assertLess(hand2.compare(hand1), 0)

    def test_compare_two_blackjacks(self):
        hand1 = self.build_hand([Card("Diamonds", "Ace"), Card("Diamonds", "King")])
        hand2 = self.build_hand([Card("Spades", "Ace"), Card("Clubs", "Ten")])
        self.assertEqual(0, hand1.compare(hand2))
        self.assertEqual(0, hand2.compare(hand1))

    def test_compare_one_bust(self):
        hand1 = self.build_hand([Card("Hearts", "Nine"), Card("Clubs", "Nine"), Card("Clubs", "Four")])
        hand2 = self.build_hand([Card("Hearts", "Four"), Card("Clubs", "Two")])
        self.assertLess(hand1.compare(hand2), 0)
        self.assertGreater(hand2.compare(hand1), 0)

    def test_compare_two_busts(self):
        hand1 = self.build_hand([Card("Hearts", "Nine"), Card("Clubs", "Nine"), Card("Clubs", "Four")])
        hand2 = self.build_hand([Card("Spades", "King"), Card("Spades", "Ten"), Card("Diamonds", "Six")])
        self.assertEqual(0, hand1.compare(hand2))
        self.assertEqual(0, hand2.compare(hand1))

    def test_compare_no_blackjack_or_bust(self):
        hand1 = self.build_hand([Card("Hearts", "Nine"), Card("Clubs", "Four")])
        hand2 = self.build_hand([Card("Spades", "King"), Card("Diamonds", "Six")])
        self.assertLess(hand1.compare(hand2), 0)
        self.assertGreater(hand2.compare(hand1), 0)
        self.assertEqual(0, hand1.compare(hand1))


if __name__ == "__main__":
    unittest.main()
