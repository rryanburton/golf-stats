from django.contrib import admin
from golfstats.models import Event, Course, Hole, Team, Score


class HoleInline(admin.TabularInline):
    model = Hole
    extra = 18


class CourseAdmin(admin.ModelAdmin):
    inlines = [
        HoleInline,
    ]


admin.site.register(Course, CourseAdmin)


class TeamInline(admin.TabularInline):
    model = Team
    extra = 6
    fields = [
        'name',
        'event',
        'handicap',
    ]


class EventAdmin(admin.ModelAdmin):
    inlines = [
        TeamInline,
    ]


admin.site.register(Event, EventAdmin)


class ScoreInline(admin.TabularInline):
    model = Score


class TeamAdmin(admin.ModelAdmin):
    inlines = [
        ScoreInline,
    ]

    list_filter = ['event']


admin.site.register(Team, TeamAdmin)


class ScoreAdmin(admin.ModelAdmin):
    pass


admin.site.register(Score, ScoreAdmin)