#forms.py 

from django import forms
from django.db import models
from django.forms import ModelForm
from oboe import pathfinders, models
from django.forms.widgets import SplitDateTimeWidget, SelectMultiple, Select
from models import Filter, Bulletin, UserData
from datetime import datetime, timedelta



class LoginForm(forms.Form):
	username = forms.CharField(required=True, max_length=30, widget=forms.TextInput(attrs={'placeholder': 'first.last'}))
	password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': '********'}))

class RegistrationForm(forms.Form):
	first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder': 'Franklin'}))
	last_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder': 'Olin'}))
	emailAddress = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'franklin.olin@students.olin.edu'}))
	password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': '********'}))
	confirmPassword = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': '********'}))
	dorm = forms.CharField(max_length=5, widget=forms.TextInput(attrs={'placeholder': 'WH101'}))
	pic = forms.ImageField(required=False)

class EditProfileForm(forms.Form):
	
	def genUserFilters(self):
		userFilters = self._user.userdata.filters.all()
		userHelpFilters = set([(userHelpFilter.name, userHelpFilter.name) for userHelpFilter in userFilters if userHelpFilter.helpfilter])
		userWantFilters = set([(userWantFilter.name, userWantFilter.name) for userWantFilter in userFilters if not userWantFilter.helpfilter])
		filters = Filter.objects.all()
		helpFilters = set([(filterName.name, filterName.name) for filterName in filters if filterName.helpfilter])
		helpFilters = helpFilters-userHelpFilters
		wantFilters = set([(filterName.name, filterName.name) for filterName in filters if not filterName.helpfilter])
		wantFilters = wantFilters - userWantFilters
		return helpFilters, wantFilters
		
	def __init__(self, user=None, *args, **kwargs):
		super(EditProfileForm, self).__init__(*args, **kwargs)
		self._user = user
		helpFilters, wantFilters = self.genUserFilters()
		self.fields['addWantFilter'] = forms.ChoiceField(choices=(wantFilters))
		self.fields['addHelpFilter'] = forms.ChoiceField(choices=(helpFilters))
		
	first_name = forms.CharField(max_length=30)
	last_name = forms.CharField(max_length=30)
	emailAddress = forms.EmailField()
	dorm = forms.CharField(max_length=5)
	pic = forms.ImageField(required=False)

class UserProfileForm(forms.Form):
		
	first_name = forms.CharField(max_length=30)
	last_name = forms.CharField(max_length=30)
	emailAddress = forms.EmailField()
	dorm = forms.CharField(max_length=5)
	pic = forms.ImageField(required=False)

class EditFilterForm(forms.Form):

	def genUserFilters(self):
		userFilters = self._user.userdata.filters.all()
		userHelpFilters = set([(userHelpFilter.name, userHelpFilter.name) for userHelpFilter in userFilters if userHelpFilter.helpfilter])
		userWantFilters = set([(userWantFilter.name, userWantFilter.name) for userWantFilter in userFilters if not userWantFilter.helpfilter])
		filters = Filter.objects.all()
		helpFilters = set([(filterName.name, filterName.name) for filterName in filters if filterName.helpfilter])
		helpFilters = helpFilters-userHelpFilters
		wantFilters = set([(filterName.name, filterName.name) for filterName in filters if not filterName.helpfilter])
		wantFilters = wantFilters - userWantFilters
		return helpFilters, wantFilters
		
	def __init__(self, user, *args, **kwargs):
		super(EditFilterForm, self).__init__(*args, **kwargs)
		self._user = user
		print user
		helpFilters, wantFilters = self.genUserFilters()
		self.fields['addWantFilter'] = forms.ChoiceField(choices=(wantFilters))
		self.fields['addHelpFilter'] = forms.ChoiceField(choices=(helpFilters))
		
class ChangePasswordForm(forms.Form):
	oldPassword = forms.CharField(widget=forms.PasswordInput())
	newPassword = forms.CharField(widget=forms.PasswordInput())
	confirmPassword = forms.CharField(widget=forms.PasswordInput())

class ContactForm(forms.Form):
	emailAddress = forms.EmailField(required=True)
	subject = forms.CharField(max_length = 60, widget=forms.TextInput(attrs={'placeholder': 'Nice Site!'}))
	message = forms.CharField(widget=forms.Textarea(attrs={'class': "row-fluid", 'rows': 10}))

class PasswordResetForm(forms.Form):
	emailAddress = forms.EmailField()

class BulletinForm(forms.Form):
	filters = Filter.objects.all()
	filters = set((filterName.name, filterName.name) for filterName in filters)
	bulletinType = forms.ChoiceField(choices=(
			('Help?', 'Can you help?'),
			('Want?', 'Do you want?'),
			))
	price = forms.ChoiceField(choices=(
			('Free', 'Free'),
			('Cheap', 'Cheap'),
			))
	subject = forms.CharField(max_length=50)
	message = forms.CharField(widget=forms.Textarea(attrs={'class': "span3", 'rows': 5}))
	week = datetime.now() + timedelta(7)
	relevance = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'placeholder':'01/01/01 12:00'}), initial = week.strftime('%m/%d/%Y'))
	location = forms.ChoiceField(choices=(
			('NA','Not Applicable'),
            ('AC','Academic Center'),
            ('CC','Campus Center'),
            ('EH','East Hall'),
            ('LP','Large Project Building'),
            ('MH','Milas Hall'),
            ('WH','West Hall')
            ))
	filters = forms.ChoiceField(choices=(filters))

class MissiveForm(forms.Form):
	price = forms.ChoiceField(choices=(
			('Free', 'Free'),
			('Cheap', 'Cheap'),
			))
	message = forms.CharField(widget=forms.Textarea(attrs={'class': "span3", 'rows': 10}))

	def __init__(self, *args, **kwargs):
		bulletins = kwargs.pop('bulletins')
		super(MissiveForm, self).__init__(*args, **kwargs)
		self.fields['bulletin'] = forms.ChoiceField(choices=(bulletins))

class MultiProfileDisplay(forms.Form):
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

class selectBulletinForm(forms.Form):
	def __init__(self, *args, **kwargs):
		bulletins = kwargs.pop('bulletins')
		super(selectBulletinForm, self).__init__(*args, **kwargs)
		self.fields['bulletin'] = forms.ChoiceField(choices=(bulletins))

class ReplyForm(forms.Form):
	message = forms.CharField(widget=forms.Textarea())

class UpdateBulletinForm(forms.Form):
	missive = forms.CharField(widget=forms.Textarea())

class CreateBulletinForm(forms.Form):
	subject = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'autocomplete':'off', 'placeholder':'Subject...','class':'textsharp'}))
	tag = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'autocomplete':'off','placeholder':'Tag...','class':'textsharp'}))
	missive = forms.CharField(widget=forms.Textarea(attrs={'placeholder':'Message...','class':'sharp'}))
        hiddentype = forms.CharField(widget=forms.HiddenInput(attrs={'value':'Help'}))
	hiddenloc = forms.CharField(widget=forms.HiddenInput(attrs={'value':'NA'}))
        hiddenrel = forms.IntegerField(min_value=2, max_value=96, widget=forms.HiddenInput(attrs={'value':24}))
	hiddenprice = forms.CharField(max_length=5, widget=forms.HiddenInput(attrs={'value':'Free'}))
