from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.models import User
from models import Reply_Thread, Reply
from django.core.mail import send_mail
from forms import ReplyForm

def base(request):
    """Redirect to mailbox."""
    return HttpResponseRedirect('/mail/box/')

def mailbox(request):
    """Render the mailbox template if user is authenticated."""
    if request.user.is_authenticated():

        #Return all threads including the user, properly ordered
        mail = Reply_Thread.objects.filter(users=request.user.userdata).order_by("-update")
        
        #Filter out the threads that ONLY include the user
        pks = []
        user = request.user
        for thread in mail:
            if len(thread.users.all()) == 1:
                pks.append(thread.id)
        mail = mail.exclude(id__in=pks)
        
        return render(request, 'mailbox.html', {'mail':mail})
    else:
        #send to login page if anonymous
        return HttpResponseRedirect('/login/')

def thread(request, pk):
    """Render a single thread's info, usually for the mailbox"""
    
    thread = Reply_Thread.objects.get(id=pk)
    info={}
    
    #You have to belong to the thread to access it!
    if (request.user.is_authenticated() 
        and request.user.userdata in thread.users.all()):
        info.update({'thread':thread})
        #Handle request to add replies to the thread
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
    #Filling out the necessary context
    form = ReplyForm()	
    info.update({'form':form});
    return render(request, 'elements/replythread.html', info)

from django.conf.urls import patterns, url

urls = patterns('',
                url(r'^$', base),
                url(r'^box/$', mailbox),
                url(r'^thread/(?P<pk>\d+)/$', thread),
)
