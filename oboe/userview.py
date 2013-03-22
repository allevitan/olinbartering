#userview.py

from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.models import User
from forms import LoginForm, RegistrationForm, ChangePasswordForm
from forms import UserProfileForm, EditFilterForm, ManageFiltersForm
from forms import PasswordResetForm
from models import UserData, Missive, Filter, Bulletin, Reply_Thread
from django.core.mail import send_mail
from passgen import generate_password
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
import requests

@csrf_exempt
def login(request):
    if request.method == 'POST':  #check to see if form has been submitted
        sesh = request.POST.get('sessionid','')
        who = requests.get('http://olinapps.com/api/me?sessionid=%s' % sesh)
        request.session['who'] = who.json().get('user').get('id')
        everybody = requests.get('http://directory.olinapps.com/api/people?sessionid=%s' % sesh).json().get('people')
        peeps = {}
        for person in everybody:
            peeps[person.get('email').split('@')[0]] = person
        cache.set('peeps', peeps)
        return HttpResponseRedirect('/home/')
    else:
        return HttpResponseRedirect('http://olinapps.com/external?callback=http://127.0.0.1:8000/login/')

def logout(request):
	if request.user.is_authenticated():
		auth.logout(request) #log user out, no questions asked.
	return HttpResponseRedirect('/')
	

def passwordsMatch(password, confirmPassword):
	return password == confirmPassword

def uniquename(username):
	#queries database to check for existing entries.
	try: 
		User.objects.get(username=username)
		return False
	except:
		return True

def register(request):	
	if request.method == 'POST':
		form = RegistrationForm(request.POST, request.FILES)
		if form.is_valid():
			cleaned_data = form.clean()
			first_name = cleaned_data['first_name'].strip()
			last_name = cleaned_data['last_name'].strip()
			email = cleaned_data['emailAddress']
			password = cleaned_data['password']
			confirmPassword = cleaned_data['confirmPassword']
			username = ".".join([first_name.lower(), last_name.lower()])
			if passwordsMatch(password, confirmPassword) and uniquename(username):
				dorm = cleaned_data['dorm']
				pic = request.FILES.get('pic','')
				user = User.objects.create_user(username=username, email=email, password=password)
				user.first_name = first_name
				user.last_name = last_name
				userdata = UserData.objects.create(user=user,score=0,dorm=dorm, pic=pic)
				helpmefilter = Filter.objects.get(name = 'Helpme', helpfilter = True)
				carpefilter = Filter.objects.get(name = 'Carpediem', helpfilter = False)
				userdata.filters.add(helpmefilter)
				userdata.filters.add(carpefilter)
				user.save()
				userdata.save()
				#attach previous carpes/helpmes to new user
				linkPrevious(userdata)
				user = auth.authenticate(username=username, password=password)
				auth.login(request, user)
				return HttpResponseRedirect('/link/')
			else: 
				form = RegistrationForm()
				render(request, 'registration.html', {'form':form})
	else:
		form = RegistrationForm()
	
	return render(request, 'registration.html', {'form':form})

def linkOld(request):
	if request.user.is_authenticated:
		if request.method == 'POST' and request.POST['link'] == 'True':
			linkPrevious(request.user.userdata)
			return HttpResponseRedirect('/manageFilters/')
		else: return render(request, 'linkPrevious.html')
	return HttpResponseRedirect('/home/')

def editProfile(request):	
	if request.user.is_authenticated():
		form =UserProfileForm(request.POST, request.FILES)
		if form.is_valid():
			cleaned_data = form.clean()

			#extract form info (could potentially use .serialize() to remove redundant code)
			first_name = cleaned_data['first_name'].strip()
			last_name = cleaned_data['last_name'].strip()
			email = cleaned_data['emailAddress']
			dorm = cleaned_data['dorm']
			pic = request.FILES.get('pic','')

			#update user fields
			user = User.objects.get(username = request.user)
			userdata = user.userdata
			user.first_name = first_name
			user.last_name = last_name
			user.email = email
			userdata.dorm = dorm

			if pic:
				userdata.pic = pic

			#save results
			user.save()
			userdata.save()

			#resubmit user data to pre-fill form
			data = {'first_name':user.first_name, 'last_name':user.last_name, 'emailAddress':user.email, 'dorm':userdata.dorm}
			form = UserProfileForm(initial=data)
			return render(request, 'editProfile.html', {'form':form})
		else: 

			#if a form error occurs
			user = request.user
			userdata = user.userdata
			
			#re-render the form - the html page will handle the error display
			data = {'first_name':user.first_name, 'last_name':user.last_name, 'emailAddress':user.email, 'dorm':userdata.dorm}
			form = UserProfileForm(initial = data)
			return render(request, 'editProfile.html', {'form':form})
	else:
		return HttpResponseRedirect('/login')

