import unittest
import string
from app.utils import generate_invite_code

class TestUtils(unittest.TestCase):

    def test_generate_invite_code_length(self):
        code = generate_invite_code(8)
        self.assertEqual(len(code), 8)

    def test_generate_invite_code_default_length(self):
        code = generate_invite_code()
        self.assertEqual(len(code), 6)

    def test_generate_invite_code_characters(self):
        code = generate_invite_code(10)
        for char in code:
            self.assertIn(char, string.ascii_uppercase + string.digits)

    def test_generate_invite_code_unique(self):
        code1 = generate_invite_code()
        code2 = generate_invite_code()
        self.assertNotEqual(code1, code2)

if __name__ == '__main__':
    unittest.main()