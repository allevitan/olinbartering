#contentview.py
from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.models import User
from forms import ContactForm, PasswordResetForm, selectBulletinForm
from forms import MultiProfileDisplay, SortByFilter
from forms import ReplyForm, UpdateBulletinForm, ResolverCreditForm, FilterSuggestionForm
from models import UserData, Missive, Filter, Bulletin, Reply, Reply_Thread
from django.core.mail import send_mail, EmailMessage
from passgen import generate_password
from datetime import datetime
import re


def about(request):
	return render(request, 'about.html')

def people(request):
	if request.method == 'POST':
		if 'username' in request.POST:
			form = MultiProfileDisplay(request.POST)
			if form.is_valid():
				cleaned_data = form.clean()
				user_name = cleaned_data['username']

				#username follows form "first.last"
				username = '.'.join(user_name.lower().split())
				return HttpResponseRedirect('/profile/'+username+'/')

		elif 'filternames' in request.POST:
			form = SortByFilter(request.POST)
			if form.is_valid():
				try:
					cleaned_data = form.clean()
					filterName = cleaned_data['filternames']
					filterName = re.split(' - ', filterName, 1)
					filterText, filterType = filterName[1], filterName[0]
					chosenFilter = Filter.objects.filter(name=filterText, helpfilter=filterType)
					users = UserData.objects.filter(filters__id=chosenFilter)
					form = MultiProfileDisplay()
					form2 = SortByFilter()
					filterText = "None"
					return render(request, 'MultiProfileDisplay.html', {'users':users, 'form':form, 'filterText': filterText, 'form2':form2})
				except:
					return HttpResponseRedirect('/people/')
	else:

		#query database for list of all users and redisplay the same page.
		users = UserData.objects.all()
		form = MultiProfileDisplay()
		form2 = SortByFilter()
		filterText = "None"
	return render(request, 'MultiProfileDisplay.html', {'users':users, 'form':form, 'filterText': filterText, 'form2':form2})

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
	form = FilterSuggestionForm()
	return render(request, 'filterSuggestions.html', {'form': form})


def contact(request):
	if request.method == 'POST':
		form = ContactForm(request.POST)
		if form.is_valid():

			#send message using POST data
			cleaned_data = form.clean()
			subject = cleaned_data['subject']
			message = cleaned_data['message']
			emailAddress = cleaned_data['emailAddress']
			message = "Filtr Feedback from %s:\n%s"  %(emailAddress,message)
			email = EmailMessage(subject, message, 'olin.filtr@gmail.com', ['allevitan@gmail.com', 'madison.may@students.olin.edu'])
			email.send(fail_silently=False)
			return HttpResponseRedirect('/')

	#initial page render
	form = ContactForm()
	return render(request, 'contact.html', {'form':form})

