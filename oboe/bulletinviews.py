from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.models import User
from models import Bulletin, Missive, Filter
from forms import CreateBulletinForm
import datetime

def create(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')
    errors = []
    if request.method == 'POST':
        form = CreateBulletinForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            creator = request.user.userdata
            subject = data['subject']
            reltime = datetime.timedelta(hours=data['hiddenrel'])
            relevance = datetime.datetime.now() + reltime
            location = data['hiddenloc']
            
            if location not in ["NA","EH","WH","AC","CC","MH","LP"]:
                errors.append("that's not a real location")
            
            if data['hiddentype'] == "Help":
                helpbulletin = True
                try: tag = Filter.objects.filter(helpfilter=True).get(name=data['tag'])
                except: errors.append("that tag isn't a help tag")
            elif data['hiddentype'] == "Want":
                helpbulletin = False
                try: tag = Filter.objects.filter(helpfilter=False).get(name=data['tag'])
                except: errors.append("that tag isn't a want tag")
            else: errors.append("that's not a type of bulletin!")

            if data['hiddenprice'] == "Free":
                free = True
            elif data['hiddenprice'] == "Cheap":
                free = False
            else: errors.append("please enter a valid price.")            
            
            message = data['missive']
            
            if not errors:
                bulletin = Bulletin.objects.create(creator=creator, subject=subject, relevance=relevance, location=location, tag=tag, helpbulletin=helpbulletin, free=free)
                bulletin.save()
                missive = Missive.objects.create(message=message, bulletin=bulletin)
                missive.save()
                return HttpResponseRedirect("/home/")
            
        else:
            if not request.POST.get('subject',''):
                errors.append('please enter a subject.')
            if not request.POST.get('missive',''):
                errors.append('please enter a message.')
            if not request.POST.get('tag',''):
                errors.append('please enter a tag.')
    else: form = CreateBulletinForm()
    print errors
    helptags = Filter.objects.filter(helpfilter=True)
    wanttags = Filter.objects.filter(helpfilter=False)
    return render(request, 'create.html', {'form':form, 'helptags':helptags, 'wanttags':wanttags, 'errors':errors})
