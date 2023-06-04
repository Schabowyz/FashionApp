from django.db import models

# Create your models here.
class Item(models.Model):
    GENDERS = [
        ("male", "male"),
        ("female", "female"),
        ("unisex", "unisex")
    ]
    CATEGORIES = [
        ("shoes", "shoes"),
        ("legwear", "legwear"),
        ("pants", "pants"),
        ("shorts", "shorts"),
        ("skirt", "skirt"),
        ("t-shirt", "t-shirt"),
        ("shirt", "shirt"),
        ("dress", "dress"),
        ("hoodie", "hoodie"),
        ("jacket", "jacket"),
        ("headwear", "headwear"),
        ("gloves", "gloves")
    ]

    name = models.CharField(max_length=128)
    gender = models.CharField(choices=GENDERS, max_length=16)
    category = models.CharField(choices=CATEGORIES, max_length=16)
    description = models.CharField(max_length=512)
    quantity = models.IntegerField()
    image = models.ImageField(upload_to="images")
    visibility = models.BooleanField(default=True)

class Price(models.Model):
    item_id = models.ForeignKey(Item, on_delete=models.CASCADE)
    date = models.DateField()
    price = models.FloatField()