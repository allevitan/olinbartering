from django.http import HttpResponseRedirect

class PreventAccess():

    def process_request(self, request):
        if not request.session.get('who') and request.path != '/login/':
            return HttpResponseRedirect('/login/')
