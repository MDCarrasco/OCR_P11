import datetime
import unittest
from unittest.mock import patch
from unittest.mock import mock_open

import server


class ServerTester(unittest.TestCase):
    """
    """

    CLUBS = """{
        "clubs":
            [
                {
                    "name": "club1",
                    "email": "club1@mail.com",
                    "points": "2"
                },
                {
                    "name": "club2",
                    "email": "club2@mail.com",
                    "points": "20"
                }
            ]
    }"""

    @patch("builtins.open", new_callable=mock_open, read_data=CLUBS)
    def test__load_clubs(self, _):
        expected_output = [
            {
                "name": "club1",
                "email": "club1@mail.com",
                "points": "2"
            },
            {
                "name": "club2",
                "email": "club2@mail.com",
                "points": "20"
            }
        ]
        output = server.load_clubs()
        self.assertEqual(expected_output, output)

    COMPETITIONS = """{
        "competitions":
            [
                {
                    "name": "competition1",
                    "date": "2020-03-27 10:00:00",
                    "numberOfPlaces": "21"
                },
                {
                    "name": "competition2",
                    "date": "2020-04-27 11:00:00",
                    "numberOfPlaces": "22"
                },
                {
                    "name": "competition2",
                    "date": "2022-12-27 11:00:00",
                    "numberOfPlaces": "23"
                }
            ]
    }"""

    @patch("builtins.open", new_callable=mock_open, read_data=COMPETITIONS)
    def test__load_competitions(self, _):
        expected_output = [
            {
                "name": "competition1",
                "date": datetime.datetime(2020, 3, 27, 10, 0),
                "numberOfPlaces": "21",
                "is_past": True
            },
            {

                "name": "competition2",
                "date": datetime.datetime(2020, 4, 27, 11, 0),
                "numberOfPlaces": "22",
                "is_past": True
        },
            {

                "name": "competition2",
                "date": datetime.datetime(2022, 12, 27, 11, 0),
                "numberOfPlaces": "23",
                "is_past": False
        }
        ]
        output = server.load_competitions()
        self.assertEqual(expected_output, output)


if __name__ == "__main__":
    unittest.main()
