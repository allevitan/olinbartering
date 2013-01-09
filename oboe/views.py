from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.models import User
from forms import LoginForm, RegistrationForm, EditProfileForm, ChangePasswordForm
from forms import ContactForm, PasswordResetForm, BulletinForm, MissiveForm, MultiProfileDisplay
from models import UserData, Missive, Filter, Bulletin
from django.core.mail import send_mail
from passgen import generate_password
from datetime import datetime

def home(request):
	if not (request.user.is_authenticated() and request.user.userdata.filterhelp):
		#helps = Help_Bulletin.objects.filter(resolved=False).order_by("-update")
		helps = Bulletin.objects.filter(resolved=False, helpbulletin=True).order_by("-update")
	else:
		helpfilters = request.user.userdata.filters.filter(helpfilter=True)
		helps = Bulletin.objects.filter(resolved=False, helpbulletin=True).filter(tag__in=helpfilters).order_by("-update")
	if not (request.user.is_authenticated() and request.user.userdata.filterwant):	
		wants = Bulletin.objects.filter(resolved=False, helpbulletin=False).order_by("-update")
	else:
		wantfilters = request.user.userdata.filters.filter(helpfilter=False)
		wants = Bulletin.objects.filter(resolved=False, helpbulletin=False).filter(tag__in=wantfilters).order_by("-update")

	return render(request, 'home.html', {'range':range(1, 6), 'helps':helps, 'wants':wants})

def redirecthome(request):
	return HttpResponseRedirect('home/')

def login(request): 
	if request.method == 'POST':  #check to see if form has been submitted
		form = LoginForm(request.POST)  #capture data
		if form.is_valid():  #validate data
			cleaned_data = form.clean()
			username = cleaned_data['username']
   			password = cleaned_data['password']
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
				return render(request, 'login.html', {'form': form, 'incorrectPassword': incorrectPassword})
	else:
		incorrectPassword = 0
		form = LoginForm() #reload blank form
	return render(request, 'login.html', {'form': form, 'incorrectPassword': incorrectPassword})

def logout(request):
	auth.logout(request) #log user out, no questions asked.
	return HttpResponseRedirect('/')

def basetest(request): #test base form
	return render(request, 'base.html')

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
				userdata.pic = pic
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
			return HttpResponseRedirect('/')
	else:
		user = request.user
		userdata = user.userdata
		data = {'first_name':user.first_name, 'last_name':user.last_name, 'emailAddress':user.email, 'dorm':userdata.dorm}
		form = EditProfileForm(initial = data)
	
	return render(request, 'editProfile.html', {'form':form})

def homescreen(request):
	return render(request, 'homescreen.html',  {'range':range(1, 11), 'form':form})

def changePassword(request):
	if request.method == 'POST':
		form = ChangePasswordForm(request.POST)
		if form.is_valid():
			newpassword = request.POST.get('newPassword', '')
			request.user.set_password(newpassword)
			request.user.save()
			return HttpResponseRedirect('successful/')
	else:
		form = ChangePasswordForm()
	
	return render(request, 'changePassword.html', {'form':form})

def passwordChanged(request):
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
			send_mail(subject, message, 'worldpeaceagentforchange@gmail.com',
    ['allevitan@gmail.com', 'madison.may@students.olin.edu'], fail_silently=False)
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

			

		
		
	

