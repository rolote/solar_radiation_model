from django.conf.urls import patterns, include, url
from plumbing.views import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    #url(r'^requester$', 'requester.views.index'),
    #url(r'^requester/automatic$', AutomaticDownloadList.as_view()),
    #url(r'^requester/order$', OrderList.as_view()),
    #url(r'^requester/time_range$', TimeRangeList.as_view()),
    #url(r'^requester/area$', AreaList.as_view()),
    #url(r'^requester/channel$', ChannelList.as_view()),
    #url(r'^requester/account$', AccountList.as_view()),
    url(r'^plumbing$', 'plumbing.views.index'),
    url(r'^plumbing/execute/(?P<program_id>\d+)/$', 'plumbing.views.execute'),
    url(r'^plumbing/status$', 'plumbing.views.status'),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
