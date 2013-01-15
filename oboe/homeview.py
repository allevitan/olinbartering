#homeview.py
from django.shortcuts import render
from models import Bulletin
from django.http import HttpResponseRedirect
import datetime

def home(request):
	base = Bulletin.objects.filter(resolved=False).filter(relevance__gte=datetime.datetime.now()).order_by("-update")
	helps = base.filter(helpbulletin=True)
	wants = base.filter(helpbulletin=False)
	
	if not (request.user.is_authenticated() and request.user.userdata.filterhelp):
		pass
	else:
		helpfilters = request.user.userdata.filters.filter(helpfilter=True)
		helps = helps.filter(tag__in=helpfilters)
	if not (request.user.is_authenticated() and request.user.userdata.filterwant):	
		pass
	else:
		wantfilters = request.user.userdata.filters.filter(helpfilter=False)
		wants = wants.filter(tag__in=wantfilters)

	return render(request, 'home.html', {'helps':helps, 'wants':wants})

def redirecthome(request):
	return HttpResponseRedirect('home/')

