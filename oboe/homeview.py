#homeview.py
from django.shortcuts import render
from models import Bulletin, UserData
from django.http import HttpResponseRedirect
from ajaxviews import pullfeed
import datetime

def home(request):
    me = UserData.objects.get(pk=request.session['pk'])
    helps = pullfeed(UserData.objects.get(pk=request.session['pk']), True)
    wants = pullfeed(UserData.objects.get(pk=request.session['pk']), False)
    return render(request, 'home.html', {'helps':helps, 'wants':wants})

def redirecthome(request):
    return HttpResponseRedirect('home/')

