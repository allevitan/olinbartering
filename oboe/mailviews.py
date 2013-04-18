from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.models import User
from models import Reply_Thread, Reply
from django.core.mail import send_mail
from forms import ReplyForm
import outmail

def base(request):
    """Redirect to mailbox."""
    return HttpResponseRedirect('/mail/box/')

def mailbox(request):
    """Render the mailbox template if user is authenticated."""
    #Return all threads including the user, properly ordered
    mail = Reply_Thread.objects.filter(bulletin__creator=request.session['userdata'])
    mail2 = Reply_Thread.objects.filter(replier=request.session['userdata'])
    
    mail = mail | mail2
    mail = mail.order_by("-update")
    #Filter out the threads that ONLY include the user
    pks = []
    user = request.user
    for thread in mail:
        if thread.replier == thread.bulletin.creator:
            pks.append(thread.id)
    mail = mail.exclude(id__in=pks)
    
    return render(request, 'mailbox.html', {'mail':mail})

def thread(request, pk):
    """Render a single thread's info, usually for the mailbox"""

    print 'made it!'
    thread = Reply_Thread.objects.get(id=pk)
    info={}

    #You have to belong to the thread to access it!
    if request.session['userdata'] in [thread.bulletin.creator, thread.replier]:
	info.update({'thread':thread})
	new=[]
	for reply in thread.reply_set.exclude(sender=request.session['userdata']).filter(read=False):
	    new.append(reply.id)
	    reply.read=True
	    reply.save()
	#Handle request to add replies to the thread
	if request.method == 'POST':
	    form = ReplyForm(request.POST)
	    if form.is_valid():
		cleaned_data = form.clean()
		if request.POST['visibility'] == 'Public':
		    public = True
		else: public = False
		user = request.session['userdata']
		message = cleaned_data['message']
                outmail.replyWithThread(thread, message, user, public)
    #Filling out the necessary context
    form = ReplyForm()
    info.update({'form':form, 'new':new});
    return render(request, 'elements/replythread.html', info)


def newmail(request):
    replies = Reply.objects.filter(read=False)\
        .filter(thread__bulletin__creator=request.session['pk'])\
        .exclude(sender=request.session['pk'])
    replies2 = Reply.objects.filter(read=False)\
        .filter(thread__replier=request.session['pk'])\
        .exclude(sender=request.session['pk'])
    replies = replies | replies2
    length = len(replies)
    if length >= 1:
	new = "(%d)" % len(replies)
    else: new = ""
    for reply in replies:
	new = "%s %d" %(new, reply.thread.pk)
    return HttpResponse(new)


from django.conf.urls import patterns, url

urls = patterns('',
		url(r'^$', base),
		url(r'^box/$', mailbox),
		url(r'^thread/(?P<pk>\d+)/$', thread),
		url(r'^newmail/$', newmail),
)
