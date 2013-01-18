from inbound import PostmarkInbound
import json as simplejson
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from models import Filter, Bulletin, Missive, Reply, Reply_Thread, UserData
import datetime
import re


def match_filter(subject, helpfilter):
	#search for a matching filter if filter does not exist
	for word in subject.split():
		try:
			tag = Filter.objects.get(name = word.title(), helpfilter=helpfilter)
			return tag.name
		except:
			pass
	return ''

@csrf_exempt
def incoming(request):
	if request.method == 'POST':
		inbound = PostmarkInbound(json = request.raw_post_data)
		sender = inbound.sender()
		message = inbound.text_body()
		try:
			tag, subject = re.split(r':', inbound.subject(), 1)
			print tag, subject
		except:
			#No tag
			helpfilter = False
			result = match_filter(inbound.subject(), helpfilter)
			print result, inbound.subject()
			
		return HttpResponse('POST Request')
	return HttpResponse('GET Request')

def reply(request):
	if request.method == 'POST':
		inbound = PostmarkInbound(json = request.raw_past_data)
		sender = inbound.sender()
		try:
			bulletinID = re.search(r'ID\:\d+')
		except: 
			pass


def mailinglist(inbound):
	'''Check to see if email originated in carpe or helpme'''
	return "[Carpe]" in inbound.subject() or "[Helpme]" in inbound.subject():

def mailinglist_process(inbound):
	'''Process helpme's and carpe's'''
	if "[Carpe]" in subject:
		handle_mailing_list(False, inbound)					
	else:
		handle_mailing_list(True, inbound)

def handle_mailing_list(helpfilter, inbound):
	
	subject = inbound.subject()	
	sender = inbound.sender()#need to convert to userdata instance
	timestamp = datetime.datetime.now()
	message = inbound.text_body()

	#Assign to mailing list
	if helpfilter: mailing_list = 'Helpme'
	else: mailing_list = 'Carpe'

	#remove tag from subject line
	regex = r'\[' + mailing_list + '\] '
	subject = re.sub(regex, '', subject)
	if "Re: " in subject:
		#send reply

		#remove "Re:" from subject line
		bulletin_subject = re.sub(r'Re\:', '', subject)	

		#remove everything but latest response
		reply_end = message.find('From:')
		message = message[:reply_end-1]	
		
		#find bulletin and reply_thread in database that match email title
		bulletin = Bulletin.objects.get(subject = bulletin_subject, helpbulletin = helpfilter)
		reply_thread = Reply_Thread.objects.get(bulletin = bulletin)

		#create new reply object
		#reply = Reply.objects.create(thread = reply_thread, sender = sender, public = True, 
									  #timestamp = timestamp, message = message)
		#send_reply(missive)
	else:
		#send bulletin
		tag = Filter.objects.get(name = mailing_list, helpfilter = helpfilter)
		relevance = datetime.datetime.now() + datetime.timedelta(7)

		#generate new bulletin
		if helpfilter:
			#bulletin = Bulletin.objects.create(subject = subject, creation = timestamp, relevance = relevance,
											   #location = 'NA', tag = tag, creator = sender)
		else:
			#bulletin = Bulletin.objects.create(subject = subject, creation = timestamp, relevance = relevance,
											   #location = 'NA', tag = tag, creator = sender, free=False)

		#send_bulletin(bulletin)
		

	
				
			


