from django.db import models


class Deck(models.Model):
    quantity = models.IntegerField()
    name = models.TextField()
    set_code = models.TextField()
    collector_number = models.TextField()

    def __str__(self):
        return f"{self.quantity} {self.name} ({self.set_code}) {self.collector_number}"


class Params(models.Model):
    random_basic_land_art = models.BooleanField()
    only_full_art_basic_lands = models.BooleanField()
    allow_duplicate_basic_lands = models.BooleanField()

    def __str__(self):
        return f"{self.random_basic_land_art} {self.only_full_art_basic_lands} {self.allow_duplicate_basic_lands}"


class Cards(models.Model):
    card = models.TextField()
