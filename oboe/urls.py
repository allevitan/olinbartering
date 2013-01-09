from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.static import * 
from django.conf import settings
import views
import ajaxviews

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.redirecthome),
    url(r'^about/$', views.about),
    url(r'^contact/$', views.contact),
    url(r'^home/$', views.home),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^logout/$', views.logout),
    url(r'^login/$', views.login),	
    url(r'^register/$', views.register),
    url(r'^editProfile/$', views.editProfile),
    url(r'^changePassword/$', views.changePassword),
    url(r'^changePassword/successful/$', views.passwordChanged),
    url(r'^resetPassword/$', views.resetPassword),
    url(r'^resetPassword/successful/$', views.passwordReset),
    url(r'^new/$', views.addBulletin),
    url(r'^elements/help/raw/', ajaxviews.help_raw),
    url(r'^elements/help/filtered/', ajaxviews.help_filtered),
    url(r'^elements/want/raw/', ajaxviews.want_raw),
    url(r'^elements/want/filtered/', ajaxviews.want_filtered),
	url(r'^newMissive/$', views.newMissive),
	url(r'^people/$', views.people),
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
