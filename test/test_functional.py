import unittest

import server


class ServerTester(unittest.TestCase):
    def setup(self):
        server.app = Flask(__name__)
        server.app.secret_key = 'something_special'

    def tearDown(self):
        server.competitions = server.load_competitions()
        server.clubs = server.load_clubs()

    def test__happy__login(self):
        """
        Plot:
            A user logs in with a registered email
        Result:
            The welcome template is displayed with status 200
        """
        with server.app.test_client() as client:
            response = client.post("/showSummary", data={"email": "admin@irontemple.com"})
            self.assertEqual("200 OK", response.status)

            user = next((club for club in server.clubs if club["name"] == "Iron Temple"), None)
            self.assertTrue(user)

            response_str = response.data.decode("utf-8")
            self.assertIn(f"""Welcome, {user["email"]}""", response_str)
            self.assertIn(f"""Points available: {user["points"]}""", response_str)

            for expected_competition in server.competitions:
                self.assertIn(expected_competition["name"], response_str)
                self.assertIn(f"""Date: {expected_competition["date"]}""", response_str)
                if not expected_competition["is_past"]:
                    self.assertIn(f"""Number of Places: {expected_competition["numberOfPlaces"]}""", response_str)

    def test__sad__login(self):
        """
        Plot:
            A user logs in with a non registered email
        Result:
            An error message is displayed on the index template
        """
        with server.app.test_client() as client:
            response = client.post("/showSummary", data={"email": "stuff@mail.com"})
            self.assertEqual("200 OK", response.status)

    def test__happy__booking(self):
        """
        Plot:
            A logged in user wants to book a place for a competition
            Summary page is displayed showing the user's mail, number of points left and a competition list
            The user picks a competition
        Steps:
            Booking page is displayed asking the user for a number of places to book
            The user enters a number and clicks "book"
        Result:
            Summary page is displayed showing "Great-booking complete!" and updated number of points/competition list
        """
        with server.app.test_client() as client:
            response = client.get("/book/New%20Competition/Simply%20Lift")
            self.assertEqual("200 OK", response.status)

            competition = next(
                (competition for competition in server.competitions if competition["name"] == "New Competition"),
                None
            )
            self.assertTrue(competition)

            response_str = response.data.decode("utf-8")
            self.assertIn(competition["name"], response_str)
            self.assertIn(f"""Places available: {competition["numberOfPlaces"]}""", response_str)

            user = next((club for club in server.clubs if club['name'] == "Simply Lift"), None)
            self.assertTrue(user)

            expected_user_points = str(int(user["points"]) - 1)
            expected_competition_number_of_places = str(int(competition["numberOfPlaces"]) - 1)

            response = client.post(
                "/purchasePlaces",
                data=
                {
                    "competition": "New Competition",
                    "club": "Simply Lift",
                    "places": "1"
                }
            )

            response_str = response.data.decode("utf-8")
            self.assertIn(f"""Welcome, {user["email"]}""", response_str)
            self.assertIn("Great-booking complete!", response_str)
            self.assertEqual(expected_user_points, user["points"])
            self.assertIn(f"""Points available: {user["points"]}""", response_str)

            for expected_competition in server.competitions:
                self.assertIn(expected_competition["name"], response_str)
                self.assertIn(f"""Date: {expected_competition["date"]}""", response_str)
                if expected_competition["name"] == "Simply Lift":
                    self.assertEqual(expected_competition_number_of_places, expected_competition["numberOfPlaces"])
                self.assertIn(f"""Number of Places: {expected_competition["numberOfPlaces"]}""", response_str)

    def test__sad__booking__1(self):
        """
        Plot:
            A logged in user wants to book more  places for a competition than possible
            Summary page is displayed showing the user's mail, number of points left and a competition list
            The user picks a competition
        Steps:
            Booking page is displayed asking the user for a number of places to book
            The user enters a number (higher than possible) and clicks "book"
        Result:
            Summary page is displayed showing "Great-booking complete!" and updated number of points/competition list
        """
        with server.app.test_client() as client:
            response = client.get("/book/Spring%20Festival/Simply%20Lift")
            self.assertEqual("200 OK", response.status)

            competition = next(
                (competition for competition in server.competitions if competition["name"] == "Spring Festival"),
                None
            )
            self.assertTrue(competition)

            response_str = response.data.decode("utf-8")
            self.assertIn(competition["name"], response_str)
            self.assertIn(f"""Places available: {competition["numberOfPlaces"]}""", response_str)

            user = next((club for club in server.clubs if club['name'] == "Simply Lift"), None)
            self.assertTrue(user)

            expected_competition_number_of_places = competition["numberOfPlaces"]
            expected_user_points = user["points"]

            response = client.post(
                "/purchasePlaces",
                data=
                {
                    "competition": "Spring Festival",
                    "club": "Simply Lift",
                    "places": "26"
                }
            )

            response_str = response.data.decode("utf-8")
            self.assertIn(f"Cannot book more places than remaining ({expected_competition_number_of_places})", response_str)
            self.assertIn(f"Places available: {expected_competition_number_of_places}", response_str)
            self.assertIn(f"Club points: {expected_user_points}", response_str)

    def test__sad__booking__2(self):
        """
        Plot:
            A logged in user wants to book more  places for a competition than he has left
            Summary page is displayed showing the user's mail, number of points left and a competition list
            The user picks a competition
        Steps:
            Booking page is displayed asking the user for a number of places to book
            The user enters a number (higher than remaining points) and clicks "book"
        Result:
            Summary page is displayed showing "Great-booking complete!" and updated number of points/competition list
        """
        with server.app.test_client() as client:
            response = client.get("/book/Spring%20Festival/Simply%20Lift")
            self.assertEqual("200 OK", response.status)

            competition = next(
                (competition for competition in server.competitions if competition["name"] == "Spring Festival"),
                None
            )
            self.assertTrue(competition)

            response_str = response.data.decode("utf-8")
            self.assertIn(competition["name"], response_str)
            self.assertIn(f"""Places available: {competition["numberOfPlaces"]}""", response_str)

            user = next((club for club in server.clubs if club['name'] == "Simply Lift"), None)
            self.assertTrue(user)

            expected_competition_number_of_places = competition["numberOfPlaces"]
            expected_user_points = user["points"]

            response = client.post(
                "/purchasePlaces",
                data=
                {
                    "competition": "Spring Festival",
                    "club": "Simply Lift",
                    "places": "14"
                }
            )

            response_str = response.data.decode("utf-8")
            self.assertIn(f"Cannot book more places than points you have ({expected_user_points})", response_str)
            self.assertIn(f"Places available: {expected_competition_number_of_places}", response_str)
            self.assertIn(f"Club points: {expected_user_points}", response_str)

    def test__sad__booking__3(self):
        """
        Plot:
            A logged in user wants to book more  places for a competition than maximum allowed
            Summary page is displayed showing the user's mail, number of points left and a competition list
            The user picks a competition
        Steps:
            Booking page is displayed asking the user for a number of places to book
            The user enters a number (higher than maximum allowed) and clicks "book"
        Result:
            Summary page is displayed showing "Great-booking complete!" and updated number of points/competition list
        """
        with server.app.test_client() as client:
            response = client.get("/book/Spring%20Festival/Simply%20Lift")
            self.assertEqual("200 OK", response.status)

            competition = next(
                (competition for competition in server.competitions if competition["name"] == "Spring Festival"),
                None
            )
            self.assertTrue(competition)

            response_str = response.data.decode("utf-8")
            self.assertIn(competition["name"], response_str)
            self.assertIn(f"""Places available: {competition["numberOfPlaces"]}""", response_str)

            user = next((club for club in server.clubs if club['name'] == "Simply Lift"), None)
            self.assertTrue(user)

            expected_competition_number_of_places = competition["numberOfPlaces"]
            expected_user_points = user["points"]

            response = client.post(
                "/purchasePlaces",
                data=
                {
                    "competition": "Spring Festival",
                    "club": "Simply Lift",
                    "places": "26"
                }
            )

            response_str = response.data.decode("utf-8")
            self.assertIn(f"Cannot book more places than max limit ({expected_competition_number_of_places})", response_str)
            self.assertIn(f"Places available: {expected_competition_number_of_places}", response_str)
            self.assertIn(f"Club points: {expected_user_points}", response_str)


if __name__ == "__main__":
    unittest.main()
