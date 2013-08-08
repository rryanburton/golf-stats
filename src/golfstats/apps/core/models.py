from django.db import models


class Course(models.Model):
    name = models.CharField(max_length=64)


class Hole(models.Model):
    course = models.ForeignKey(Course)

    name = models.CharField(max_length=64)
    par = models.IntegerField()
    distance = models.IntegerField()


class Player(models.Model):
    name = models.CharField(max_length=64)


class Event(models.Model):
    name = models.CharField(max_length=64)
    course = models.ForeignKey(Course)
    players = models.ManyToManyField(Player, through='EventPlayer')
    password = models.CharField(max_length=64)
    date = models.DateField()


class EventPlayer(models.Model):
    event = models.ForeignKey(Event)
    player = models.ForeignKey(Player)
    handicap = models.IntegerField()


class Score(models.Model):
    hole = models.ForeignKey(Hole)
    event_player = models.ForeignKey(EventPlayer)
    score = models.IntegerField()