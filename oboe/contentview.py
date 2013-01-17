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
	if request.user.is_authenticated():
		return render(request, 'about.html')
	else:
		return HttpResponseRedirect('/login/')

def people(request):
	if request.user.is_authenticated():
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
	else:
		return HttpResponseRedirect('/login/')

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
	
