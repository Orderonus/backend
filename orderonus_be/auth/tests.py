from django.test import TestCase
from django.contrib.auth.models import User


# Create your tests here.
class LoginTest(TestCase):
    def setUp(self) -> None:
        """Set up the test"""
        self.username = "test"
        self.email = "test@test.com"
        self.password = "test"

        self.user = User.objects.create_user(self.username, self.email, self.password)
        self.user.save()
        return super().setUp()

    def tearDown(self) -> None:
        """Tear down the test"""
        self.user.delete()
        return super().tearDown()

    def test_login_fail_method_not_allowed(self: "LoginTest") -> None:
        """Check if a different method can access the api"""
        response = self.client.get("/auth/login/")
        self.assertEqual(response.status_code, 405, response.content)

    def test_login_fail_no_username(self: "LoginTest") -> None:
        """Check if the login fails if there is no username"""
        response = self.client.post("/auth/login/", {"password": self.password})
        self.assertEqual(response.status_code, 400, response.content)
        self.assertEqual(
            response.json(), {"message": "Username or password not provided"}
        )

    def test_login_fail_no_password(self: "LoginTest") -> None:
        """Check if the login fails if there is no password"""
        response = self.client.post("/auth/login/", {"username": self.username})
        self.assertEqual(response.status_code, 400, response.content)
        self.assertEqual(
            response.json(), {"message": "Username or password not provided"}
        )

    def test_login_fail_user_does_not_exist(self: "LoginTest") -> None:
        """Check if the login fails correctly if the user does not exist"""
        response = self.client.post(
            "/auth/login/", {"username": "test2", "password": self.password}
        )
        self.assertEqual(response.status_code, 404, response.content)
        self.assertEqual(
            response.json(), {"message": "User does not exist or Password is incorrect"}
        )

    def test_login_fail_user_password_incorrect(self: "LoginTest") -> None:
        """Check if the login fails correctly if the user password is wrong"""
        response = self.client.post(
            "/auth/login/", {"username": self.username, "password": "test2"}
        )
        self.assertEqual(response.status_code, 404, response.content)
        self.assertEqual(
            response.json(), {"message": "User does not exist or Password is incorrect"}
        )

    def test_login_success(self: "LoginTest") -> None:
        """Check if the login works"""
        response = self.client.post(
            "/auth/login/", {"username": self.username, "password": self.password}
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json(), {"message": "User logged in successfully"})


class RegisterTest(TestCase):
    def setUp(self) -> None:
        """Set up the test"""
        self.username = "test"
        self.email = "test@test.com"
        self.password = "test"

        self.user = User.objects.create_user(self.username, self.email, self.password)
        self.user.save()
        return super().setUp()

    def test_register_fail_duplicate_username(self: "RegisterTest") -> None:
        """Test if the registration fails if there is a duplicated username"""
        response = self.client.post(
            "/auth/register/", {"username": self.username, "password": "1234"}
        )
        self.assertEqual(response.status_code, 409, response.content)
        self.assertEqual(response.json(), {"message": "User already exists"})

    def test_register_fail_method_not_allowed(self: "RegisterTest") -> None:
        """Test if the registration fails if the method is incorrect"""
        response = self.client.get("/auth/register/")
        self.assertEqual(response.status_code, 405, response.content)

    def test_register_fail_no_username(self: "RegisterTest") -> None:
        """Test if the registration fails if there is no username"""
        response = self.client.post("/auth/register/", {"password": "1234"})
        self.assertEqual(response.status_code, 400, response.content)
        self.assertEqual(
            response.json(), {"message": "Username or password not provided"}
        )

    def test_register_fail_no_password(self: "RegisterTest") -> None:
        response = self.client.post("/auth/register/", {"username": "test"})
        self.assertEqual(response.status_code, 400, response.content)
        self.assertEqual(
            response.json(), {"message": "Username or password not provided"}
        )

    def test_register_success(self: "RegisterTest") -> None:
        """Check if the register works"""
        username = "test2"
        password = "password"
        response = self.client.post(
            "/auth/register/", {"username": username, "password": password}
        )
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(response.json(), {"message": "User created successfully"})
