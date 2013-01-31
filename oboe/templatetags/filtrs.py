from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter(name='replacebr', is_safe=True)
@stringfilter
def replacebr(value):
    """replaces all values of the first part of arg with the second, comma separated"""
    return value.replace("<br>", "\n")
