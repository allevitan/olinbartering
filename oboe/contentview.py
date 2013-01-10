#contentview.py
from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.models import User
from forms import ContactForm, PasswordResetForm, BulletinForm, MissiveForm, MultiProfileDisplay
from models import UserData, Missive, Filter, Bulletin
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
			if filterText == "None":
				users = UserData.objects.all()
			else:
				chosenFilter = Filter.objects.filter(name=filterText)
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
		if request.user.is_active:
			data = {'emailAddress':request.user.email, 'subject':"Nice site!"}
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
		if form.is_valid():
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
					location = location, relevance = relevance,
					resolved=False, reply_count = 0,
                                        free=price, tag=bulletinFilter)
			elif bulletinType == "Help?":
				bulletinFilter = getFilter(filters, helpfilter=True)
				bulletin = Bulletin.objects.create(creator = userdata, subject = subject,
					location = location, relevance = relevance, 
					resolved=False, reply_count = 0,
					tag=bulletinFilter)
			else:
				raise ValidationError
			missive = Missive.objects.create(bulletin = bulletin, timestamp = datetime.now(), 
				message = message)
			bulletin.save()
			missive.save()
			return HttpResponseRedirect('/')
	else:
		form = BulletinForm()
	
	return render(request, 'addBulletin.html', {'form':form})

def selectBulletin(request):	
	if request.method == 'POST':
		bulletins = set((bulletin.subject, bulletin.subject) for bulletin in Bulletin.objects.filter(creator=request.user.userdata))
		form = selectBulletinForm(request.POST or None, request.FILES, bulletins=bulletins)
		if form.is_valid():
			cleaned_data = form.clean()
			user = User.objects.get(username = request.user)
			userdata = user.userdata
			bulletin = Bulletin.objects.get(subject=subject)
			missive.save()
			return HttpResponseRedirect('/')
	else:
		bulletins = set((bulletin.subject, bulletin.subject) for bulletin in Bulletin.objects.filter(creator=request.user.userdata))
		form = selectBulletinForm(request.POST or None, bulletins=bulletins)
	return render(request, 'newMissive.html', {'form':form})


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
			missive = Missive.objects.create(bulletin = bulletin, timestamp = datetime.now(), message = message)
			missive.save()
			return HttpResponseRedirect('/')
	else:
		bulletins = set((bulletin.subject, bulletin.subject) for bulletin in Bulletin.objects.filter(creator=request.user.userdata))
		form = MissiveForm(request.POST or None, bulletins=bulletins)
	
	return render(request, 'newMissive.html', {'form':form})
