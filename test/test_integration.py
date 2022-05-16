import unittest
from contextlib import contextmanager
from flask import template_rendered

import server


unittest.TestLoader.sortTestMethodsUsing = None


@contextmanager
def captured_templates(app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))
    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


class ServerTester(unittest.TestCase):
    def setup(self):
        server.app = Flask(__name__)
        server.app.secret_key = 'something_special'

    def tearDown(self):
        server.competitions = server.load_competitions()
        server.clubs = server.load_clubs()

    # ROUTES ------------------------------------------------------------------------
    def test__index_rendered(self):
        with server.app.test_client() as client:
            with captured_templates(server.app) as templates:
                client.get("/")
                template, _ = templates[0]
                expected_name = template.name
                self.assertEqual(expected_name, "index.html")

    def test__clubs_rendered(self):
        with server.app.test_client() as client:
            with captured_templates(server.app) as templates:
                client.get("/clubs")
                template, _ = templates[0]
                expected_name = template.name
                self.assertEqual(expected_name, "clubs.html")

    def test__show_summary__welcome_rendered(self):
        with server.app.test_client() as client:
            with captured_templates(server.app) as templates:
                client.post("/showSummary", data={"email": "admin@irontemple.com"})
                template, _ = templates[0]
                expected_name = template.name
                self.assertEqual(expected_name, "welcome.html")

    def test__book__booking_rendered(self):
        """
        booking.html is rendered if club name and competition name are found
        """
        with server.app.test_client() as client:
            with captured_templates(server.app) as templates:
                client.get("/book/Spring%20Festival/Simply%20Lift")
                template, _ = templates[0]
                expected_name = template.name
                self.assertEqual(expected_name, "booking.html")

    # This test does not pass !
    def test__book__welcome_rendered(self):
        """
        welcome.html is rendered if either club name or competition name is not found
        """
        with server.app.test_client() as client:
            with captured_templates(server.app) as templates:
                client.get("/book/competition_name/club_name")
                template, _ = templates[0]
                expected_name = template.name
                self.assertEqual(expected_name, "welcome.html")

    def test__purchase_places__welcome_rendered(self):
        """
        welcome.html is rendered upon purchasePlaces form sending
        """
        with server.app.test_client() as client:
            with captured_templates(server.app) as templates:
                client.post(
                    "/purchasePlaces",
                    data=
                    {
                        "competition": "Spring Festival",
                        "club": "Simply Lift",
                        "places": "1"
                    }
                )
                template, _ = templates[0]
                expected_name = template.name
                self.assertEqual(expected_name, "welcome.html")

    def test__logout__index_redirected(self):
        with server.app.test_client() as client:
            response = client.get("/logout")
            self.assertEqual("/", response.location)

    # CONTEXTS ----------------------------------------------------------------------
    def test__show_summary__club(self):
        """
        This test checks that render_template method is called within show_summary function with the right club
        """
        with server.app.test_client() as client:
            with captured_templates(server.app) as templates:
                client.post("/showSummary", data={"email": "admin@irontemple.com"})
                _, context = templates[0]
                expected_club = {
                    "name": "Iron Temple",
                    "email": "admin@irontemple.com",
                    "points": "4"
                }
                self.assertEqual(expected_club, context["club"])

    def test__show_summary__competitions(self):
        """
        This test checks that render_template method is called within show_summary function with the right competitions
        """
        with server.app.test_client() as client:
            with captured_templates(server.app) as templates:
                client.post("/showSummary", data={"email": "admin@irontemple.com"})
                _, context = templates[0]
                expected_competitions = [
                    {
                        "name": "Spring Festival",
                        "date": "2020-03-27 10:00:00",
                        "numberOfPlaces": "25"
                    },
                    {
                        "name": "Fall Classic",
                        "date": "2020-10-22 13:30:00",
                        "numberOfPlaces": "13"
                    }
                ]
                self.assertEqual(expected_competitions, context["competitions"])

    def test__book__club(self):
        """
        This test checks that render_template method is called within book function with the right club
        """
        with server.app.test_client() as client:
            with captured_templates(server.app) as templates:
                client.get("/book/Spring%20Festival/Simply%20Lift")
                _, context = templates[0]
                expected_club = {
                    "name": "Simply Lift",
                    "email": "john@simplylift.co",
                    "points": "13"
                }
                self.assertEqual(expected_club, context["club"])

    def test__book__competitions(self):
        """
        This test checks that render_template method is called within book function with the right competition
        """
        with server.app.test_client() as client:
            with captured_templates(server.app) as templates:
                client.get("/book/Spring%20Festival/Simply%20Lift")
                _, context = templates[0]
                expected_competition = {
                    "name": "Spring Festival",
                    "date": "2020-03-27 10:00:00",
                    "numberOfPlaces": "25"
                }
                self.assertEqual(expected_competition, context["competition"])

    def test__purchase_places__club(self):
        """
        This test checks that render_template method is called within purchase_places function with the right club
        """
        with server.app.test_client() as client:
            with captured_templates(server.app) as templates:
                client.post(
                    "/purchasePlaces",
                    data=
                    {
                        "competition": "Spring Festival",
                        "club": "Simply Lift",
                        "places": "1"
                    }
                )
                _, context = templates[0]
                expected_club = {
                    "name": "Simply Lift",
                    "email": "john@simplylift.co",
                    "points": "13"
                }
                self.assertEqual(expected_club, context["club"])

    # this fails because of inconsistency in numberOfPlaces type (int/str)
    def test__purchase_places__competitions(self):
        """
        This test checks that render_template method is called within purchase_places function with the right competitions
        it also checks if numberOfPlaces is updated after purchase
        """
        with server.app.test_client() as client:
            with captured_templates(server.app) as templates:
                client.post(
                    "/purchasePlaces",
                    data=
                    {
                        "competition": "Spring Festival",
                        "club": "Simply Lift",
                        "places": "1"
                    }
                )
                _, context = templates[0]
                expected_competitions = [
                    {
                        "name": "Spring Festival",
                        "date": "2020-03-27 10:00:00",
                        # one place booked in this test
                        "numberOfPlaces": "24"
                    },
                    {
                        "name": "Fall Classic",
                        "date": "2020-10-22 13:30:00",
                        "numberOfPlaces": "13"
                    }
                ]
                self.assertEqual(expected_competitions, context["competitions"])


if __name__ == "__main__":
    unittest.main()
