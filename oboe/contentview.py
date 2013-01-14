#contentview.py
from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.models import User
from forms import ContactForm, PasswordResetForm, selectBulletinForm
from forms import BulletinForm, MissiveForm, MultiProfileDisplay
from forms import ReplyForm, UpdateBulletinForm
from models import UserData, Missive, Filter, Bulletin, Reply, Reply_Thread
from django.core.mail import send_mail
from passgen import generate_password
from datetime import datetime


def about(request):
	return render(request, 'about.html')

def people(request):
	if request.method == 'POST':
		form = MultiProfileDisplay(request.POST, request.FILES)
		if form.is_valid():
			cleaned_data = form.clean()
			filterText = cleaned_data['filters']
			filterType = cleaned_data['filterType']
			if filterText == "None":
				users = UserData.objects.all()
			else:
				chosenFilter = Filter.objects.filter(name=filterText, helpfilter = filterType)
				users = UserData.objects.filter(filters__id=chosenFilter)
			form = MultiProfileDisplay()
	else:
		users = UserData.objects.all().order_by("user")
		form = MultiProfileDisplay()
		filterText = "None"
	return render(request, 'MultiProfileDisplay.html', {'users':users, 'form':form, 'filterText': filterText})

def contact(request):
	if request.method == 'POST':
		form = ContactForm(request.POST)
		if form.is_valid():
			cleaned_data = form.clean()
			subject = cleaned_data['subject']
			message = cleaned_data['message']
			toAddress = cleaned_data['emailAddress']
			send_mail(subject, message, 'allevitan@gmail.com',
    ['allevitan@gmail.com'], fail_silently=False)
			return HttpResponseRedirect('/')
	else:
		if request.user.is_active and request.user.is_authenticated():
			data = {'emailAddress':request.user.email}
			form = ContactForm(initial=data)
		else:
			form = ContactForm()
	
	return render(request, 'contact.html', {'form':form})

def getFilter(name, helpfilter):
	try:
		if helpfilter:
			bulletinFilter = Filter.objects.get(name = name, helpfilter=True)
		else:
			bulletinFilter = Filter.objects.get(name = name, helpfilter=False)
	except: 
		if helpfilter:
			bulletinFilter = Filter.objects.create(name = name, helpfilter=True)
		else:
			bulletinFilter = Filter.objects.create(name = name, helpfilter=False)	
		bulletinFilter.save()
	return bulletinFilter

def addBulletin(request):	
	if request.method == 'POST':
		form = BulletinForm(request.POST, request.FILES)
		if form.is_valid() and request.user.is_authenticated():
			cleaned_data = form.clean()
			user = User.objects.get(username = request.user)
			userdata = user.userdata
			email = user.email
			subject = cleaned_data['subject']
			message = cleaned_data['message']
			location = cleaned_data['location']
			relevance = cleaned_data['relevance']
			filters = cleaned_data['filters']
			bulletinType = cleaned_data['bulletinType']
			if bulletinType == "Want?":
				price = cleaned_data['price']
				bulletinFilter = getFilter(filters, helpfilter=False)
				bulletin = Bulletin.objects.create(creator = userdata, subject = subject,
					location = location, relevance = relevance, resolved=False, reply_count = 0,
                	free=price, tag=bulletinFilter, helpbulletin=False)
			elif bulletinType == "Help?":
				bulletinFilter = getFilter(filters, helpfilter=True)
				bulletin = Bulletin.objects.create(creator = userdata, subject = subject,
					location = location, relevance = relevance, helpbulletin=True,
					resolved=False, reply_count = 0, tag=bulletinFilter)
			else:
				raise ValidationError
			missive = Missive.objects.create(bulletin = bulletin, timestamp = datetime.now(), 
				message = message)
			bulletin.save()
			missive.save()
			return HttpResponseRedirect('/')
	else:
		if request.user.is_authenticated():
			form = BulletinForm()
		else:
			return HttpResponseRedirect('/login')
	return render(request, 'addBulletin.html', {'form':form})

