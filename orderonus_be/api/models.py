from django.db import models
from typing import Dict, Any


# Create your models here.
class Dish(models.Model):
    id = models.AutoField(primary_key=True)
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


class DishModifier(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.BigIntegerField()
    is_available = models.BooleanField(default=True)

    def to_dict(self: "DishModifier") -> Dict[str, Any]:
        """Serialize the dish modifier to a dictionary"""
        return {
            "name": self.name,
            "price": self.price,
            "is_available": self.is_available,
        }


class Order(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField()
    name = models.CharField(max_length=100)
    isOnline = models.BooleanField()
    isCompleted = models.BooleanField()  # IsComplete / AtKitchen

    def to_dict(self: "Order") -> Dict[str, Any]:
        """Serialize the order to a dictionary"""
        return {
            "id": self.id,
            "created_at": self.created_at.astimezone().isoformat(),
            "name": self.name,
            "isOnline": self.isOnline,
            "isCompleted": self.isCompleted,
        }


class OrderDishRelation(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    dish_modifiers = models.ManyToManyField(DishModifier)

    def to_dict(self: "OrderDishRelation") -> Dict[str, Any]:
        """Convert the relation to a dictionary"""
        return {
            "dish": self.dish.to_dict(),
            "order": self.order.to_dict(),
        }
