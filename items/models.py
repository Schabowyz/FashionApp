from django.db import models

import os
from uuid import uuid4


def path_and_rename(self, filename):
    upload_to = "images"
    ext = filename.split(".")[-1]
    filename = f"{uuid4().hex}.{ext}"
    return os.path.join(upload_to, filename)


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
    description = models.CharField(max_length=2048)
    image = models.ImageField(upload_to=path_and_rename)
    visibility = models.BooleanField(default=True)
    current_price = models.FloatField(default=0)