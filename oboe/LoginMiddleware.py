from django.http import HttpResponseRedirect
from models import UserData
import urllib2

class PreventAccess():

    def process_request(self, request):
        if not self._logged_in(request) and request.path != '/login/':
            return HttpResponseRedirect('/login/')

    def _logged_in(self, request):
        if request.session.get('who'):
            return True
            print 'Logged in'
        else: return False
