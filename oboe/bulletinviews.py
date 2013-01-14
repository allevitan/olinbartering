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
                errors.append("Error: Not a real location")
            try: tag = Filter.objects.get(name=data['tag'])
            except: errors.append("Error: Not a real tag")
            
            if data['hiddentype'] == "Help":
                helpbulletin = True
            elif data['hiddentype'] == "Want":
                helpbulletin = False
            else: errors.append("Error: Not a type of bulletin")

            if data['hiddenprice'] == "Free":
                free = True
            elif data['hiddenprice'] == "Cheap":
                free = False
            else: errors.append("Error: Not a valid price")            
            
            message = data['missive']
            
            if not errors:
                bulletin = Bulletin.objects.create(creator=creator, subject=subject, relevance=relevance, location=location, tag=tag, helpbulletin=helpbulletin, free=free)
                bulletin.save()
                missive = Missive.objects.create(message=message, bulletin=bulletin)
                missive.save()
                return HttpResponseRedirect("/home/")
            
    else: form = CreateBulletinForm()
    helptags = Filter.objects.filter(helpfilter=True)
    wanttags = Filter.objects.filter(helpfilter=False)
    return render(request, 'create.html', {'form':form, 'helptags':helptags, 'wanttags':wanttags, 'errors':errors})
