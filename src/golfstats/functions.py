def can_edit_team_score(request, team):
    if request.user.is_superuser:
        return True

    for user in team.users.all():
        if user.id == request.user.id:
            return True

    return False