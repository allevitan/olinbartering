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
    creator = models.ForeignKey(UserData, related_name="%(class)s_created")
    subject = models.CharField(max_length=50)
    creation = models.DateTimeField(auto_now=False, auto_now_add=True)
    update = models.DateTimeField(auto_now=True, auto_now_add=True)
    relevance = models.DateTimeField(auto_now=False, auto_now_add=False)
    resolved = models.BooleanField()
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
    users = models.ManyToManyField(UserData)
    bulletin = models.ForeignKey(Bulletin)
    update = models.DateTimeField(auto_now=True, auto_now_add=True)

    def __unicode__(self):
        return "%s" % bulletin.subject


class Reply(models.Model):
    thread = models.ForeignKey(Reply_Thread)
    sender = models.ForeignKey(UserData)
    public = models.BooleanField(default=False)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
    
    def __unicode__(self):
        return "%s" % self.message
