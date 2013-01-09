def site_area(request):
    splitpath = request.path.split('/')
    return {'site_area':splitpath[1]}

def is_webkit(request):
    useragent = request.META['HTTP_USER_AGENT']
    if "webkit" in useragent.lower():
        return {'webkit':True}
    else: return {'webkit':False}

if __name__ == '__main__':
    from django.http import HttpRequest
    req = HttpRequest()
    req.path = "about/us/"

    #note: area works! (pulls first part of URI)
    print site_area(req)
