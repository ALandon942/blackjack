import unittest
from main import Card


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


if __name__ == "__main__":
    unittest.main()
