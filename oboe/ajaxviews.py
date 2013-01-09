from django.shortcuts import render
from django.http import HttpResponseRedirect
from models import Bulletin  #, Help_Bulletin, Want_Bulletin

def help_raw(request):
    if request.user.is_authenticated():
        request.user.userdata.filterhelp = False
        request.user.userdata.save()
    bulletins = Bulletin.objects.filter(resolved=False, helpbulletin=True).order_by("-update")
    return render(request, 'elements/helpwidget.html', { 'bulletins': bulletins })

def help_filtered(request):
    if request.user.is_authenticated():
        request.user.userdata.filterhelp = True
        request.user.userdata.save()
        filters = request.user.userdata.filters.filter(helpfilter=True)
        bulletins = Bulletin.objects.filter(resolved=False, helpbulletin=True).filter(tag__in=filters).order_by("-update")
    else:
        bulletins = Bulletin.objects.filter(resolved=False, helpbulletin=True).order_by("-update")
    return render(request, 'elements/helpwidget.html', { 'bulletins': bulletins })

def want_raw(request):
    if request.user.is_authenticated():
        request.user.userdata.filterwant = False
        request.user.userdata.save()
    bulletins = Bulletin.objects.filter(resolved=False, helpbulletin=False).order_by("-update")
    return render(request, 'elements/wantwidget.html', { 'bulletins': bulletins })

def want_filtered(request):
    if request.user.is_authenticated():
        request.user.userdata.filterwant = True
        request.user.userdata.save()
        filters = request.user.userdata.filters.filter(helpfilter=False)
        bulletins = Bulletin.objects.filter(resolved=False, helpbulletin=False).filter(tag__in=filters).order_by("-update")
    else:
        bulletins = Bulletin.objects.filter(resolved=False, helpfilter=False).order_by("-update")
    return render(request, 'elements/wantwidget.html', { 'bulletins': bulletins })
