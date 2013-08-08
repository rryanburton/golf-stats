from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from golfstats.models import Event, Team, Score, Hole


def home(request):
    return render(request, 'home.html')


@login_required()
def events(request):
    my_events = Event.objects.filter(team__users=request.user)
    return render(request, 'events.html', {'events': my_events})


@login_required()
def teams(request, event_id):
    event = Event.objects.filter(team__users=request.user, id=event_id)[0]
    teams = Team.objects.filter(event=event)
    return render(request, 'teams.html', {'teams': teams, 'event': event})


@login_required()
def scores(request, event_id, team_id):
    event = Event.objects.filter(team__users=request.user, id=event_id)[0]
    team = Team.objects.get(event=event, id=team_id)
    scores = Score.objects.filter(team=team)

    holes = Hole.objects.filter(course=event.course).exclude(score__in=scores)
    return render(request, 'scores.html', {'scores': scores, 'event': event, 'team': team, 'holes': holes})


@login_required()
def edit_score(request, event_id, team_id, score_id):
    event = Event.objects.filter(team__users=request.user, id=event_id)[0]
    team = Team.objects.get(event=event, id=team_id)
    score = Score.objects.get(team=team, id=score_id)
    return render(request, 'edit-score.html', {'score': score, 'event': event, 'team': team})


@login_required()
def add_score(request, event_id, team_id, hole_id):
    event = Event.objects.filter(team__users=request.user, id=event_id)[0]
    team = Team.objects.get(event=event, id=team_id)
    hole = Hole.objects.get(id=hole_id, course=event.course)
    score = Score.objects.create(team=team, hole=hole, score=0)
    return redirect(reverse('edit-score', args=[event.id, team.id, score.id]))