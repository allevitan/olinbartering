from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.models import User
from models import Reply_Thread, Reply
from django.core.mail import send_mail
from forms import ReplyForm

def base(request):
    return HttpResponseRedirect('/mail/box/')

def mailbox(request):
    mail = Reply_Thread.objects.filter(users=request.user.userdata).order_by("-update")
    pks = []
    user = request.user
    for thread in mail:
        if len(thread.users.all()) == 1:
            pks.append(thread.id)
    print pks
    mail = mail.exclude(id__in=pks)
    return render(request, 'mailbox.html', {'mail':mail})

def thread(request, pk):
    thread = Reply_Thread.objects.get(id=pk);
    if request.user.is_authenticated() and request.user.userdata in thread.users.all(): info = {'thread':thread}
    else: info = {}

    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            cleaned_data = form.clean()
            if request.POST['visibility'] == 'Public':
                public = True
            else: public = False
            user = request.user.userdata
            message = cleaned_data['message']
            reply = Reply.objects.create(public=public, sender=user, message=message, thread=thread)
            thread.save()
            reply.save()
    
    form = ReplyForm()	
    info.update({'form':form});
    return render(request, 'elements/replythread.html', info)