def filterList(request):
	pass

def manageFilters(request):	
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login')
	else:
		user = request.user
		userdata = user.userdata

		#seperate filters and sort by name
		helpfilters = sorted([filterName for filterName in userdata.filters.all() if filterName.helpfilter], key = lambda x: x.name)
		wantfilters = sorted([filterName for filterName in userdata.filters.all() if not filterName.helpfilter], key = lambda x: x.name)

		#generate list of all helpfilters
		globalhelpfilters = set(Filter.objects.filter(helpfilter=True))
		globalwantfilters = set(Filter.objects.filter(helpfilter=False))

		#compute difference (filters user does not have enabled)
		unusedHelpFilters = set(globalhelpfilters - set(helpfilters))
		unusedWantFilters = set(globalwantfilters - set(wantfilters))

		#get user data to pre-fill form with
		form = ManageFiltersForm(user = user)

	return render(request, 'editProfile2.html', {'user':request.user, 'form':form, 'helpfilters':helpfilters, 'wantfilters':wantfilters,
												 'unusedHelpFilters':unusedHelpFilters, 'unusedWantFilters':unusedWantFilters})

@csrf_exempt
def editFilters(request, help=False, delete=False):	
	if request.user.is_authenticated():

		#user data is passed to form for processing - potential violation of MVC philosophy 
		user = request.user
		form = EditFilterForm(user, request.POST, request.FILES)
		if form.is_valid():
			cleaned_data = form.clean()
			user = request.user
			userdata = user.userdata
			try: 
				if help:
					userdata.filters.add(Filter.objects.get(name = request.POST.get('add', ''), helpfilter=True))
				else:
					userdata.filters.add(Filter.objects.get(name = request.POST.get('add', ''), helpfilter=False))	
			except:
				if help: #add a help filter to users ManyToMany field
					userdata.filters.add(Filter.objects.get(name=cleaned_data[u'helptag'], helpfilter=True))
				elif not delete: #add a want filter
					userdata.filters.add(Filter.objects.get(name=cleaned_data[u'wanttag'], helpfilter=False))
				else: #delete a filter
					if request.POST.get('helpfilter', '') == "True":
						helpfilter = True
					else:
						helpfilter = False
					userdata.filters.remove(Filter.objects.get(name = request.POST.get('name', ''), helpfilter=helpfilter))

			#sort the new data
			helpfilters = sorted([filterName for filterName in userdata.filters.all() if filterName.helpfilter], key = lambda x: x.name)
			wantfilters = sorted([filterName for filterName in userdata.filters.all() if not filterName.helpfilter], key = lambda x: x.name)

			#generate list of all helpfilters
			globalhelpfilters = set(Filter.objects.filter(helpfilter=True))
			globalwantfilters = set(Filter.objects.filter(helpfilter=False))

			#compute difference (filters user does not have enabled)
			unusedHelpFilters = set(globalhelpfilters - set(helpfilters))
			unusedWantFilters = set(globalwantfilters - set(wantfilters))
	
			#save changes and render the page again via AJAX call
			user.save()
			userdata.save()
			form = EditFilterForm(user = user)
			return render(request, 'elements/filterSubPage.html', {'form':form, 'helpfilters':helpfilters, 'wantfilters':wantfilters, 
															'unusedHelpFilters':unusedHelpFilters, 'unusedWantFilters':unusedWantFilters})
		else:
			
			#in the event of form errors
			user = request.user
			userdata = user.userdata
			
			#resort filters and render page again with error display
			helpfilters = sorted([filterName for filterName in userdata.filters.all() if filterName.helpfilter], key = lambda x: x.name)
			wantfilters = sorted([filterName for filterName in userdata.filters.all() if not filterName.helpfilter], key = lambda x: x.name)

			#generate list of all helpfilters
			globalhelpfilters = set(Filter.objects.filter(helpfilter=True))
			globalwantfilters = set(Filter.objects.filter(helpfilter=False))

			#compute difference (filters user does not have enabled)
			unusedHelpFilters = set(globalhelpfilters - set(helpfilters))
			unusedWantFilters = set(globalwantfilters - set(wantfilters))

			form = EditFilterForm(user = user)
			return render(request, 'elements/filterSubPage.html', {'form':form, 'helpfilters':helpfilters, 'wantfilters':wantfilters, 
															'unusedHelpFilters':unusedHelpFilters, 'unusedWantFilters':unusedWantFilters})
	else:
			return HttpResponseRedirect('/login')

