from django.db import models
from django.contrib.auth.models import User
from typing import Dict, Any


class Store(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    image = models.ImageField(upload_to="stores", blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def to_dict(self: "Store") -> Dict[str, Any]:
        """Serialize the store to a dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "image": self.image.url if self.image else None,
        }

    def __str__(self: "Store") -> str:
        return f"Store: {self.name} by {self.user.username}"


# Create your models here.
class Dish(models.Model):
    id = models.AutoField(primary_key=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.BigIntegerField()
    description = models.CharField(max_length=1000)
    image = models.ImageField(upload_to="dishes", blank=True)
    is_available = models.BooleanField(default=True)

    def to_dict(self: "Dish") -> Dict[str, Any]:
        """Serialize the dish to a dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "description": self.description,
            "image": self.image.url if self.image else None,
            "is_available": self.is_available,
            "modifiers": [
                modifier.to_dict()
                for modifier in DishModifier.objects.filter(dish=self).all()
            ],
        }

    def __str__(self: "Dish") -> str:
        return f"Dish: {self.name} ({self.store})"


class DishModifier(models.Model):
    id = models.AutoField(primary_key=True)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.BigIntegerField()
    is_available = models.BooleanField(default=True)

    def to_dict(self: "DishModifier") -> Dict[str, Any]:
        """Serialize the dish modifier to a dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "is_available": self.is_available,
        }

    def __str__(self: "DishModifier") -> str:
        return f"DishModifier: {self.name} ({self.dish} in {self.dish.store})"


class Order(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField()
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    is_online = models.BooleanField()
    is_completed = models.BooleanField()

    def to_dict(self: "Order") -> Dict[str, Any]:
        """Serialize the order to a dictionary"""
        return {
            "id": self.id,
            "created_at": self.created_at.astimezone().isoformat(),
            "is_online": self.is_online,
            "is_completed": self.is_completed,
            "dishes": list(
                map(
                    lambda x: x.to_dict(),
                    OrderDishRelation.objects.filter(order=self).all(),
                )
            ),
        }

    def __str__(self: "Order") -> str:
        return f"Order: {self.id} ({self.store})"


class OrderDishRelation(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    modifiers = models.ManyToManyField(DishModifier)
    quantity = models.PositiveBigIntegerField()
    other_comments = models.CharField(max_length=1000)

    def to_dict(self: "OrderDishRelation") -> Dict[str, Any]:
        """Convert the relation to a dictionary"""
        return {
            "dish": self.dish.to_dict(),
            "quantity": self.quantity,
            "dish_modifiers": list(map(lambda x: x.to_dict(), self.modifiers.all())),
        }

    def __str__(self: "OrderDishRelation") -> str:
        return f"OrderDishRelation: {self.dish} ({self.order})"
