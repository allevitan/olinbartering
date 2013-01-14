#userview.py

from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.models import User
from forms import LoginForm, RegistrationForm, EditProfileForm, ChangePasswordForm
from forms import PasswordResetForm, BulletinForm, MissiveForm 
from models import UserData, Missive, Filter, Bulletin
from django.core.mail import send_mail
from passgen import generate_password

def login(request): 
	if request.method == 'POST':  #check to see if form has been submitted
		form = LoginForm(request.POST)  #capture data
		if form.is_valid():  #validate data
			cleaned_data = form.clean()
			username = cleaned_data['username']
   			password = cleaned_data['password']
			if username and password:
				user = auth.authenticate(username=username, password=password)
				if user is not None and user.is_active:
		    		# Correct password, and the user is marked "active"
					auth.login(request, user)
		    		# Render home page.
		    		incorrectPassword = 0
		    		return HttpResponseRedirect('/')
    		else:
        		# Return to login page.
				incorrectPassword = 1
				form = LoginForm()
				return render(request, 'login.html', {'form': form, 'incorrectPassword': incorrectPassword, 'form_error':True})
	
	else:
		incorrectPassword = 0
		form = LoginForm() #reload blank form
	return render(request, 'login.html', {'form': form, 'incorrectPassword': incorrectPassword, 'form_error':False})

def logout(request):
	auth.logout(request) #log user out, no questions asked.
	return HttpResponseRedirect('/')

def passwordsMatch(password, confirmPassword):
	return password == confirmPassword

def uniquename(username):
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
				user.save()
				userdata.save()
				user = auth.authenticate(username=username, password=password)
				auth.login(request, user)
				return HttpResponseRedirect('/')
			else: 
				form = RegistrationForm()
				render(request, 'registration.html', {'form':form})
	else:
		form = RegistrationForm()
	
	return render(request, 'registration.html', {'form':form})

def editProfile(request):	
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login')
	else:
		user = request.user
		userdata = user.userdata
		helpfilters = sorted([filterName for filterName in userdata.filters.all() if filterName.helpfilter], key = lambda x: x.name)
		wantfilters = sorted([filterName for filterName in userdata.filters.all() if not filterName.helpfilter], key = lambda x: x.name)
		data = {'first_name':user.first_name, 'last_name':user.last_name, 'emailAddress':user.email, 'dorm':userdata.dorm}
		form = EditProfileForm(initial = data, user = user)

	return render(request, 'editProfile2.html', {'form':form, 'helpfilters':helpfilters, 'wantfilters':wantfilters})

def editUserProfile(request):	
	if request.method == 'POST':
		form = EditProfileForm(request.POST, request.FILES)
		if form.is_valid():
			cleaned_data = form.clean()
			first_name = cleaned_data['first_name'].strip()
			last_name = cleaned_data['last_name'].strip()
			email = cleaned_data['emailAddress']
			dorm = cleaned_data['dorm']
			pic = request.FILES.get('pic','')
			user = User.objects.get(username = request.user)
			userdata = user.userdata
			if first_name.strip():
				user.first_name = first_name
			if last_name.strip():
				user.last_name = last_name
			if email.strip():
				user.email = email
			if dorm.strip():
				userdata.dorm = dorm
			if pic:
				userdata.pic = pic
			user.save()
			userdata.save()
			return render(request, 'editProfileForm.html', {'form':form})
	else:
		if not request.user.is_authenticated():
			return HttpResponseRedirect('/login')
		else:
			user = request.user
			userdata = user.userdata
			data = {'first_name':user.first_name, 'last_name':user.last_name, 'emailAddress':user.email, 'dorm':userdata.dorm}
			form = UserProfileForm(initial = data)

	return render(request, 'editProfileForm.html', {'form':form})

def editFilters(request):	
	if request.method == 'POST':
		form = EditProfileForm(request.POST, request.FILES)
		if form.is_valid():
			cleaned_data = form.clean()
			user = request.user
			userdata = user.userdata
			helpfilters = sorted([filterName for filterName in userdata.filters.all() if filterName.helpfilter], key = lambda x: x.name)
			wantfilters = sorted([filterName for filterName in userdata.filters.all() if not filterName.helpfilter], key = lambda x: x.name)
			user.save()
			userdata.save()
			form = EditFilterForm(user = user)
			render(request, 'filter.html', {'form':form, 'helpfilters':helpfilters, 'wantfilters':wantfilters})
	else:
		if not request.user.is_authenticated():
			return HttpResponseRedirect('/login')
		else:
			user = request.user
			userdata = user.userdata
			helpfilters = sorted([filterName for filterName in userdata.filters.all() if filterName.helpfilter], key = lambda x: x.name)
			wantfilters = sorted([filterName for filterName in userdata.filters.all() if not filterName.helpfilter], key = lambda x: x.name)
			form = EditFilterForm(user = user)

	return render(request, 'filter.html', {'form':form, 'helpfilters':helpfilters, 'wantfilters':wantfilters})



def changePassword(request):
	if request.method == 'POST':
		form = ChangePasswordForm(request.POST)
		if form.is_valid():
			newpassword = request.POST.get('newPassword', '')
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
			newpassword = generate_password(12)
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

