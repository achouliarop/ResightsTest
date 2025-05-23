import unittest
from calculator.calculator import calculate_real_shares

class CalculatorTestCase(unittest.TestCase):
    def test_simple_ownership_no_cycles(self):
        # C2 -> C1 -> FC
        # C2 owns 70% of C1, C1 owns 50% of FC
        # Expected: C2's real ownership in FC is 70% * 50% = 35%
        network = [
            {
                "id": "C1_FC",
                "source": 111,
                "source_name": "C1",
                "source_depth": 1,
                "target": 0,
                "target_name": "FC",
                "target_depth": 0,
                "share": "50%",
                "real_lower_share": None,
                "real_average_share": None,
                "real_upper_share": None,
                "active": True
            },
            {
                "id": "C2_C1",
                "source": 222,
                "source_name": "C2",
                "source_depth": 2,
                "target": 111,
                "target_name": "C1",
                "target_depth": 1,
                "share": "70%",
                "real_lower_share": None,
                "real_average_share": None,
                "real_upper_share": None,
                "active": True
            },
            {
                "id": "C3_C2",
                "source": 333,
                "source_name": "C3",
                "source_depth": 3,
                "target": 222,
                "target_name": "C2",
                "target_depth": 2,
                "share": "50%",
                "real_lower_share": None,
                "real_average_share": None,
                "real_upper_share": None,
                "active": False
            }
        ]
        
        result = calculate_real_shares(network)
        
        # Check C1's ownership (direct 50%)
        c1_edge = next(edge for edge in result if edge["id"] == "C1_FC")
        self.assertAlmostEqual(c1_edge["real_lower_share"], 50.0)
        self.assertAlmostEqual(c1_edge["real_average_share"], 50.0)
        self.assertAlmostEqual(c1_edge["real_upper_share"], 50.0)
        
        # Check C2's ownership (indirect 35%)
        c2_edge = next(edge for edge in result if edge["id"] == "C2_C1")
        self.assertAlmostEqual(c2_edge["real_lower_share"], 35.0)
        self.assertAlmostEqual(c2_edge["real_average_share"], 35.0)
        self.assertAlmostEqual(c2_edge["real_upper_share"], 35.0)
    
    def test_range_based_shares_no_cycles(self):
        network = [
            {
                "id": "C1_FC",
                "source": 111,
                "source_name": "C1",
                "source_depth": 1,
                "target": 0,
                "target_name": "FC",
                "target_depth": 0,
                "share": "10-20%",
                "real_lower_share": None,
                "real_average_share": None,
                "real_upper_share": None,
                "active": True
            },
            {
                "id": "C2_FC",
                "source": 222,
                "source_name": "C2",
                "source_depth": 1,
                "target": 0,
                "target_name": "FC",
                "target_depth": 0,
                "share": "<30%",
                "real_lower_share": None,
                "real_average_share": None,
                "real_upper_share": None,
                "active": True
            }
        ]
        
        result = calculate_real_shares(network)
        
        # Check C1's ownership (10-20%)
        c1_edge = next(edge for edge in result if edge["id"] == "C1_FC")
        self.assertAlmostEqual(c1_edge["real_lower_share"], 10.0)
        self.assertAlmostEqual(c1_edge["real_average_share"], 15.0)
        self.assertAlmostEqual(c1_edge["real_upper_share"], 20.0)
        
        # Check C2's ownership (<30%)
        c2_edge = next(edge for edge in result if edge["id"] == "C2_FC")
        self.assertAlmostEqual(c2_edge["real_lower_share"], 0.0)
        self.assertAlmostEqual(c2_edge["real_average_share"], 15.0)
        self.assertAlmostEqual(c2_edge["real_upper_share"], 30.0)

    def test_downstream_ownership(self):
        # S1 owns 25% of S2
        # FC owns 50% of S1
        # Expected: S1 is owned 50% from FC, S2 is owned 12.5% from FC

        network = [
            {
                "id": "444_555",
                "source": 444,
                "source_name": "S1",
                "source_depth": -1,
                "target": 555,
                "target_name": "S2",
                "target_depth": -2,
                "share": "25%",
                "real_lower_share": None,
                "real_average_share": None,
                "real_upper_share": None,
                "active": True
            },
            {
                "id": "0_444",
                "source": 0,
                "source_name": "FC",
                "source_depth": 0,
                "target": 444,
                "target_name": "S1",
                "target_depth": -1,
                "share": "50%",
                "real_lower_share": None,
                "real_average_share": None,
                "real_upper_share": None,
                "active": True
            }
        ]

        result = calculate_real_shares(network)

        s1_fc_edge = next(edge for edge in result if edge["id"] == "0_444")
        self.assertAlmostEqual(s1_fc_edge["real_lower_share"], 50.0)
        self.assertAlmostEqual(s1_fc_edge["real_average_share"], 50.0)
        self.assertAlmostEqual(s1_fc_edge["real_upper_share"], 50.0)

        s2_fc_edge = next(edge for edge in result if edge["id"] == "444_555")
        self.assertAlmostEqual(s2_fc_edge["real_lower_share"], 12.5)
        self.assertAlmostEqual(s2_fc_edge["real_average_share"], 12.5)
        self.assertAlmostEqual(s2_fc_edge["real_upper_share"], 12.5)

    def test_ownership_through_multiple_parallel_paths(self):
        # C1 owns 50% of FC
        # C2 owns 25% of C1
        # C3 owns 10% of C1 and 5% of C2
        # Expected: C1 owns 50% of FC, C2 owns 12.5% of FC, C3 owns 5% of FC through C1 and 0.63% of FC through C2
        network = [
            {
                "id": "C1_FC",
                "source": 111,
                "source_name": "C1",
                "source_depth": 1,
                "target": 0,
                "target_name": "FC",
                "target_depth": 0,
                "share": "50%",
                "real_lower_share": None,
                "real_average_share": None,
                "real_upper_share": None,
                "active": True
            },
            {
                "id": "C2_C1",
                "source": 222,
                "source_name": "C2",
                "source_depth": 2,
                "target": 111,
                "target_name": "C1",
                "target_depth": 1,
                "share": "25%",
                "real_lower_share": None,
                "real_average_share": None,
                "real_upper_share": None,
                "active": True
            },
            {
                "id": "C3_C1",
                "source": 333,
                "source_name": "C3",
                "source_depth": 2,
                "target": 111,
                "target_name": "C1",
                "target_depth": 1,
                "share": "10%",
                "real_lower_share": None,
                "real_average_share": None,
                "real_upper_share": None,
                "active": True
            },
            {
                "id": "C3_C2",
                "source": 333,
                "source_name": "C3",
                "source_depth": 3,
                "target": 222,
                "target_name": "C2",
                "target_depth": 2,
                "share": "5%",
                "real_lower_share": None,
                "real_average_share": None,
                "real_upper_share": None,
                "active": True
            }
        ]

        result = calculate_real_shares(network)

        c1_fc_edge = next(edge for edge in result if edge["id"] == "C1_FC")
        self.assertAlmostEqual(c1_fc_edge["real_lower_share"], 50.0)
        self.assertAlmostEqual(c1_fc_edge["real_average_share"], 50.0)
        self.assertAlmostEqual(c1_fc_edge["real_upper_share"], 50.0)

        c2_fc_edge = next(edge for edge in result if edge["id"] == "C2_C1")
        self.assertAlmostEqual(c2_fc_edge["real_lower_share"], 12.5)
        self.assertAlmostEqual(c2_fc_edge["real_average_share"], 12.5)
        self.assertAlmostEqual(c2_fc_edge["real_upper_share"], 12.5)

        c3_fc_edge = next(edge for edge in result if edge["id"] == "C3_C1")
        self.assertAlmostEqual(c3_fc_edge["real_lower_share"], 5.62, places=1)
        self.assertAlmostEqual(c3_fc_edge["real_average_share"], 5.62, places=1)
        self.assertAlmostEqual(c3_fc_edge["real_upper_share"], 5.62, places=1)

        c3_from_c2_fc_edge = next(edge for edge in result if edge["id"] == "C3_C2")
        self.assertAlmostEqual(c3_from_c2_fc_edge["real_lower_share"], 5.62, places=1)
        self.assertAlmostEqual(c3_from_c2_fc_edge["real_average_share"], 5.62, places=1)
        self.assertAlmostEqual(c3_from_c2_fc_edge["real_upper_share"], 5.62, places=1)
       
    def test_complex_ownership_with_cycles(self):
        # C1 owns 50% of FC, C1 owns 10% of C2
        # C2 owns 5% of C1
        # Expected after convergence: C1 owns 50.25% of FC, C2 owns 2.51% of FC
        network = [
            {
                "id": "C1_FC",
                "source": 111,
                "source_name": "C1",
                "source_depth": 1,
                "target": 0,
                "target_name": "FC",
                "target_depth": 0,
                "share": "50%",
                "real_lower_share": None,
                "real_average_share": None,
                "real_upper_share": None,
                "active": True
            },
            {
                "id": "C2_C1",
                "source": 222,
                "source_name": "C2",
                "source_depth": 2,
                "target": 111,
                "target_name": "C1",
                "target_depth": 1,
                "share": "5%",
                "real_lower_share": None,
                "real_average_share": None,
                "real_upper_share": None,
                "active": True
            },
            {
                "id": "C1_C2",
                "source": 111,
                "source_name": "C1",
                "source_depth": 3,
                "target": 222,
                "target_name": "C2",
                "target_depth": 2,
                "share": "10%",
                "real_lower_share": None,
                "real_average_share": None,
                "real_upper_share": None,
                "active": True
            }
        ]
        
        result = calculate_real_shares(network)
        
        c1_c2_edge = next(edge for edge in result if edge["id"] == "C1_C2")
        self.assertAlmostEqual(c1_c2_edge["real_lower_share"], 50.25)
        self.assertAlmostEqual(c1_c2_edge["real_average_share"], 50.25)
        self.assertAlmostEqual(c1_c2_edge["real_upper_share"], 50.25)

        c1_fc_edge = next(edge for edge in result if edge["id"] == "C1_FC")
        self.assertAlmostEqual(c1_fc_edge["real_lower_share"], 50.25)
        self.assertAlmostEqual(c1_fc_edge["real_average_share"], 50.25)
        self.assertAlmostEqual(c1_fc_edge["real_upper_share"], 50.25)
        
        c2_fc_edge = next(edge for edge in result if edge["id"] == "C2_C1")
        self.assertAlmostEqual(c2_fc_edge["real_lower_share"], 2.5, places=1)
        self.assertAlmostEqual(c2_fc_edge["real_average_share"], 2.5, places=1)
        self.assertAlmostEqual(c2_fc_edge["real_upper_share"], 2.5, places=1)

if __name__ == "__main__":
    unittest.main()