from django.test import TestCase


# Create your tests here.
class HomepageTest(TestCase):
    def test_homepage(self: "HomepageTest") -> None:
        """Check if the homepage returns a 200 status code"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Server is up and running"})
