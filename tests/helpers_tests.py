import unittest
from calculator.helpers import parse_share_string, multiply_shares, add_shares

class HelpersTestCase(unittest.TestCase):
    def test_parse_share_string_empty(self):
        self.assertEqual(parse_share_string(''), (0.0, 0.0, 0.0))
        self.assertEqual(parse_share_string('%'), (0.0, 0.0, 0.0))
    
    def test_parse_share_string_exact(self):
        self.assertEqual(parse_share_string('50%'), (0.5, 0.5, 0.5))
        self.assertEqual(parse_share_string('0%'), (0.0, 0.0, 0.0))
        self.assertEqual(parse_share_string('100%'), (1.0, 1.0, 1.0))
    
    def test_parse_share_string_range(self):
        self.assertEqual(parse_share_string('10-20%'), (0.1, 0.15, 0.2))
        self.assertEqual(parse_share_string('0-100%'), (0.0, 0.5, 1.0))
        # Test auto-correction of reversed ranges
        self.assertEqual(parse_share_string('20-10%'), (0.1, 0.15, 0.2))
    
    def test_parse_share_string_less_than(self):
        self.assertEqual(parse_share_string('<10%'), (0.0, 0.05, 0.1))
        self.assertEqual(parse_share_string('<50%'), (0.0, 0.25, 0.5))
    
    def test_parse_share_string_malformed(self):
        self.assertEqual(parse_share_string('10-20-30%'), (0.0, 0.0, 0.0))
        self.assertEqual(parse_share_string('abc%'), (0.0, 0.0, 0.0))
        self.assertEqual(parse_share_string('<abc%'), (0.0, 0.0, 0.0))
        self.assertEqual(parse_share_string('10-abc%'), (0.0, 0.0, 0.0))
    
    def test_multiply_shares(self):
        # Basic multiplication
        self.assertEqual(
            multiply_shares((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
            (0.25, 0.25, 0.25)
        )
        
        # Multiplication with ranges
        self.assertEqual(
            multiply_shares((0.1, 0.15, 0.2), (0.3, 0.4, 0.5)),
            (0.03, 0.065, 0.1)
        )
    
    def test_add_shares(self):
        # Basic addition
        self.assertEqual(
            add_shares((0.3, 0.3, 0.3), (0.2, 0.2, 0.2)),
            (0.5, 0.5, 0.5)
        )
        
        # Addition with ranges
        self.assertEqual(
            add_shares((0.1, 0.15, 0.2), (0.3, 0.35, 0.4)),
            (0.4, 0.5, 0.6)
        )
        
        # Addition exceeding 100% (should be clamped)
        self.assertEqual(
            add_shares((0.6, 0.6, 0.6), (0.6, 0.6, 0.6)),
            (1.0, 1.0, 1.0)
        )
        
        # Addition with one value exceeding 100%
        self.assertEqual(
            add_shares((0.7, 0.8, 0.9), (0.2, 0.3, 0.4)),
            (0.9, 0.95, 1.0)
        )

if __name__ == '__main__':
    unittest.main()