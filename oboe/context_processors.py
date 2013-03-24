from django.core.cache import cache
from models import UserData

def site_area(request):
    splitpath = request.path.split('/')
    return {'site_area':splitpath[1]}

def is_webkit(request):
    useragent = request.META['HTTP_USER_AGENT']
    if "webkit" in useragent.lower():
        return {'webkit':True}
    else: return {'webkit':False}

def who_dis(request):
    dis = request.session.get('pk')
    return {'me' : UserData.objects.get(dis)}

def the_folk(request):
    return {'folk' : UserData.objects.all()}

if __name__ == '__main__':
    from django.http import HttpRequest
    req = HttpRequest()
    req.path = "about/us/"

    #note: area works! (pulls first part of URI)
    print site_area(req)
