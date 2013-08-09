from django.conf.urls import include, patterns, url
from django.contrib import admin
from django.views.generic import TemplateView
from golfstats.views import home, events, teams, scores, edit_score, add_score


admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', home),
    url(r'^events$', events, name='events'),
    url(r'^events/(?P<event_id>\d+)/teams$', teams, name='teams'),
    url(r'^events/(?P<event_id>\d+)/teams/(?P<team_id>\d+)/scores$', scores, name='scores'),
    url(r'^events/(?P<event_id>\d+)/teams/(?P<team_id>\d+)/scores/(?P<score_id>\d+)$', edit_score, name='edit-score'),
    url(r'^events/(?P<event_id>\d+)/teams/(?P<team_id>\d+)/scores/(?P<hole_id>\d+)/add$', add_score, name='add-score'),
    url(r'^not-allowed$', TemplateView.as_view(template_name='not-allowed.html'), name='not-allowed'),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^browserid/', include('django_browserid.urls')),
)
