#The django models for OBOE

from django.db import models
from django.contrib.auth.models import User
import pathfinders

class Filter(models.Model):
	name = models.CharField(max_length=20)
	helpfilter = models.BooleanField(choices=(
	    (True, 'Help'),
	    (False, 'Want')))

	def __unicode__(self):
		return self.name


class UserData(models.Model):
	user = models.OneToOneField(User)
	score = models.IntegerField()
	dorm = models.CharField(max_length=5)
	pic = models.ImageField(upload_to=pathfinders.create_profpic_path, blank=True)

	filters = models.ManyToManyField(Filter, blank=True)

	filterhelp = models.BooleanField(default=True);
	filterwant = models.BooleanField(default=True);
	includehelpme = models.BooleanField(default=False);
	includecarpe = models.BooleanField(default=False);

	def __unicode__(self):
		return "%s %s" %( self.user.first_name, self.user.last_name)


class Bulletin(models.Model):
	creator = models.ForeignKey(UserData, related_name="%(class)s_created", blank=True, null=True)
	subject = models.CharField(max_length=50)
	creation = models.DateTimeField(auto_now=False, auto_now_add=True)
	update = models.DateTimeField(auto_now=True, auto_now_add=True)
	relevance = models.DateTimeField(auto_now=False, auto_now_add=False)
	resolved = models.BooleanField(default=False)
	location = models.CharField(max_length=2,choices=(
	    ('AC','Academic Center'),
	    ('CC','Campus Center'),
	    ('EH','East Hall'),
	    ('LP','Large Project Building'),
	    ('MH','Milas Hall'),
	    ('NA','Not Applicable'),
	    ('WH','West Hall')
	    ))
	reply_count = models.IntegerField(default=0)
	tag = models.ForeignKey(Filter)

	helpbulletin = models.BooleanField(choices=(
	    (True, 'Help'),
	    (False, 'Want')))

    #Help Specific Fields
	resolver = models.ForeignKey(UserData, null=True, blank=True, related_name="%(class)s_resolved")
	advice = models.CharField(max_length=200, blank=True)

	#Want Specific Fields
	free = models.BooleanField(choices=(
	    (True,'Free'),
	    (False,'Cheap')))

	anon = models.BooleanField(default=False)

	anon_email = models.EmailField(blank=True)
	anon_name = models.CharField(max_length=75, default="", blank="True")

	def get_creator_name(self):
		if self.anon:
			if self.anon_name != "":
				return self.anon_name
			else: 
				return self.anon_email
		else:
			if self.creator:
				return self.creator.__unicode__()
			else: 
				return "Franklin W. Olin's Ghost"

	def get_creator_first_name(self):
		if self.anon:
			if self.anon_name != "":
				return self.anon_name.split(" ")[0]
			else: 
				return self.anon_email.split("@")[0]
		else: 
			if self.creator:
				return self.creator.__unicode__().split(" ")[0]
			else: 
				return "Franklin W. Olin's Ghost"

	def get_creator_email(self):
		if self.anon:
			return self.anon_email
		else:
			if self.creator:
				return self.creator.user.email
			else: 
				return None

	def get_absolute_url(self):
		return "/bulletin/%d/" % self.id

	def __unicode__(self):
		return self.subject

class Missive(models.Model):
	timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
	message = models.TextField()
	bulletin = models.ForeignKey(Bulletin)


	def __unicode__(self):
		return self.message


class Image(models.Model):
	image = models.ImageField(upload_to=pathfinders.create_missivepic_path)
	missive = models.ForeignKey(Missive)

	def __unicode__(self):
		return '%s_pic' % self.missive.subject

class Reply_Thread(models.Model):
	bulletin = models.ForeignKey(Bulletin)
	replier = models.ForeignKey(UserData, blank=True, null=True)
	update = models.DateTimeField(auto_now=True, auto_now_add=True)
	anon = models.BooleanField(default=False)

    #only used if there's an anonymous user
	anon_email = models.EmailField(blank=True)
	anon_name = models.CharField(max_length=75, blank=True)

	def get_replier_name(self):
		if self.anon:
			if self.anon_name:
				return self.anon_name
			else: 
				return self.anon_email
		else:
			if self.replier:
				return self.replier.__unicode__()
			else: 
				return "Franklin W. Olin's Ghost"

	def get_replier_first_name(self):
		if self.anon:
			if self.anon_name:
				return self.anon_name.split(" ")[0]
			else: 
				return self.anon_email.split("@")[0]
		else:
			if self.replier:
				return self.replier.__unicode__().split(" ")[0]
			else: 
				return "Franklin's Ghost"

	def get_creator_name(self):
		return self.bulletin.get_creator_name()

	def get_creator_first_name(self):
		return self.bulletin.get_creator_first_name()

	def __unicode__(self):
		return "%s" % self.bulletin

    anon_email = models.EmailField(blank=True)
    anon_name = models.CharField(max_length=75, blank=True)

   

class Reply(models.Model):
    thread = models.ForeignKey(Reply_Thread)
    sender = models.ForeignKey(UserData, blank=True, null=True)
    public = models.BooleanField(default=False)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
    read = models.BooleanField(default=False)

    #whether or not this is from the anonymous user
    anon = models.BooleanField(default=False)
    
    def get_replier_name(self):
        if self.anon and self.thread.anon:
            return self.thread.get_replier_name()
        elif self.anon and not self.thread.anon():
            return self.thread.get_creator_name()
        else: return self.sender.__unicode__()
    
    def get_to_email(self):
        if self.anon and self.thread.anon:
            return self.thread.get_creator_email()
        elif self.anon and not self.thread.anon: 
            return self.thread.get_replier_email()
        elif self.thread.anon:
            return self.thread.get_creator_email()
        elif self.sender == self.thread.replier:
            return self.thread.get_creator_email()
        else: return self.get_replier_email()
    
    def __unicode__(self):
		return "%s" % self.message