def editBulletin(request):	
	if request.method == 'POST':
		form = BulletinForm(request.POST, request.FILES)
		bulletin = request.session['bulletin']
		missive = Missive.objects.filter(bulletin=bulletin).order_by("timestamp")[0]
		if form.is_valid() and request.user.is_authenticated():
			cleaned_data = form.clean()
			user = User.objects.get(username = request.user)
			userdata = user.userdata
			email = user.email
			subject = cleaned_data['subject']
			message = cleaned_data['message']
			location = cleaned_data['location']
			relevance = cleaned_data['relevance']
			filters = cleaned_data['filters']
			bulletinType = cleaned_data['bulletinType']
			bulletin.subject = subject
			missive.message = message
			bulletin.location = location
			bulletin.relevance = relevance			
			if bulletinType == "Want?":
				price = cleaned_data['price']
				bulletinFilter = getFilter(filters, helpfilter=False)
				bulletin.tag = bulletinFilter
				bulletin.helpbulletin = False
				bulletin.price = price
			elif bulletinType == "Help?":
				bulletinFilter = getFilter(filters, helpfilter=True)
				bulletin.tag = bulletinFilter
				bulletin.helpbulletin = True
			else:
				raise ValidationError
			bulletin.save()
			missive.save()
			return HttpResponseRedirect('/')
	else:
		if request.user.is_authenticated():
			bulletin = request.session['bulletin']
			missive = Missive.objects.filter(bulletin=bulletin).order_by("timestamp")[0]
			data = {'subject': bulletin.subject, 'relevance':bulletin.relevance, 
					'location':bulletin.location, 'filters': bulletin.tag.name, 'message':missive.message}
			if bulletin.helpbulletin:
				data['bulletinType']= 'Help?'
			else:
				data['bulletinType']= 'Want?'
				data['price'] = bulletin.free

			form = BulletinForm(initial = data)
		else:
			return HttpResponseRedirect('/login')
	return render(request, 'editBulletin.html', {'form':form, 'edit':True})

def selectBulletin(request):	
	if request.method == 'POST':
		bulletins = set((bulletin.subject, bulletin.subject) for bulletin in Bulletin.objects.filter(creator=request.user.userdata))
		form = selectBulletinForm(request.POST or None, request.FILES, bulletins=bulletins)
		if form.is_valid():
			cleaned_data = form.clean()
			user = User.objects.get(username = request.user)
			userdata = user.userdata
			subject = request.POST.get('bulletin', '')
			bulletin = Bulletin.objects.get(subject=subject)
			request.session['bulletin'] = bulletin
			return HttpResponseRedirect('/editBulletin')
	else:
		if request.user.is_authenticated():
			bulletins = set((bulletin.subject, bulletin.subject) for bulletin in Bulletin.objects.filter(creator=request.user.userdata))
			form = selectBulletinForm(request.POST or None, bulletins=bulletins)
		else:
			return HttpResponseRedirect('/login')
	return render(request, 'selectBulletin.html', {'form':form})


def newMissive(request):	
	if request.method == 'POST':
		bulletins = set((bulletin.subject, bulletin.subject) for bulletin in Bulletin.objects.filter(creator=request.user.userdata))
		form = MissiveForm(request.POST or None, request.FILES, bulletins=bulletins)
		if form.is_valid():
			cleaned_data = form.clean()
			user = User.objects.get(username = request.user)
			userdata = user.userdata
			message = cleaned_data['message']
			subject = request.POST.get('bulletin', '')
			bulletin = Bulletin.objects.get(subject=subject)
			bulletin.update = datetime.now()
			bulletin.save()
			missive = Missive.objects.create(bulletin = bulletin, timestamp = datetime.now(), message = message)
			missive.save()
			return HttpResponseRedirect('/')
	else:
		if request.user.is_authenticated():
			bulletins = set((bulletin.subject, bulletin.subject) for bulletin in Bulletin.objects.filter(creator=request.user.userdata))
			form = MissiveForm(request.POST or None, bulletins=bulletins)
		else:
			return HttpResponseRedirect('/login')
	return render(request, 'newMissive.html', {'form':form})

def viewBulletin(request, pk):
	if pk > 0:
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
			user = request.user.userdata
			message = cleaned_data['message']
			if allreplies.filter(sender=user).exists():
				thread = (allreplies.filter(sender=user)[0]).thread
			else:
				thread = Reply_Thread.objects.create(bulletin=bulletin)
				thread.users.add(user)
				thread.users.add(bulletin.creator)
			thread.save()
			reply = Reply.objects.create(public=public, sender=user, message=message, thread=thread)
			reply.save()
	
	form = ReplyForm()	
	if request.user.userdata == bulletin.creator:
		bulletinform = UpdateBulletinForm()
	else: bulletinform = {}
	return render(request, 'bulletin.html', {'bulletin':bulletin, 'replies':replies, 'privatecount':privatecount, 'form':form, 'bulletinform':bulletinform})

def updateBulletin(request, pk):
	if pk > 0 and request.user.is_authenticated() and request.method == 'POST':
		bulletin = Bulletin.objects.get(pk=pk)
	else: return HttpResponseRedirect('/home/')
	if request.user.userdata == bulletin.creator:
		form = UpdateBulletinForm(request.POST)
		if form.is_valid():
			cleaned_data = form.clean()
			message = cleaned_data['missive']
			missive = Missive.objects.create(message=message,bulletin=bulletin)
			if request.POST.get('free',''):
				bulletin.free = "true"
			bulletin.save()
			missive.save()
		else: return HttpResponseRedirect('/bulletin/%d/' % bulletin.id)
	else: return HttpResponseRedirect('/bulletin/%d/' % bulletin.id)
	return HttpResponseRedirect('/home/');
