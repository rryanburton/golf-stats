from django.conf.urls import include, patterns
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns(
    '',
    (r'', include('golfstats.apps.homepage.urls')),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
)
