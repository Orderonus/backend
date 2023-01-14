from django.db import models

# Create your models here.
class Dish(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    price = models.BigIntegerField()
    description = models.CharField(max_length=1000)
    image = models.ImageField()
    is_available = models.BooleanField(default=True)


class DishModifieres(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.BigIntegerField()


class Order(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100)
    type = models.IntegerField()
    status = models.IntegerField() #IsComplete / AtKitchen

class OrderDishRelation(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    dish_modifiers = models.ManyToManyField(DishModifieres)
