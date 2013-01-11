#forms.py 

from django import forms
from django.db import models
from django.forms import ModelForm
from oboe import pathfinders, models
from django.forms.widgets import SplitDateTimeWidget, SelectMultiple
from models import Filter, Bulletin, UserData
from datetime import datetime, timedelta

class LoginForm(forms.Form):
	username = forms.CharField(required=True, max_length=30)
	password = forms.CharField(widget=forms.PasswordInput())

class RegistrationForm(forms.Form):
	first_name = forms.CharField(max_length=30)
	last_name = forms.CharField(max_length=30)
	emailAddress = forms.EmailField()
	password = forms.CharField(widget=forms.PasswordInput())
	confirmPassword = forms.CharField(widget=forms.PasswordInput())
	dorm = forms.CharField(max_length=5)
	pic = forms.ImageField(required=False)

class EditProfileForm(forms.Form):
	first_name = forms.CharField(max_length=30, required=False)
	last_name = forms.CharField(max_length=30, required=False)
	emailAddress = forms.EmailField(required=False)
	dorm = forms.CharField(max_length=5, required=False)
	pic = forms.ImageField(required=False)

class ChangePasswordForm(forms.Form):
	oldPassword = forms.CharField(widget=forms.PasswordInput())
	newPassword = forms.CharField(widget=forms.PasswordInput())
	confirmPassword = forms.CharField(widget=forms.PasswordInput())

class ContactForm(forms.Form):
	emailAddress = forms.EmailField(required=True)
	subject = forms.CharField(max_length = 60)
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
	relevance = forms.DateTimeField(initial = week.strftime('%m/%d/%Y'))
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

