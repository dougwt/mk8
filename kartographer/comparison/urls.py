"""Specify Django url patterns for Comparison views."""

from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^$', 'comparison.views.home', name='home'),
    url(r'^components/', 'comparison.views.components', name='components'),
    url(r'^kart-components/', 'comparison.views.components_redirect'),
    url(r'^add/(?P<character>[0-9]+)/(?P<kart>[0-9]+)/(?P<wheel>[0-9]+)/(?P<glider>[0-9]+)/', 'comparison.views.add'),
    url(r'^add/', 'comparison.views.add', name='add'),
    url(r'^reset/', 'comparison.views.reset', name='reset'),
    url(r'^save/', 'comparison.views.save', name='save'),
    url(r'^l/(?P<url_hash>[0-9a-f]{5})/', 'comparison.views.list', name='list'),
    url(r'^ajax_set_pref/$','comparison.views.ajax_set_preference'),
    url(r'^ajax_remove_kart/$','comparison.views.ajax_remove_kart'),
    url(r'^top/', 'comparison.views.top', name='top'),
)
