#userview.py

from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from forms import UserProfileForm, EditFilterForm, ManageFiltersForm
from models import UserData, Missive, Filter, Bulletin, Reply_Thread
from django.core.mail import send_mail
from passgen import generate_password
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
import requests

@csrf_exempt
def login(request):

    if request.method == 'POST':  #check to see if we've logged in

        #Find the session ID from olinapps
        sesh = request.POST.get('sessionid','')

        #Figure out who we are and store it
        who = requests.get('http://olinapps.com/api/me?sessionid=%s' % sesh)
        request.session['who'] = who.json().get('user').get('id')

        #Get the data on everyone and cache it
        everybody = requests.get('http://directory.olinapps.com/api/people?sessionid=%s' % sesh).json().get('people')
        peeps = {}
        for person in everybody:
            uid = person.get('email').split('@')[0]
            peeps[uid] = person
            if UserData.objects.filter(uid = uid).count() == 0:
                dude = UserData.objects.create(uid=uid,score=0)
                print dude.name
        cache.set('peeps', peeps)

        #Now that we know their in our database, get the pk
        request.session['pk'] = UserData.objects.get(uid = request.session['who']).pk
        #And match the expiry to olinapps
        request.session.set_expiry(0)



        return HttpResponseRedirect('/home/')
    else:
        return HttpResponseRedirect('http://olinapps.com/external?callback=http://127.0.0.1:8000/login/')

def logout(request):
    #Make it do something!
    return HttpResponseRedirect('/')

def filterList(request):
	pass

def manageFilters(request):

	userdata = UserData.objects.get(uid = request.session['who'])

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
	form = ManageFiltersForm(user = userdata)

	return render(request, 'editProfile2.html', {'user': userdata, 'form':form, 'helpfilters':helpfilters, 'wantfilters':wantfilters,
												 'unusedHelpFilters':unusedHelpFilters, 'unusedWantFilters':unusedWantFilters})

@csrf_exempt
def editFilters(request, help=False, delete=False):
	#user data is passed to form for processing - potential violation of MVC philosophy
	userdata = UserData.objects.get(uid=request.session['who'])
	form = EditFilterForm(userdata, request.POST, request.FILES)
	if form.is_valid():
		print 'Valid Form'
		cleaned_data = form.clean()
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
		userdata.save()
		form = EditFilterForm(user = userdata)
		return render(request, 'elements/filterSubPage.html', {'form':form, 'helpfilters':helpfilters, 'wantfilters':wantfilters,
														'unusedHelpFilters':unusedHelpFilters, 'unusedWantFilters':unusedWantFilters})
	else:
		print 'Invalid Form'

		#in the event of form errors
		userdata = UserData.objects.get(uid=request.session['who'])

		#resort filters and render page again with error display
		helpfilters = sorted([filterName for filterName in userdata.filters.all() if filterName.helpfilter], key = lambda x: x.name)
		wantfilters = sorted([filterName for filterName in userdata.filters.all() if not filterName.helpfilter], key = lambda x: x.name)

		#generate list of all helpfilters
		globalhelpfilters = set(Filter.objects.filter(helpfilter=True))
		globalwantfilters = set(Filter.objects.filter(helpfilter=False))

		#compute difference (filters user does not have enabled)
		unusedHelpFilters = set(globalhelpfilters - set(helpfilters))
		unusedWantFilters = set(globalwantfilters - set(wantfilters))

		form = EditFilterForm(user = userdata)
		return render(request, 'elements/filterSubPage.html', {'form':form, 'helpfilters':helpfilters, 'wantfilters':wantfilters,
														'unusedHelpFilters':unusedHelpFilters, 'unusedWantFilters':unusedWantFilters})

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

def profilepage(request, username):

	#handle invalid input
	try: user = UserData.objects.get(uid=request.session['who'])
	except: return HttpResponseRedirect('/people/')

	print user
	#generate list of user filters to display in profile page
	filters = user.filters.all()
	bulletins = sorted(Bulletin.objects.filter(creator=user), key = lambda bulletin: bulletin.update, reverse=True)
	helpfilters = sorted([filterName.name for filterName in filters.all() if filterName.helpfilter and filterName.name != "Helpme"])
	wantfilters = sorted([filterName.name for filterName in filters.all() if not filterName.helpfilter and filterName.name != "Carpediem"])
	return render(request, 'profilepage.html', {'request': request, 'owner':user, 'bulletins':bulletins, 'helpfilters':helpfilters, 'wantfilters':wantfilters})
