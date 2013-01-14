from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.models import User
from models import Bulletin, Missive

def create(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')
    if request.method == 'POST':
        print request.POST
    return render(request, 'create.html', {})
