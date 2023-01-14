from datetime import timedelta
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Order, Dish, DishModifier, Store


# Create your tests here.
class LoginTestCase(TestCase):
    def setUp(self: "LoginTestCase") -> None:
        super().setUp()
        self.password = "password"
        self.username = "username"

        self.user1 = User.objects.create_user(
            username=self.username, password=self.password
        )
        self.user1.save()

    def tearDown(self: "LoginTestCase") -> None:
        User.objects.all().delete()
        return super().tearDown()

    def login(self: "LoginTestCase") -> bool:
        """Log in as the user"""
        return self.client.login(username=self.username, password=self.password)


class StoreTestCase(LoginTestCase):
    def setUp(self: "StoreTestCase") -> None:
        super().setUp()
        self.store_name = "Test Store"
        self.store_description = "Test Description"
        self.store = Store.objects.create(
            name=self.store_name,
            description=self.store_description,
            user=self.user1,
        )
        self.store.save()

    def tearDown(self: "StoreTestCase") -> None:
        Store.objects.all().delete()
        return super().tearDown()


class AddStoreTest(StoreTestCase):
    def test_add_store_fail_no_login(self: "AddStoreTest") -> None:
        """Test adding a store without logging in"""
        response = self.client.post(
            "/api/stores/add",
            {
                "name": self.store_name,
                "description": self.store_description,
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 302)

    def test_add_store_fail_same_name(self: "AddStoreTest") -> None:
        """Test adding a store"""
        self.assertTrue(self.login(), "Failed to log in")
        response = self.client.post(
            "/api/stores/add",
            {
                "name": self.store_name,
                "description": self.store_description,
            },
            content_type="application/json",
        )
        self.assertEqual(
            response.status_code,
            400,
            f"Suppose to not add store: {response.content}",
        )
        self.assertEqual(
            response.json(),
            {
                "error": "Store already exists",
            },
        )

    def test_add_store_fail_no_name(self) -> None:
        """Test adding a store"""
        self.assertTrue(self.login(), "Failed to log in")
        response = self.client.post(
            "/api/stores/add",
            {
                "description": self.store_description,
            },
            content_type="application/json",
        )
        self.assertEqual(
            response.status_code,
            400,
            f"Suppose to not add store: {response.content}",
        )
        self.assertEqual(
            response.json(),
            {
                "error": "Missing parameters",
            },
        )

    def test_add_store_success(self) -> None:
        """Test adding a store"""
        self.assertTrue(self.login(), "Failed to log in")
        response = self.client.post(
            "/api/stores/add",
            {
                "name": "New Store",
                "description": "New Description",
            },
            content_type="application/json",
        )
        self.assertEqual(
            response.status_code,
            200,
            f"Suppose to add store: {response.content}",
        )
        self.assertEqual(
            response.json(),
            {"data": "Store added successfully"},
        )


class GetStoreTest(StoreTestCase):
    def test_get_store_fail_no_login(self) -> None:
        """Test getting a store without logging in"""
        response = self.client.get(f"/api/stores/")
        self.assertEqual(response.status_code, 302, response.content)

    def test_get_store_fail_method_not_allowed(self) -> None:
        """Test getting a store without logging in"""
        self.assertTrue(self.login(), "Failed to log in")
        response = self.client.post(f"/api/stores/")
        self.assertEqual(response.status_code, 405, response.content)

    def test_get_store_success(self) -> None:
        """Test getting a store"""
        self.assertTrue(self.login(), "Failed to log in")
        response = self.client.get(f"/api/stores/")
        self.assertEqual(
            response.status_code,
            200,
            f"Suppose to get store: {response.content}",
        )
        self.assertEqual(
            response.json(),
            {
                "data": [
                    {
                        "id": self.store.id,
                        "name": self.store_name,
                        "description": self.store_description,
                        "image": None,
                    }
                ]
            },
        )


class GetOrdersTest(StoreTestCase):
    def setUp(self: "GetOrdersTest") -> None:
        super().setUp()
        now = timezone.now()
        self.physical_order = Order.objects.create(
            name="Physical Order",
            isOnline=False,
            isCompleted=False,
            created_at=now - timedelta(minutes=2),
            store=self.store,
        )

        self.online_order = Order.objects.create(
            name="Online Order",
            isOnline=True,
            isCompleted=False,
            created_at=now - timedelta(minutes=1),
            store=self.store,
        )

        self.completed_order = Order.objects.create(
            name="Completed Order",
            isOnline=True,
            isCompleted=True,
            created_at=now - timedelta(minutes=4),
            store=self.store,
        )

        self.old_order = Order.objects.create(
            name="Old Order",
            isOnline=True,
            isCompleted=True,
            created_at=now - timedelta(days=1),
            store=self.store,
        )

    def tearDown(self: "GetOrdersTest") -> None:
        Order.objects.all().delete()
        return super().tearDown()

    def save_all_orders(self) -> None:
        """Add the orders to the db"""
        self.old_order.save()
        self.online_order.save()
        self.physical_order.save()
        self.completed_order.save()

    def test_not_logged_in_fail(self: "GetOrdersTest") -> None:
        """Check if users who are not logged in cannot see the orders"""
        response = self.client.get(f"/api/stores/{self.store.id}/orders/")
        self.assertEqual(response.status_code, 302, response.content)

    def test_retrieve_orders_success(self: "GetOrdersTest") -> None:
        """Check if the correct orders are shown"""
        self.assertTrue(self.login(), "Login failed")
        response = self.client.get(f"/api/stores/{self.store.id}/orders/")
        self.assertEqual(response.status_code, 200, response.content)
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


class CompleteOrderTest(StoreTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.order = Order.objects.create(
            name="Order",
            isOnline=True,
            isCompleted=False,
            created_at=timezone.now(),
            store=self.store,
        )
        self.order.save()

    def tearDown(self) -> None:
        Order.objects.all().delete()
        return super().tearDown()

    def test_complete_order_fail_no_login(self) -> None:
        """Check if users who are not logged in cannot complete the order"""
        self.assertFalse(Order.objects.all().get().isCompleted)
        response = self.client.post(
            f"/api/stores/{self.store.id}/orders/{self.order.id}/complete",
            {
                "is_completed": True,
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 302)

    def test_complete_order_fail_order_does_not_exist(self) -> None:
        """Check if users who are logged in cannot complete an order that does not exist"""
        self.assertTrue(self.login(), "Login failed")
        response = self.client.post(
            f"/api/stores/{self.store.id}/orders/{self.order.id + 1}/complete",
            {
                "is_completed": True,
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)


class DishAvailableTest(StoreTestCase):
    def setUp(self: "DishAvailableTest") -> None:
        super().setUp()
        self.endpoint = f"/api/stores/{self.store.id}/dishes/{'{}'}/available"
        self.maxDiff = None

        self.dish = Dish.objects.create(
            name="Ramen",
            price=10000,
            description="A bowl of ramen",
            store=self.store,
        )

        self.dish.save()

    def tearDown(self) -> None:
        Dish.objects.all().delete()
        return super().tearDown()

    def test_update_available_fail_no_login(self) -> None:
        """Check if users who are not logged in cannot update the dish"""
        response = self.client.post(
            self.endpoint.format(self.dish.id),
            {"is_available": False},
        )
        self.assertEqual(response.status_code, 302)

    def test_update_available_fail_no_availability(self) -> None:
        """Check if users who are logged in cannot update a dish without specifying availability"""
        self.assertTrue(self.login(), "Login failed")
        response = self.client.post(
            self.endpoint.format(self.dish.id),
            {},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Missing parameter"})

    def test_update_available_fail_invalid_id(self) -> None:
        """Check if users who are logged in cannot update a dish with an invalid id"""
        self.assertTrue(self.login(), "Login failed")
        response = self.client.post(
            self.endpoint.format(self.dish.id + 1),
            {"is_available": False},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_update_available_success(self) -> None:
        """Check if users who are logged in can update the dish"""
        self.assertTrue(self.login(), "Login failed")
        self.assertTrue(Dish.objects.filter(id=self.dish.id).get().is_available)
        response = self.client.post(
            self.endpoint.format(self.dish.id),
            {"is_available": False},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"data": "Dish updated successfully"})

        self.assertFalse(Dish.objects.filter(id=self.dish.id).get().is_available)


class GetDishTest(StoreTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.endpoint = f"/api/stores/{self.store.id}/dishes/"

        # Create dish 1
        self.name = "rawoman"
        self.price = 10000
        self.description = "A bowl of rawoman"
        self.dish = Dish.objects.create(
            name=self.name,
            price=self.price,
            description=self.description,
            store=self.store,
        )
        self.dish.save()

        # Create dish 2
        self.name2 = "ramen"
        self.price2 = 10000
        self.description2 = "A bowl of ramen"
        self.dish2 = Dish.objects.create(
            name=self.name2,
            price=self.price2,
            description=self.description2,
            store=self.store,
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

    def tearDown(self) -> None:
        Dish.objects.all().delete()
        DishModifier.objects.all().delete()
        return super().tearDown()

    def test_get_all_dishes_fail_no_login(self) -> None:
        """Check if users who are not logged in cannot see the dishes"""
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 302)

    def test_get_all_dishes_success(self) -> None:
        """Check if the correct dishes are shown"""
        self.assertTrue(self.login(), "Login failed")
        response = self.client.get(self.endpoint)
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


class AddDishTest(StoreTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.endpoint = f"/api/stores/{self.store.id}/dishes/add"
        self.name = "ramen"
        self.price = 10000
        self.description = "A bowl of ramen"
        self.dish = Dish.objects.create(
            name=self.name,
            price=self.price,
            description=self.description,
            store=self.store,
        )
        self.dish.save()

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
        response = self.client.post(self.endpoint)
        self.assertEqual(response.status_code, 302)

    def test_add_dish_fail_same_name(self) -> None:
        """Test if adding a dish fails when the name already exists"""
        self.assertTrue(self.login(), "Login failed")
        response = self.client.post(
            self.endpoint,
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
            self.endpoint,
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
            self.endpoint,
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
