#homeview.py
from django.shortcuts import render
from models import Bulletin
from django.http import HttpResponseRedirect

def home(request):
	if not (request.user.is_authenticated() and request.user.userdata.filterhelp):
		helps = Bulletin.objects.filter(resolved=False, helpbulletin=True).order_by("-update")
	else:
		helpfilters = request.user.userdata.filters.filter(helpfilter=True)
		helps = Bulletin.objects.filter(resolved=False, helpbulletin=True).filter(tag__in=helpfilters).order_by("-update")
	if not (request.user.is_authenticated() and request.user.userdata.filterwant):	
		wants = Bulletin.objects.filter(resolved=False, helpbulletin=False).order_by("-update")
	else:
		wantfilters = request.user.userdata.filters.filter(helpfilter=False)
		wants = Bulletin.objects.filter(resolved=False, helpbulletin=False).filter(tag__in=wantfilters).order_by("-update")

	return render(request, 'home.html', {'range':range(1, 6), 'helps':helps, 'wants':wants})

def redirecthome(request):
	return HttpResponseRedirect('home/')

