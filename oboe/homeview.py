#homeview.py
from django.shortcuts import render
from models import Bulletin
from django.http import HttpResponseRedirect
from ajaxviews import pullfeed
import datetime

def home(request):
	if request.user.is_authenticated():
		helps = pullfeed(request.user.userdata, True)
		wants = pullfeed(request.user.userdata, False)
		return render(request, 'home.html', {'helps':helps, 'wants':wants})
	else:
		return HttpResponseRedirect('/login/')

def redirecthome(request):
	return HttpResponseRedirect('home/')

