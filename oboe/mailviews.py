from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.models import User
from models import Reply_Thread, Reply
from django.core.mail import send_mail

def mailbox(request):
    mail = Reply_Thread.objects.filter(users=request.user.userdata).order_by("-update")
    return render(request, 'mailbox.html', {'mail':mail})
