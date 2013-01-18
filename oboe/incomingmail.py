from inbound import PostmarkInbound
import json as simplejson
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from models import Filter, Bulletin, Missive, Reply, Reply_Thread, UserData
import datetime
import re

@csrf_exempt
def standard_reply(request):
	if request.method == 'POST':
		inbound = PostmarkInbound(json = request.raw_past_data)
		if mailinglist(inbound):
			return mailinglist_process(inbound)
		else:
			return process(inbound)

def mailinglist(inbound):
	'''Check to see if email originated in carpe or helpme'''
	return "[Carpe]" in inbound.subject() or "[Helpme]" in inbound.subject()

def mailinglist_process(inbound):
	'''Process helpme's and carpe's'''
	if "[Carpe]" in subject:
		return handle_mailing_list(False, inbound)					
	else:
		return handle_mailing_list(True, inbound)

def basic_info(inbound):
	subject = inbound.subject()	
	sender = inbound.sender()#need to convert to userdata instance
	timestamp = datetime.datetime.now()
	message = inbound.text_body()
	return subject, sender, timestamp, message

def generate_name(sender):
	email_halves = re.split(r'\@', sender)
	name = email_halves[0]
	names = re.split(r'\.', name)
	name = ' '.join([name.title() for name in names])
	return name

def handle_mailing_list(helpfilter, inbound):
	#Assign to mailing list
	if helpfilter: mailing_list = 'Helpme'
	else: mailing_list = 'Carpe'
	
	if "Re: " in subject:
		send_reply(inbound, mailing_list)
	else:
		send_bulletin(inbound, mailing_list)

def send_reply(inbound, mailing_list):
	#send reply
	subject, sender, timestamp, message = basic_info(inbound)

	#remove tag from subject line
	regex = r'\[' + mailing_list + '\] '
	subject = re.sub(regex, '', subject)

	#remove "Re:" from subject line
	bulletin_subject = re.sub(r'Re\:', '', subject)	

	#remove everything but latest response
	reply_end = message.find('From:')
	message = message[:reply_end-1]	
	
	#find bulletin and reply_thread in database that match email title
	bulletin = Bulletin.objects.get(subject = bulletin_subject, helpbulletin = helpfilter)
	reply_thread = Reply_Thread.objects.get(bulletin = bulletin)

	try:
		#does user exist?
		user = user.objects.get(email = sender)
		userdata = user.userdata

		#create new reply object
		reply = Reply.objects.create(thread = reply_thread, sender = userdata, public = True, 
									 timestamp = timestamp, message = message)
		reply.save()

	except:
		#user does not exist - generate basic info for reply
		name = generate_name(sender)
	
		reply = Reply.objects.create(thread = reply_thread, name = name, email = sender, public = True, 
									 timestamp = timestamp, message = message)

		reply.save()

def send_bulletin(inbound, mailing_list):
	subject, sender, timestamp, message = basic_info(inbound)

	#remove tag from subject line
	regex = r'\[' + mailing_list + '\] '
	subject = re.sub(regex, '', subject)

	#send bulletin
	tag = match_filter(subject, helpfilter)
	relevance = datetime.datetime.now() + datetime.timedelta(7)

	#generate new bulletin
	if helpfilter:

		try:
			#does user exist?
			user = user.objects.get(email = sender)
			userdata = user.userdata

			bulletin = Bulletin.objects.create(subject = subject, creation = timestamp, relevance = relevance,
											   location = 'NA', tag = tag, creator = userdata)
			bulletin.save()
		
		except:
			name = generate_name(sender)

			bulletin = Bulletin.objects.create(subject = subject, creation = timestamp, relevance = relevance,
												location = 'NA', tag = tag, name=name, email=sender)

	else:
		
		try:
			#does user exist?
			user = user.objects.get(email = sender)
			userdata = user.userdata

			bulletin = Bulletin.objects.create(subject = subject, creation = timestamp, relevance = relevance,
											   location = 'NA', tag = tag, creator = userdata, free=False)
			bulletin.save()
		
		except:
			name = generate_name(sender)

			bulletin = Bulletin.objects.create(subject = subject, creation = timestamp, relevance = relevance,
												location = 'NA', tag = tag, name=name, email=sender, free=False)
	

def match_filter(subject, helpfilter):
	#search for a matching filter if filter does not exist
	for word in subject.split():
		try:
			#return tag
			tag = Filter.objects.get(name = word.title(), helpfilter=helpfilter)
			return tag
		except:
			pass
	#Nothing is found, return None
	return 'None'

def process(inbound):

	timestamp = datetime.datetime.now()
	message = inbound.text_body()

	#remove "Re:" from subject line
	bulletin_subject = re.sub(r'Re\:', '', subject)	

	#remove everything but latest response
	reply_end = message.find('From:')
	message = message[:reply_end-1]	

	#find bulletin and reply_thread in database that match email title
	bulletin = Bulletin.objects.get(subject = bulletin_subject)
	reply_thread = Reply_Thread.objects.get(bulletin = bulletin)

	sender = inbound.sender()#need to convert to userdata instance
	
	try:
		#does user exist?
		user = user.objects.get(email = sender)
		userdata = user.userdata

		#create new reply object
		reply = Reply.objects.create(thread = reply_thread, sender = userdata, public = True, 
								     timestamp = timestamp, message = message)
		reply.save()

	except:
		#user does not exist - generate basic info for reply
		name = generate_name(sender)
		
		reply = Reply.objects.create(thread = reply_thread, name = name, email = sender, public = True, 
								     timestamp = timestamp, message = message)

		reply.save()


	
				
			


