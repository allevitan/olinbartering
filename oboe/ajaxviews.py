from django.shortcuts import render
from django.http import HttpResponseRedirect
from models import Bulletin
import datetime



def help_raw(request):
    """Render all relevant & unresolved help bulletins."""
    #Set the user's help filtering preference to raw
    if request.user.is_authenticated():
        request.user.userdata.filterhelp = False
        request.user.userdata.save()
    #Query for and return the list of bulletins
    bulletins = Bulletin.objects.filter(resolved=False).filter(helpbulletin=True).filter(relevance__gte=datetime.datetime.now()).order_by("-update")
    return render(request, 'elements/helpwidget.html', { 'bulletins': bulletins })

def help_filtered(request):
    """
    Render all relevant & unresolved help bulletins that correspond
    to the user's filters.
    """
    if request.user.is_authenticated():
        #Set the user's help filtering preference to filtered
        request.user.userdata.filterhelp = True
        request.user.userdata.save()
        #Query the database for the filters and bulletins
        filters = request.user.userdata.filters.filter(helpfilter=True)
        bulletins = Bulletin.objects.filter(resolved=False).filter(helpbulletin=True).filter(tag__in=filters).filter(relevance__gte=datetime.datetime.now()).order_by("-update")
    else:
        bulletins = Bulletin.objects.filter(resolved=False).filter(helpbulletin=True).filter(relevance_gte=datetime.datetime.now()).order_by("-update")
    return render(request, 'elements/helpwidget.html', { 'bulletins': bulletins })

def want_raw(request):
    """Render all relevant & unresolved want bulletins."""
    #Set the user's want filtering preference to raw
    if request.user.is_authenticated():
        request.user.userdata.filterwant = False
        request.user.userdata.save()
    #Query and return the appropriate bulletins
    bulletins = Bulletin.objects.filter(resolved=False).filter(helpbulletin=False).filter(relevance__gte=datetime.datetime.now()).order_by("-update")
    return render(request, 'elements/wantwidget.html', { 'bulletins': bulletins })

def want_filtered(request):
    """
    Render all relevant & unresolved help bulletins that correspond
    to the user's filters.
    """
    if request.user.is_authenticated():
        #Set the user's want filtering preference to filtered
        request.user.userdata.filterwant = True
        request.user.userdata.save()
        #Query for the filters and the bulletins
        filters = request.user.userdata.filters.filter(helpfilter=False)
        bulletins = Bulletin.objects.filter(resolved=False).filter(helpbulletin=False).filter(tag__in=filters).filter(relevance__gte=datetime.datetime.now()).order_by("-update")
    else:
        bulletins = Bulletin.objects.filter(resolved=False).filter(helpbulletin=False).filter(relevance__gte=datetime.datetime.now()).order_by("-update")
    return render(request, 'elements/wantwidget.html', { 'bulletins': bulletins })
