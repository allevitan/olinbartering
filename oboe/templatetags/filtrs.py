from django import template
from django.template import defaultfilters

register = template.Library()

@register.filter(name='keepbreaks', is_safe=True)
@defaultfilters.stringfilter
def keepbreaks(value):
    """turns an html string into plain text, but keeps all the <br>s"""
    value = value.replace("<br>", "\n")
    value = defaultfilters.striptags(value)
    return defaultfilters.linebreaksbr(value)

@register.filter(name='replace')
@defaultfilters.stringfilter
def replace(value, args):
    """replaces all values of the first part of arg with the second, comma separated"""
    args = args.split(',')
    #If they use a space after the comma
    if args[1][0] == ' ':
        args[1] = args[1][1:]
    return value.replace(args[0], args[1])
