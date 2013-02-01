#forms.py 

from django import forms
from django.db import models
from django.forms import ModelForm
from oboe import pathfinders, models
from django.forms.widgets import SplitDateTimeWidget, SelectMultiple, Select
from models import Filter, Bulletin, UserData
from datetime import datetime, timedelta
from django.utils.safestring import mark_safe 

class LoginForm(forms.Form):
	username = forms.CharField(required=True, max_length=30, widget=forms.TextInput(attrs={'placeholder': 'Username or email address...'}))
	password = forms.CharField(widget=forms.PasswordInput(attrs={}))


class RegistrationForm(forms.Form):
	first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder': 'Franklin'}))
	last_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder': 'Olin'}))
	emailAddress = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'franklin.olin@students.olin.edu'}))
	password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': '********'}))
	confirmPassword = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': '********'}))
	dorm = forms.CharField(max_length=5, widget=forms.TextInput(attrs={'placeholder': 'WH101'}))
	pic = forms.ImageField(required=False) #pic is the only form field not required


class UserProfileForm(forms.Form):
	first_name = forms.CharField(max_length=30)
	last_name = forms.CharField(max_length=30)
	emailAddress = forms.EmailField()
	dorm = forms.CharField(max_length=5)
	pic = forms.ImageField(required=False)

class EditFilterForm(forms.Form):

	def genFilters(self):
		'''genFilters returns a formatted list of filters that the user does not have enabled'''

		#basic database query for user's enable filters
		userFilters = self._user.userdata.filters.all()  

		#divide the filters into categories (help & want) and access name attribute -- then convert to string
		userHelpFilters = set([str(userHelpFilter.name) for userHelpFilter in userFilters if userHelpFilter.helpfilter])
		userWantFilters = set([str(userWantFilter.name) for userWantFilter in userFilters if not userWantFilter.helpfilter])
		
		#get list of all existing filters
		filters = Filter.objects.all()

		#divide all existing filters into categories (help & want) and access name attribute -- then convert to string
		helpFilters = set([str(filterName.name) for filterName in filters if filterName.helpfilter])
		wantFilters = set([str(filterName.name)  for filterName in filters if not filterName.helpfilter])

		#perform set subtraction to generate the desired list of unenabled filters
		helpFilters = helpFilters - userHelpFilters
		wantFilters = wantFilters - userWantFilters
	
		#convert to list and return result
		return list(helpFilters), list(wantFilters)
		
	def __init__(self, user, *args, **kwargs):
		#__init__ method override needed to pass data from view to form (in this case, the variable user)
		super(EditFilterForm, self).__init__(*args, **kwargs)
		self._user = user
		helpFilters, wantFilters = self.genFilters()
		
		#mark_safe and .replace method needed to override html formatting
		self.fields['wanttag'] = forms.CharField(widget=forms.TextInput(attrs={'data-provide':'typeahead', 'autocomplete':'off',\
								'placeholder':'Tag...', 'data-source': mark_safe(wantFilters).replace("'", '"')}), required=False) 
		self.fields['helptag'] = forms.CharField(widget=forms.TextInput(attrs={'data-provide':'typeahead', 'autocomplete':'off',\
								'placeholder':'Tag...', 'data-source': mark_safe(helpFilters).replace("'", '"')}), required=False)

class ManageFiltersForm(EditFilterForm):
	pass
	
class ChangePasswordForm(forms.Form):
	oldPassword = forms.CharField(widget=forms.PasswordInput())
	newPassword = forms.CharField(widget=forms.PasswordInput())
	confirmPassword = forms.CharField(widget=forms.PasswordInput())

class ContactForm(forms.Form):
	emailAddress = forms.EmailField(widget=forms.TextInput(attrs = {'placeholder':"Email...", 'size':'20'}))
	subject = forms.CharField(max_length = 60, widget=forms.TextInput(attrs={'placeholder': 'Subject...', 'size':'20'}))
	message = forms.CharField(widget=forms.Textarea(attrs={'class':"row-fluid", 'placeholder':"Message..."}))

class PasswordResetForm(forms.Form):
	emailAddress = forms.EmailField()

class MultiProfileDisplay(forms.Form):

	users = [str(user) for user in UserData.objects.all()]
	username = forms.CharField(widget=forms.TextInput(attrs={'data-provide':'typeahead', 'autocomplete':'off','placeholder':'Search by username...', 'data-source': mark_safe(users).replace("'", '"')}))

class SortByFilter(forms.Form):

	helpfilters = [str("Help" + ' - ' + filterName.name) for filterName in Filter.objects.all() if filterName.helpfilter and filterName.name != "Helpme"] 
	wantfilters = [str("Want" + ' - ' + filterName.name) for filterName in Filter.objects.all() if not filterName.helpfilter and filterName.name != "Carpediem"]
	filters = helpfilters + wantfilters

	filternames = forms.CharField(widget=forms.TextInput(attrs={'data-provide':'typeahead', 'autocomplete':'off','placeholder':'Search by filter...', 'data-source': mark_safe(filters).replace("'", '"')}))

	#Has potential for future use in a FilterDisplay class
	'''
	filters = Filter.objects.all()
	filters = set((filterName.name, filterName.name) for filterName in filters)
	filters = list(filters)
	filters.sort()
	filters = [("None", "None")] + filters
	filters = forms.ChoiceField(choices=(filters))
	filterType = forms.ChoiceField(choices=(
				(False, "Do you want?"),
				(True, "Can you help?"),
				))
	'''

class selectBulletinForm(forms.Form):
	
	#__init__ overriding is again used to allow the use of request data
	def __init__(self, *args, **kwargs):
		bulletins = kwargs.pop('bulletins')
		super(selectBulletinForm, self).__init__(*args, **kwargs)
		self.fields['bulletin'] = forms.ChoiceField(choices=(bulletins))

class ReplyForm(forms.Form):
	message = forms.CharField(widget=forms.Textarea(attrs={'placeholder':'Reply...'}))

class UpdateBulletinForm(forms.Form):
	missive = forms.CharField(widget=forms.Textarea(attrs={'placeholder':"You've changed..."}))

class CreateBulletinForm(forms.Form):
	subject = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'autocomplete':'off', 'placeholder':'Subject...','class':'textsharp'}))
	tag = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'autocomplete':'off','placeholder':'Tag...','class':'textsharp'}))
	missive = forms.CharField(widget=forms.Textarea(attrs={'placeholder':'Message...','class':'textsharp'}))
	hiddensend = forms.CharField(widget=forms.HiddenInput(attrs={'value':'True'}))
	hiddentype = forms.CharField(widget=forms.HiddenInput(attrs={'value':'Help'}))
	hiddenloc = forms.CharField(widget=forms.HiddenInput(attrs={'value':'NA'}))
	hiddenrel = forms.IntegerField(min_value=2, max_value=96, widget=forms.HiddenInput(attrs={'value':24}))
	hiddenprice = forms.CharField(max_length=5, widget=forms.HiddenInput(attrs={'value':'Free'}))

class ResolverCreditForm(forms.Form):
	users = [str(user) for user in UserData.objects.all()]
	username = forms.CharField(widget=forms.TextInput(attrs={'data-provide':'typeahead', 'autocomplete':'off','placeholder':'Thank someone...', 'data-source': mark_safe(users).replace("'", '"')}))

class FilterSuggestionForm(forms.Form):
	filterName = forms.CharField()
