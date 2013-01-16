#contentview.py
from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.models import User
from forms import ContactForm, PasswordResetForm, selectBulletinForm
from forms import MultiProfileDisplay
from forms import ReplyForm, UpdateBulletinForm, ResolverCreditForm, FilterSuggestionForm
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
			user_name = cleaned_data['username']

			#username follows form "first.last"
			username = '.'.join(user_name.lower().split())

			#Maybe be useful in the future 
			'''
			filterText = cleaned_data['filters']
			filterType = cleaned_data['filterType']
			if filterText == "None":
				users = UserData.objects.all()
			else:
				chosenFilter = Filter.objects.filter(name=filterText, helpfilter = filterType)
				users = UserData.objects.filter(filters__id=chosenFilter)
			'''
			return HttpResponseRedirect('/profile/'+username+'/')
	else:
		
		#query database for list of all users and redisplay the same page.
		users = UserData.objects.all().order_by("user")
		form = MultiProfileDisplay()
		filterText = "None"
	return render(request, 'MultiProfileDisplay.html', {'users':users, 'form':form, 'filterText': filterText})

def getFilter(name, helpfilter):
	
	#better to ask forgiveness than permission
	#attempt to access filter object in database and create an entry if it does not exist
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

def viewBulletin(request, pk):
		
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
			user = request.user.userdata
			if user != bulletin.creator or public:
	
				#send public message
				message = cleaned_data['message']

				#generate new thread if needed
				if allreplies.filter(sender=user).exists():
					thread = (allreplies.filter(sender=user)[0]).thread
				else:
					thread = Reply_Thread.objects.create(bulletin=bulletin)
					thread.users.add(user)
					thread.users.add(bulletin.creator)
				
				#save info
				thread.save()
				reply = Reply.objects.create(public=public, sender=user, message=message, thread=thread)
				reply.save()

	#update page
	form = ReplyForm()
	resolveform = ResolverCreditForm()
	if request.user.userdata == bulletin.creator:
		bulletinform = UpdateBulletinForm()
	else: bulletinform = {}
	return render(request, 'bulletin.html', {'bulletin':bulletin, 'replies':replies, 'privatecount':privatecount, 'form':form, 'bulletinform':bulletinform, 'resolveform':resolveform})

def updateBulletin(request, pk):
	
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
				missive = Missive.objects.create(message=message,bulletin=bulletin)
				if request.POST.get('free',''):
					bulletin.free = True
				bulletin.save()
				missive.save()

			#add words of wisdom from the bulletin creator
			elif bulletin.helpbulletin and len(message) <= 200:
				bulletin.advice = message
				bulletin.save()
		
		#re-render form with update values 
		else: return HttpResponseRedirect('/bulletin/%d/' % bulletin.id)

	#direct users who did not create the bulletin to the public bulletin page
	else: return HttpResponseRedirect('/bulletin/%d/' % bulletin.id)
	return HttpResponseRedirect('/home/');

def filterSuggestions(request):

	if request.method == "POST": 
		form = FilterSuggestionForm(request.POST)
		if form.is_valid:

			#capture form data
			filterName = request.POST.get('filterName', '')

			#send anonymous message to admins to consider updating filter list
			subject = "New Filter: "+filterName+"?"
			message = subject
			send_mail(subject, message, 'allevitan@gmail.com',
			['allevitan@gmail.com'], fail_silently=False)
			return HttpResponseRedirect('/editProfile/')

	#initial page render
	if request.user.is_authenticated():
		form = FilterSuggestionForm()
		return render(request, 'filterSuggestions.html', {'form': form})
	else: HttpResponseRedirect('/login/')
		

def contact(request):
	if request.method == 'POST':
		form = ContactForm(request.POST)
		if form.is_valid():

			#send message using POST data
			cleaned_data = form.clean()
			subject = cleaned_data['subject']
			message = cleaned_data['message']
			toAddress = cleaned_data['emailAddress']
			send_mail(subject, message, 'allevitan@gmail.com',
    ['allevitan@gmail.com'], fail_silently=False)
			return HttpResponseRedirect('/')

	#initial page render
	elif request.user.is_active and request.user.is_authenticated():
		data = {'emailAddress':request.user.email}
		form = ContactForm(initial=data)
		return render(request, 'contact.html', {'form':form})

	#redirect to login page if user is not authenticated
	else: return HttpResponseRedirect('/login/')
	
