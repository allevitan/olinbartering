from django import template

register = template.Library.filter()

@register.filter(name='replace')
def replace(value, arg):
    """replaces all values of the first part of arg with the second, comma separated"""
    args = arg.split(arg, ',')
    return value.replace(args[0], args[1])



