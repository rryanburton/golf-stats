from django.conf.urls import patterns, url
from golfstats.apps.homepage.views import home

urlpatterns = patterns('',
                       url(r'^$', home),
)