def editWantFilters(request):
	help = False
	return editFilters(request, help)

def editHelpFilters(request):
	help = True
	return editFilters(request, help)

def delFilters(request):
	help = False
	delete = True
	return editFilters(request, help, delete)

def changePassword(request):
	if request.method == 'POST':
		form = ChangePasswordForm(request.POST)
		if form.is_valid():
			cleaned_data = form.clean()
			newpassword = cleaned_data['newPassword']
			request.user.set_password(newpassword)
			request.user.save()
			return HttpResponseRedirect('successful/')
	else:
		if not request.user.is_authenticated():
			return HttpResponseRedirect('/login')
		form = ChangePasswordForm()
	
	return render(request, 'changePassword.html', {'form':form})

def passwordChanged(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login')
	return render(request, 'passwordChanged.html')

def resetPassword(request):
	if request.method == 'POST':
		form = PasswordResetForm(request.POST)
		if form.is_valid():
			cleaned_data = form.clean()
			email = cleaned_data['emailAddress']
			user = User.objects.get(email = email)

			#generate series of 12 alphanumeric characters to use as temporary password
			newpassword = generate_password(12)

			#save results and send email to user
			user.set_password(newpassword)
			user.save()
			subject = "Password Reset"
			message = "New Password: " + newpassword
			send_mail(subject, message, 'worldpeaceagentforchange@gmail.com', [email], fail_silently=False)

			return HttpResponseRedirect('successful/')
	else:
		form = PasswordResetForm()
	
	return render(request, 'resetPassword.html', {'form': form})

def passwordReset(request):
	return render(request, 'passwordReset.html')

def profilepage(request, username):

	#handle invalid input
	try: user = User.objects.get(username=username.lower())
	except: return HttpResponseRedirect('/people/')

	#generate list of user filters to display in profile page
	filters = user.userdata.filters.all()
	bulletins = sorted(Bulletin.objects.filter(creator=user.userdata), key = lambda bulletin: bulletin.update, reverse=True)
	helpfilters = sorted([filterName.name for filterName in filters.all() if filterName.helpfilter and filterName.name != "Helpme"])
	wantfilters = sorted([filterName.name for filterName in filters.all() if not filterName.helpfilter and filterName.name != "Carpediem"])
	return render(request, 'profilepage.html', {'request': request, 'owner':user, 'bulletins':bulletins, 'helpfilters':helpfilters, 'wantfilters':wantfilters})


def linkPrevious(userdata):
	bulletins = Bulletin.objects.filter(anon=True).filter(anon_email__iexact=userdata.user.email)
	for bulletin in bulletins:
		bulletin.anon = False
		bulletin.creator = userdata
		bulletin.save()
		for thread in bulletin.reply_thread_set.all():
			for reply in thread.reply_set.all():
				if reply.anon:
					reply.anon = False
					reply.sender = userdata
					reply.save()
	threads = Reply_Thread.objects.filter(anon=True).filter(anon_email__iexact=userdata.user.email)
	for thread in threads:
		thread.anon = False
		thread.replier = userdata
		thread.save()
		for reply in thread.reply_set.all():
			if reply.anon:
				reply.anon = False
				reply.sender = userdata
				reply.save()
	return [bulletins.count(), threads.count()]
