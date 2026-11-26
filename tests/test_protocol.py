import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "laptop"))
from protocol import Reading, parse_reading
from sources import DemoSource


class ProtocolTests(unittest.TestCase):
    def test_data(self):
        self.assertEqual(parse_reading("DATA,1,12345,840000,-315\n"),
                         Reading(1, 12345, 840000, -315))

    def test_multiple_sensor_ids(self):
        self.assertEqual(parse_reading("DATA,2,25,-20,3").sensor_id, 2)

    def test_status_ignored(self):
        self.assertIsNone(parse_reading("#EVENT,ZERO_BEGIN"))

    def test_invalid_data_ignored(self):
        for raw in ("", "DATA,1,123", "DATA,0,99,1,1", "DATA,x,1,2,3",
                    "DATA,1,-1,2,3", "DATA,1,2,3,4,5"):
            self.assertIsNone(parse_reading(raw))

    def test_demo_outputs_readings(self):
        demo = DemoSource()
        messages = demo.poll()
        self.assertEqual({m.sensor_id for m in messages}, {1, 2})
        demo.zero()
        self.assertIn("DEMO", demo.status)


if __name__ == "__main__":
    unittest.main()
