from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.static import * 
from django.conf import settings
import homeview, contentview, userview, ajaxviews

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', homeview.redirecthome),
    url(r'^about/$', contentview.about),
    url(r'^contact/$', contentview.contact),
    url(r'^home/$', homeview.home),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^logout/$', userview.logout),
    url(r'^login/$', userview.login),	
    url(r'^register/$', userview.register),
    url(r'^editProfile/$', userview.editProfile),
    url(r'^changePassword/$', userview.changePassword),
    url(r'^changePassword/successful/$', userview.passwordChanged),
    url(r'^resetPassword/$', userview.resetPassword),
    url(r'^resetPassword/successful/$', userview.passwordReset),
    url(r'^new/$', contentview.addBulletin),
    url(r'^elements/help/raw/', ajaxviews.help_raw),
    url(r'^elements/help/filtered/', ajaxviews.help_filtered),
    url(r'^elements/want/raw/', ajaxviews.want_raw),
    url(r'^elements/want/filtered/', ajaxviews.want_filtered),
	url(r'^newMissive/$', contentview.newMissive),
	url(r'^people/$', contentview.people),
)

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    from django.views.static import serve
    _media_url = settings.MEDIA_URL
    if _media_url.startswith('/'):
        _media_url = _media_url[1:]
        urlpatterns += patterns('',
                                (r'^%s(?P<path>.*)$' % _media_url,
                                serve,
                                {'document_root': settings.MEDIA_ROOT}))
    del(_media_url, serve)
