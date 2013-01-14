from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.models import User
from models import Bulletin, Missive, Filter

def create(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')
    if request.method == 'POST':
        print request.POST
    helptags = Filter.objects.filter(helpfilter=True);
    wanttags = Filter.objects.filter(helpfilter=False);
    return render(request, 'create.html', {'helptags':helptags, 'wanttags':wanttags})
