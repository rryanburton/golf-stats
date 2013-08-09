from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum


class Course(models.Model):
    name = models.CharField(max_length=64)

    def __unicode__(self):
        return self.name


class Hole(models.Model):
    course = models.ForeignKey(Course)
    name = models.CharField(max_length=64)
    par = models.IntegerField()

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.par)


class Event(models.Model):
    name = models.CharField(max_length=64)
    course = models.ForeignKey(Course)
    date = models.DateField()

    def __unicode__(self):
        return '%s on %s' % (self.name, self.date)


class Team(models.Model):
    name = models.CharField(max_length=64)
    event = models.ForeignKey(Event)
    handicap = models.IntegerField()
    users = models.ManyToManyField(User)

    class Meta:
        pass

    def __unicode__(self):
        if self.handicap:
            return '%s (%s)' % (self.name, self.handicap)
        else:
            return self.name

    def strokes(self):
        return self.score_set.aggregate(total=Sum('score'))['total']

    def par(self):
        return self.score_set.aggregate(total=Sum('hole__par'))['total']

    def score(self):
        return self.strokes() - self.par()

    def holes(self):
        return self.score_set.count()


class Score(models.Model):
    hole = models.ForeignKey(Hole)
    team = models.ForeignKey(Team)
    score = models.IntegerField()

    class Meta:
        unique_together = ['hole', 'team']

    def __unicode__(self):
        return '%s: %s on %s' % (self.team, self.hole, self.score)