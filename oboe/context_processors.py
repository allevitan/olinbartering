from django.core.cache import cache

def site_area(request):
    splitpath = request.path.split('/')
    return {'site_area':splitpath[1]}

def is_webkit(request):
    useragent = request.META['HTTP_USER_AGENT']
    if "webkit" in useragent.lower():
        return {'webkit':True}
    else: return {'webkit':False}

def who_dis(request):
    dis = request.session.get('who')
    print cache
    return {'me' : cache.get('peeps').get(dis)}

def the_folk(request):
    peeps = cache.get('peeps')
    # peeps = [peep for peep in peeps.values()]
    #Some error handling if the cache has been flushed - put in later
    return {'peeps' : peeps}

if __name__ == '__main__':
    from django.http import HttpRequest
    req = HttpRequest()
    req.path = "about/us/"

    #note: area works! (pulls first part of URI)
    print site_area(req)
