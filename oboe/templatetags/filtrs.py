from django import template
from django.template import defaultfilters
from django.core.cache import cache

register = template.Library()

@register.filter(name='keepbreaks', is_safe=True)
@defaultfilters.stringfilter
def keepbreaks(value):
    """turns an html string into plain text, but keeps all the <br>s"""
    value = value.replace("<br>", "\n")
    value = defaultfilters.striptags(value)
    return defaultfilters.linebreaksbr(value)

@register.filter(name='convertback', is_safe=True)
@defaultfilters.stringfilter
def convertback(value):
    """turns an html string into plain text, but keeps all the <br>s"""
    value = value.replace("&lt;", "<")
    value = value.replace("&gt;", ">")
    value = value.replace("&#39;", "'")
    value = value.replace('&quot;', '"')
    value = value.replace("&amp;", "&")
    return value

@register.filter(name='replace')
@defaultfilters.stringfilter
def replace(value, args):
    """replaces all values of the first part of arg with the second, comma separated"""
    args = args.split(',')
    #If they use a space after the comma
    if args[1][0] == ' ':
        args[1] = args[1][1:]
    return value.replace(args[0], args[1])


# The filters that find data from the cache
@register.filter(name='photo')
@defaultfilters.stringfilter
def photo(value):
    """finds the url for a users photo from the memcache"""
    return getpeepdata(value, 'thumbnail', error="http://www.placekitten.com/80/80")

@register.filter(name='thumb', is_safe=True)
@defaultfilters.stringfilter
def thumb(value, args):
    return value

@register.filter(name='name')
@defaultfilters.stringfilter
def name(value):
    return getpeepdata(value, 'name')

@register.filter(name='email')
@defaultfilters.stringfilter
def email(value):
    return getpeepdata(value, 'email')


def getpeepdata(name, thing, error=None):
    try:
        thing = cache.get('peeps').get(name).get(thing)
    except:
        thing = error
    #If the user doesn't have the thing, the try/except won't trigger -
    #This catches it.
    if thing:
        return thing
    else:
        return error

