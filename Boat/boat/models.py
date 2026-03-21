import uuid

from django.db import models

# Create your models here.

class Keybind(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    action = models.CharField(max_length=255)
    key = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.action} - {self.key}'

class CurrentState(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    position_x = models.IntegerField(default=0)
    position_y = models.IntegerField(default=0)

    boisium = models.IntegerField(default=0)
    feronium = models.IntegerField(default=0)
    charbonium = models.IntegerField(default=0)
    gold = models.IntegerField(default=0)

    boat_level = models.IntegerField(default=1)
    remaining_movement = models.IntegerField(default=0)
    max_movement = models.IntegerField(default=15)

    def __str__(self):
        return f'Position: ({self.position_x}, {self.position_y})'

class Ship(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Case(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    x = models.IntegerField(default=0)
    y = models.IntegerField(default=0)
    type = models.CharField(max_length=255, default='')
    zone = models.IntegerField(default=0)

    ships = models.ManyToManyField(Ship, related_name='cases')

    def __str__(self):
        return f'({self.x}, {self.y}) - {self.type} - Zone {self.zone}'