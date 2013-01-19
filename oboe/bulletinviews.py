from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import auth
from django.contrib.auth.models import User
from django.db.models import Q
from models import Bulletin, Missive, Filter, Reply_Thread, Reply, UserData
from forms import CreateBulletinForm, UpdateBulletinForm, ReplyForm, ResolverCreditForm
import datetime
import outmail


def create(request):
    if not request.user.is_authenticated():
	return HttpResponseRedirect('/login/')
    errors = []
    if request.method == 'POST':
	form = CreateBulletinForm(request.POST)
	if form.is_valid():
	    data = form.cleaned_data
	    creator = request.user.userdata
	    subject = data['subject']
	    reltime = datetime.timedelta(hours=data['hiddenrel'])
	    relevance = datetime.datetime.now() + reltime
	    location = data['hiddenloc']

	    if location not in ["NA","EH","WH","AC","CC","MH","LP"]:
		errors.append("that's not a real location")

	    if data['hiddentype'] == "Help":
		helpbulletin = True
		try: tag = Filter.objects.filter(helpfilter=True).get(name=data['tag'])
		except: errors.append("that tag isn't a help tag")
	    elif data['hiddentype'] == "Want":
		helpbulletin = False
		try: tag = Filter.objects.filter(helpfilter=False).get(name=data['tag'])
		except: errors.append("that tag isn't a want tag")
	    else: errors.append("that's not a type of bulletin!")

	    if data['hiddenprice'] == "Free":
		free = True
	    elif data['hiddenprice'] == "Cheap":
		free = False
	    else: errors.append("please enter a valid price.")

	    message = data['missive']

	    if not errors:
		outmail.createBulletin(subject, message, creator, location, relevance, tag, helpbulletin, free)
		return HttpResponseRedirect("/home/")

	else:
	    if not request.POST.get('subject',''):
		errors.append('please enter a subject.')
	    if not request.POST.get('missive',''):
		errors.append('please enter a message.')
	    if not request.POST.get('tag',''):
		errors.append('please enter a tag.')
    else: form = CreateBulletinForm()
    if len(errors) >= 3:
	errors.append('get your life together.')
    helptags = Filter.objects.filter(helpfilter=True)
    wanttags = Filter.objects.filter(helpfilter=False)
    return render(request, 'create.html', {'form':form, 'helptags':helptags, 'wanttags':wanttags, 'errors':errors})


def view(request, pk):

    if pk > 0:

	#database queries for bulletin info
	bulletin = Bulletin.objects.get(pk=pk)
	allreplies = Reply.objects.filter(thread__bulletin=bulletin)
	replies= allreplies.filter(public=True).order_by("-timestamp")
	privatecount = allreplies.filter(public=False).exclude(sender=bulletin.creator).count()
    else: return render(request, '404.html', {})

    if request.method == 'POST':
	form = ReplyForm(request.POST)
	if form.is_valid():
	    cleaned_data = form.clean()
	    if request.POST['visibility'] == 'Public':
		public = True
	    else: public = False
	    if request.user.userdata != bulletin.creator or public:
                message = cleaned_data['message']
                outmail.replyToBulletin(bulletin, message, request.user.userdata, public)

    #update page
    form = ReplyForm()
    resolveform = ResolverCreditForm()
    if request.user.is_authenticated and request.user.userdata == bulletin.creator:
	bulletinform = UpdateBulletinForm()
    else: bulletinform = {}
    return render(request, 'bulletin.html', {'bulletin':bulletin, 'replies':replies, 'privatecount':privatecount, 'form':form, 'bulletinform':bulletinform, 'resolveform':resolveform})


def resolve(request):
    if request.user.is_authenticated and request.method == 'POST':
	if request.POST.get('thread',''):
	    pk = int(request.POST['thread'])
	    thread = Reply_Thread.objects.get(pk=pk)
	    bulletin = thread.bulletin
	    fromthread = True
	else:
	    pk = int(request.POST['bulletin'])
	    bulletin = Bulletin.objects.get(pk=pk)
	    fromthread = False
	if bulletin.helpbulletin:
	    if bulletin.resolved:
		return HttpResponse('Nothing Happened')
	    else:
		if fromthread:
		    resolver = thread.users.exclude(user=request.user).get()
		    bulletin.resolver = resolver
		else:
		    resolver = request.POST['username']
		    if resolver:
			resolver = '.'.join(resolver.lower().split())
			resolver = User.objects.get(username=resolver).userdata
			if resolver == request.user.userdata:
			    return HttpResponse('Not yourself...')
			bulletin.resolver = resolver
			resolver.score = resolver.score + 1
			resolver.save()
		bulletin.resolved = True
		bulletin.save()
		return HttpResponse('Unresolve')
	else:
	   if bulletin.resolved:
		return HttpResponse('Nothing Happened')
	   else:
		bulletin.resolved = True
		bulletin.save()
		return HttpResponse('Resolved')
    else:
	return HttpResponseRedirect('/')


def update(request, pk):

    #basic validation
    if pk > 0 and request.user.is_authenticated() and request.method == 'POST':
	bulletin = Bulletin.objects.get(pk=pk)
    else: return HttpResponseRedirect('/home/')

    #check identity of user against identity of bulletin creator to
    #determine which page should be redered.
    if request.user.userdata == bulletin.creator:
	form = UpdateBulletinForm(request.POST)
	if form.is_valid():
	    cleaned_data = form.clean()
	    message = cleaned_data['missive']

	    #send out a new missive if the bulletin is not yet resolvd
	    if not bulletin.resolved:
		outmail.updateBulletin(bulletin, message)
		if request.POST.get('free',''):
		    bulletin.free = True
		    bulletin.save()

	    #add words of wisdom from the bulletin creator
	    elif bulletin.helpbulletin and len(message) <= 200:
		bulletin.advice = message
		bulletin.save()

	#direct users who input bad info to the bulletin page
	else: return HttpResponseRedirect('/bulletin/%d/' % bulletin.id)

    #direct users who don't have permission to update to the bulletin page
    else: return HttpResponseRedirect('/bulletin/%d/' % bulletin.id)

    #direct successful requests to the home page, where they see the update
    return HttpResponseRedirect('/home/');

def search(request):
    if request.user.is_authenticated and request.method == 'GET':
        query = request.GET.get('q','')
        if not query == '':
            print query
            bulletins = Bulletin.objects.filter(Q(subject__icontains=query) | Q(tag__name__icontains=query)).order_by("resolved", "-creation")
        else:
            bulletins = Bulletin.objects.none()
        return render(request, "archivesearch.html", {'bulletins':bulletins, 'query':query})
    else: return HttpResponseRedirect("/login/")


from django.conf.urls import patterns, url
urls = patterns('',
		url(r'^(?P<pk>\d+)/$', view),
		url(r'^resolve/$', resolve),
		url(r'^(?P<pk>\d+)/update/$', update),
                url(r'^search/', search),
)
