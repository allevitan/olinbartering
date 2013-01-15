from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import auth
from django.contrib.auth.models import User
from models import Bulletin, Missive, Filter, Reply_Thread, UserData
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
    if len(errors) >= 3:
        errors.append('get your life together.')
    helptags = Filter.objects.filter(helpfilter=True)
    wanttags = Filter.objects.filter(helpfilter=False)
    return render(request, 'create.html', {'form':form, 'helptags':helptags, 'wanttags':wanttags, 'errors':errors})


def resolve(request):
    if request.user.is_authenticated and request.method == 'POST':
        if request.POST.get('thread',''):
            pk = int(request.POST['thread'])
            thread = Reply_Thread.objects.get(pk=pk)
            bulletin = thread.bulletin
            fromthread = True
        else:
            pk = int(request.POST['bulletin'])
            bulletin = Bulletin.objects.get(pk=pk)
            fromthread = False
        if bulletin.helpbulletin:
            if bulletin.resolved:
                return HttpResponse('Nothing Happened')
            else:
                if fromthread:
                    resolver = thread.users.exclude(user=request.user).get()
                else:
                    resolver = request.POST['username']
                    resolver = '.'.join(resolver.lower().split())
                    resolver = User.objects.get(username=resolver).userdata
                bulletin.resolved = True
                bulletin.resolver = resolver
                bulletin.save()
                resolver.score = resolver.score + 1
                resolver.save()
                return HttpResponse('Unresolve')
        else:
           if bulletin.resolved:
                return HttpResponse('Nothing Happened')
           else:
                bulletin.resolved = True
                bulletin.save()
                return HttpResponse('Resolved')
    else:
        return HttpResponseRedirect('/')
