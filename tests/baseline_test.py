import unittest

class TestMathOperations(unittest.TestCase):

    def test_addition(self):
        self.assertEqual(1 + 1, 2)
        self.assertEqual(-1 + 1, 0)
        self.assertEqual(-1 + -1, -2)

    def test_subtraction(self):
        self.assertEqual(2 - 1, 1)
        self.assertEqual(-1 - 1, -2)
        self.assertEqual(-1 - -1, 0)

    def test_multiplication(self):
        self.assertEqual(2 * 3, 6)
        self.assertEqual(-1 * 1, -1)
        self.assertEqual(-1 * -1, 1)
