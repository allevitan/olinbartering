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
        if not request.user.userdata.includecarpe:
            bulletins = bulletins.exclude(anon=True)
        return render(request, 'elements/wantwidget.html', { 'bulletins': bulletins })
    else: return render(request, '404.html')

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
        if not request.user.userdata.includehelpme:
            bulletins = bulletins.exclude(anon=True)
        return render(request, 'elements/helpwidget.html', { 'bulletins': bulletins })
    else: return render(request, '404.html')

def want_raw(request):
    """Render all relevant & unresolved want bulletins."""
    #Set the user's want filtering preference to raw
    if request.user.is_authenticated():
        request.user.userdata.filterwant = False
        request.user.userdata.save()
        #Query and return the appropriate bulletins
        bulletins = Bulletin.objects.filter(resolved=False).filter(helpbulletin=False).filter(relevance__gte=datetime.datetime.now()).order_by("-update")
        if not request.user.userdata.includecarpe:
            bulletins = bulletins.exclude(anon=True)
        return render(request, 'elements/wantwidget.html', { 'bulletins': bulletins })
    else: return render(request, '404.html')

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
        if not request.user.userdata.includecarpe:
            bulletins = bulletins.exclude(anon=True)
        return render(request, 'elements/wantwidget.html', { 'bulletins': bulletins })
    else: return render(request, '404.html')


def includehelpme(request):
    """ render all the unresolved and relevant help bulletins, with
    the anonymous ones from helpme. """
    if request.user.is_authenticated():
        #Set the user's preference to including helpme
        request.user.userdata.includehelpme = True
        request.user.userdata.save()
        bulletins = Bulletin.objects.filter(resolved=False).filter(helpbulletin=True).filter(relevance__gte=datetime.datetime.now()).order_by("-update")
        if request.user.userdata.filterhelp:
            filters = request.user.userdata.filters.filter(helpfilter=True)
            bulletins = bulletins.filter(tag__in=filters)
        return render(request, 'elements/wantwidget.html', { 'bulletins': bulletins })
    else: return render(request, '404.html')

def excludehelpme(request):
    """ render all the unresolved and relevant help bulletins, without
    the anonymous ones from helpme. """
    if request.user.is_authenticated():
        #Set the user's preference to excluding helpme
        request.user.userdata.includehelpme = False
        request.user.userdata.save()
        bulletins = Bulletin.objects.filter(resolved=False).filter(helpbulletin=True).exclude(anon=True).filter(relevance__gte=datetime.datetime.now()).order_by("-update")
        if request.user.userdata.filterhelp:
            filters = request.user.userdata.filters.filter(helpfilter=True)
            bulletins = bulletins.filter(tag__in=filters)
        return render(request, 'elements/wantwidget.html', { 'bulletins': bulletins })  
    else: return render(request, '404.html')

def includecarpe(request):
    """ render all the unresolved and relevant help bulletins, with
    the anonymous ones from carpe. """
    if request.user.is_authenticated():
        #Set the user's preference to including carpe
        request.user.userdata.includecarpe = True
        request.user.userdata.save()
        bulletins = Bulletin.objects.filter(resolved=False).filter(helpbulletin=False).filter(relevance__gte=datetime.datetime.now()).order_by("-update")
        if request.user.userdata.filterwant:
            filters = request.user.userdata.filters.filter(helpfilter=False)
            bulletins = bulletins.filter(tag__in=filters)
        return render(request, 'elements/wantwidget.html', { 'bulletins': bulletins })
    else: return render(request, '404.html')

def excludecarpe(request):
    """ render all the unresolved and relevant help bulletins, without
    the anonymous ones from carpe. """
    if request.user.is_authenticated():
        #Set the user's preference to excluding carpe
        request.user.userdata.includecarpe = False
        request.user.userdata.save()
        bulletins = Bulletin.objects.filter(resolved=False).filter(helpbulletin=False).exclude(anon=True).filter(relevance__gte=datetime.datetime.now()).order_by("-update")
        if request.user.userdata.filterwant:
            filters = request.user.userdata.filters.filter(helpfilter=False)
            bulletins = bulletins.filter(tag__in=filters)
        return render(request, 'elements/wantwidget.html', { 'bulletins': bulletins })
    else: return render(request, '404.html')
