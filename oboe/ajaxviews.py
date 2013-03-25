from django.shortcuts import render
from django.http import HttpResponseRedirect
from models import Bulletin, UserData
import datetime
from django.utils import timezone

def pullfeed(userdata, helpbulletin):
    bulletins = Bulletin.objects.filter(resolved=False).filter(helpbulletin=helpbulletin).filter(relevance__gte=datetime.datetime.now(timezone.get_current_timezone())).order_by("-update")
    if helpbulletin and userdata.filterhelp:
        filters = userdata.filters.filter(helpfilter=True)
        bulletins = bulletins.filter(tag__in=filters)
    elif not helpbulletin and userdata.filterwant:
        filters = userdata.filters.filter(helpfilter=False)
        bulletins = bulletins.filter(tag__in=filters)
    if helpbulletin and not userdata.includehelpme:
        bulletins = bulletins.exclude(anon=True).exclude(tag__name__iexact='helpme')
    elif not helpbulletin and not userdata.includecarpe:
        bulletins = bulletins.exclude(anon=True).exclude(tag__name__iexact='carpediem')
    return bulletins

def getUD(request):
    return UserData.objects.get(pk=request.session.get('pk'))

def help(request):
    bulletins = pullfeed(getUD(request), True)
    return render(request, 'elements/helpwidget.html', { 'bulletins': bulletins })

def want(request):
    bulletins = pullfeed(getUD(request), False)
    return render(request, 'elements/wantwidget.html', { 'bulletins': bulletins })

def help_raw(request):
    """Render all relevant & unresolved help bulletins."""
    #Set the user's help filtering preference to raw
    UD = getUD(request)
    UD.filterhelp = False
    UD.save()
    #Query for and return the list of bulletins
    bulletins = pullfeed(UD, True)
    return render(request, 'elements/helpwidget.html', { 'bulletins': bulletins })

def help_filtered(request):
    """
    Render all relevant & unresolved help bulletins that correspond
    to the user's filters.
    """
    #Set the user's help filtering preference to filtered
    Ud = getUD(request)
    UD.filterhelp = True
    UD.save()
    #Query the database for the filters and bulletins
    bulletins = pullfeed(UD, True)
    return render(request, 'elements/helpwidget.html', { 'bulletins': bulletins })

def want_raw(request):
    """Render all relevant & unresolved want bulletins."""
    #Set the user's want filtering preference to raw
    UD = getUD(request)
    UD.filterwant = False
    UD.save()
    #Query and return the appropriate bulletins
    bulletins = pullfeed(UD, False)
    return render(request, 'elements/wantwidget.html', { 'bulletins': bulletins })

def want_filtered(request):
    """
    Render all relevant & unresolved help bulletins that correspond
    to the user's filters.
    """
    #Set the user's want filtering preference to filtered
    UD = getUD(request)
    UD.filterwant = True
    UD.save()
    #Query for the filters and the bulletins
    bulletins = pullfeed(UD, False)
    return render(request, 'elements/wantwidget.html', { 'bulletins': bulletins })


def includehelpme(request):
    """ render all the unresolved and relevant help bulletins, with
    the anonymous ones from helpme. """
    #Set the user's preference to including helpme
    UD = getUD(request)
    UD.includehelpme = True
    UD.save()
    bulletins = pullfeed(UD, True)
    return render(request, 'elements/helpwidget.html', { 'bulletins': bulletins })

def excludehelpme(request):
    """ render all the unresolved and relevant help bulletins, without
    the anonymous ones from helpme. """
    #Set the user's preference to excluding helpme
    UD = getUD(request)
    UD.includehelpme = False
    UD.save()
    bulletins = pullfeed(UD, True)
    return render(request, 'elements/helpwidget.html', { 'bulletins': bulletins })  

def includecarpe(request):
    """ render all the unresolved and relevant help bulletins, with
    the anonymous ones from carpe. """
    #Set the user's preference to including carpe
    UD = getUD(request)
    UD.includecarpe = True
    UD.save()
    bulletins = pullfeed(UD, False)
    return render(request, 'elements/helpwidget.html', { 'bulletins': bulletins })

def excludecarpe(request):
    """ render all the unresolved and relevant help bulletins, without
    the anonymous ones from carpe. """
    #Set the user's preference to excluding carpe
    UD = getUD(request)
    UD.includecarpe = False
    UD.save()
    bulletins = pullfeed(UD, False)
    return render(request, 'elements/helpwidget.html', { 'bulletins': bulletins })
