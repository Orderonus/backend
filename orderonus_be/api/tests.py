from datetime import timedelta
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Order, Dish, DishModifier


# Create your tests here.
class GetOrdersTest(TestCase):
    def setUp(self: "GetOrdersTest") -> None:
        self.maxDiff = None
        now = timezone.now()
        self.physical_order = Order.objects.create(
            name="Physical Order",
            isOnline=False,
            isCompleted=False,
            created_at=now - timedelta(minutes=2),
        )

        self.online_order = Order.objects.create(
            name="Online Order",
            isOnline=True,
            isCompleted=False,
            created_at=now - timedelta(minutes=1),
        )

        self.completed_order = Order.objects.create(
            name="Completed Order",
            isOnline=True,
            isCompleted=True,
            created_at=now - timedelta(minutes=4),
        )

        self.old_order = Order.objects.create(
            name="Old Order",
            isOnline=True,
            isCompleted=True,
            created_at=now - timedelta(days=1),
        )

        self.password = "password"
        self.username = "username"

        self.user1 = User.objects.create_user(
            username=self.username, password=self.password
        )
        self.user1.save()

        return super().setUp()

    def login(self: "GetOrdersTest") -> bool:
        """Log in as the user"""
        return self.client.login(username=self.username, password=self.password)

    def tearDown(self: "GetOrdersTest") -> None:
        return super().tearDown()

    def save_all_orders(self) -> None:
        """Add the orders to the db"""
        self.old_order.save()
        self.online_order.save()
        self.physical_order.save()
        self.completed_order.save()

    def test_not_logged_in_fail(self: "GetOrdersTest") -> None:
        """Check if users who are not logged in cannot see the orders"""
        response = self.client.get("/api/orders/")
        self.assertEqual(response.status_code, 302)

    def test_retrieve_orders_success(self: "GetOrdersTest") -> None:
        """Check if the correct orders are shown"""
        self.assertTrue(self.login(), "Login failed")
        response = self.client.get("/api/orders/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "data": [
                    self.completed_order.to_dict(),
                    self.physical_order.to_dict(),
                    self.online_order.to_dict(),
                ]
            },
        )


class GetDishTest(TestCase):

    def setUp(self) -> None:

        # Create dish 1
        self.name = "rawoman"
        self.price = 10000
        self.description = "A bowl of rawoman"
        self.dish = Dish.objects.create(
            name=self.name, price=self.price, description=self.description
        )
        self.dish.save()

        # Create dish 2
        self.name2 = "ramen"
        self.price2 = 10000
        self.description2 = "A bowl of ramen"
        self.dish2 = Dish.objects.create(
            name=self.name2, price=self.price2, description=self.description2
        )

        # Create dish 2 modifier
        self.modifier_name = "Extra Noodles"
        self.modifier_price = 1000
        self.modifier_description = "Extra Noodles"
        self.modifier = DishModifier.objects.create(
            dish=self.dish2,
            name=self.modifier_name,
            price=self.modifier_price,
            is_available=True,
        )

        self.dish.save()
        self.dish2.save()
        self.modifier.save()

        self.password = "password"
        self.username = "username"

        self.user1 = User.objects.create_user(
            username=self.username, password=self.password
        )
        self.user1.save()
        return super().setUp()

    def tearDown(self) -> None:
        Dish.objects.all().delete()
        DishModifier.objects.all().delete()
        User.objects.all().delete()
        return super().tearDown()

    def login(self) -> bool:
        """Login as the user"""
        return self.client.login(username=self.username, password=self.password)

    def test_get_all_dishes_fail_no_login(self) -> None:
        """Check if users who are not logged in cannot see the dishes"""
        response = self.client.get("/api/get_dishes/")
        self.assertEqual(response.status_code, 302)

    def test_get_all_dishes_success(self) -> None:
        """Check if the correct dishes are shown"""
        self.assertTrue(self.login(), "Login failed")
        response = self.client.get("/api/get_dishes/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "data": [
                    self.dish.to_dict(),
                    self.dish2.to_dict(),
                ]
            },
        )


class AddDishTest(TestCase):
    def setUp(self) -> None:
        self.name = "ramen"
        self.price = 10000
        self.description = "A bowl of ramen"
        self.dish = Dish.objects.create(
            name=self.name, price=self.price, description=self.description
        )
        self.dish.save()

        self.password = "password"
        self.username = "username"

        self.user1 = User.objects.create_user(
            username=self.username, password=self.password
        )
        self.user1.save()
        return super().setUp()

    def login(self) -> bool:
        """Log in as the user"""
        return self.client.login(username=self.username, password=self.password)

    def tearDown(self) -> None:
        Dish.objects.all().delete()
        return super().tearDown()

    def test_dish_to_dict(self) -> None:
        """Test the to_dict method of the dish"""
        self.assertEqual(
            self.dish.to_dict(),
            {
                "name": self.name,
                "price": self.price,
                "description": self.description,
                "id": self.dish.id,
                "modifiers": [],
                "is_available": True,
                "image": None,
            },
        )

    def test_add_dish_fail_no_login(self) -> None:
        """Test if adding a dish fails when not logged in"""
        response = self.client.post("/api/add_dishes/")
        self.assertEqual(response.status_code, 302)

    def test_add_dish_fail_same_name(self) -> None:
        """Test if adding a dish fails when the name already exists"""
        self.assertTrue(self.login(), "Login failed")
        response = self.client.post(
            "/api/add_dishes/",
            {
                "name": self.name,
                "price": self.price,
                "description": self.description,
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {"error": "Dish already exists, please use a different name"},
        )

    def test_add_dish_sucess(self) -> None:
        """Test if adding a dish succeeds"""
        self.assertTrue(self.login(), "Login failed")
        response = self.client.post(
            "/api/add_dishes/",
            {
                "name": "new dish",
                "price": self.price,
                "description": self.description,
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"data": "Dish created successfully"})
        self.assertEqual(Dish.objects.count(), 2)

    def test_add_dish_with_modifiers_success(self) -> None:
        """Test if adding a dish with modifiers fails"""
        self.assertTrue(self.login(), "Login failed")
        response = self.client.post(
            "/api/add_dishes/",
            {
                "name": "new dish",
                "price": self.price,
                "description": self.description,
                "modifiers": [
                    {
                        "name": "spicy",
                        "price": 1000,
                        "is_available": True,
                    },
                    {
                        "name": "not spicy",
                        "price": 1000,
                        "is_available": True,
                    },
                ],
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"data": "Dish created successfully"})
        self.assertEqual(Dish.objects.count(), 2)
        self.assertEqual(DishModifier.objects.count(), 2)
