#homeview.py
from django.shortcuts import render
from models import Bulletin
from django.http import HttpResponseRedirect
import datetime

def home(request):
	if request.user.is_authenticated():
		base = Bulletin.objects.filter(resolved=False).filter(relevance__gte=datetime.datetime.now()).order_by("-update")
		helps = base.filter(helpbulletin=True)
		wants = base.filter(helpbulletin=False)
	
		if request.user.userdata.filterhelp:
			helpfilters = request.user.userdata.filters.filter(helpfilter=True)
			helps = helps.filter(tag__in=helpfilters)
		if request.user.userdata.filterwant:
			wantfilters = request.user.userdata.filters.filter(helpfilter=False)
			wants = wants.filter(tag__in=wantfilters)
		if not request.user.userdata.includehelpme:
			helps = helps.exclude(anon=True)
		if not request.user.userdata.includecarpe:
			wants = wants.exclude(anon=True)
		return render(request, 'home.html', {'helps':helps, 'wants':wants})
	else:
		return HttpResponseRedirect('/login/')

def redirecthome(request):
	return HttpResponseRedirect('home/')

