from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.models import User
from models import Bulletin, Missive

def create(request):
    return render(request, 'create.html', {})
