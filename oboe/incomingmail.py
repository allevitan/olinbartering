from inbound import PostmarkInbound
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from models import Filter, Bulletin, Missive, Reply, Reply_Thread, UserData
import datetime
import re

@csrf_exempt
def standard_reply(request):
	print "Email incoming..."
	if request.method == 'POST':
		inbound = PostmarkInbound(json = request.raw_post_data)
		if mailinglist(inbound):
			return mailinglist_process(inbound)
		else:
			return process(inbound)

def mailinglist(inbound):
	'''Check to see if email originated in carpe or helpme'''
	return "[Carpediem]" in inbound.subject() or "[Helpme]" in inbound.subject()

def mailinglist_process(inbound):
	'''Process helpme's and carpe's'''
	if "[Carpediem]" in inbound.subject():
		return handle_mailing_list(False, inbound)					
	else:
		return handle_mailing_list(True, inbound)

def basic_info(inbound):
	subject = inbound.subject()	
	sender = inbound.sender()#need to convert to userdata instance
	timestamp = datetime.datetime.now()
	message = inbound.text_body()
	return subject, sender, timestamp, message

'''
Currently not functional
def basic_info_fwd(inbound):
	subject = inbound.subject()
	sender = {'Email': inbound.sender_email(), 'Name': inbound.sender_name()}
	timestamp = datetime.datetime.now()
	message = inbound.text_body_fwd()
	return subject, sender, timestamp, message
'''

'''def generate_name_old(sender):
	email_halves = re.split(r'\@', sender)
	name = email_halves[0]
	names = re.split(r'\.', name)
	name = ' '.join([name.title() for name in names])
	return name'''

def generate_name(sender):
	name = sender['Name']
	email = sender['Email']
	return name, email

def handle_mailing_list(helpfilter, inbound):
	#Assign to mailing list
	if helpfilter: mailing_list = 'Helpme'
	else: mailing_list = 'Carpe'
	subject = inbound.subject()
	
	if "Re: " in subject:
		return send_reply(inbound, mailing_list, helpfilter)
	else:
		return send_bulletin(inbound, mailing_list, helpfilter)

def send_reply(inbound, mailing_list, helpfilter):
	#send reply
	subject, sender, timestamp, message = basic_info(inbound)

	#remove tag from subject line
	regex = r'\[' + mailing_list + '\] '
	subject = re.sub(regex, '', subject)

	#remove "Re:" from subject line
	bulletin_subject = re.sub(r'Re\: ', '', subject)	

	#remove everything but latest response
	reply_end = message.find('From:')
	if reply_end != -1:
		message = message[:reply_end-1]	
	
	#find bulletin and reply_thread in database that match email title
	bulletin = Bulletin.objects.get(subject__iexact = bulletin_subject, helpbulletin=helpfilter)

	try:
		#does user exist?
		try:
			user = User.objects.get(email = sender['Email'])

		except: 
			user = User.objects.get(username = '.'.join(sender['Name'].lower().split()))

		userdata = user.userdata

		#check if reply thread already exists, create one if not
		try: 
			reply_thread = Reply_Thread.objects.get(bulletin = bulletin)
		except: 
			reply_thread = Reply_Thread.objects.create(bulletin = bulletin)

		#create new reply object
		reply = Reply.objects.create(thread = reply_thread, sender = userdata, public = True, 
									 timestamp = timestamp, message = message)
		reply.save()
		return HttpResponse('Success!')

	except:
		#user does not exist - generate basic info for reply
		name, email = generate_name(sender)
		
		try: 
			reply_thread = Reply_Thread.objects.get(bulletin = bulletin, anon_email = email, anon_name = name)
		except: 
			reply_thread = Reply_Thread.objects.create(bulletin = bulletin, anon_email = email, anon_name = name)

		reply = Reply.objects.create(thread = reply_thread, name = name, email = email, public = True, 
									 timestamp = timestamp, message = message, anon = True)

		reply.save()
		return HttpResponse('Success!')

def send_bulletin(inbound, mailing_list, helpfilter):
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
			try:
				user = User.objects.get(email = sender['Email'])
			except: 
				user = User.objects.get(username = '.'.join(sender['Name'].lower().split()))
			userdata = user.userdata

			#create bulletin
			bulletin = Bulletin.objects.create(subject = subject, creation = timestamp, relevance = relevance,
											   location = 'NA', tag = tag, creator = userdata)

			#create missive
			missive = Missive.objects.create(timestamp = timestamp, message = message, bulletin = bulletin)
			
			missive.save()
			bulletin.save()
			return HttpResponse('Success!')
		
		except:
			#user does not exist
			name, email = generate_name(sender)

			#create bulletin
			bulletin = Bulletin.objects.create(subject = subject, creation = timestamp, relevance = relevance,
												location = 'NA', tag = tag, name=name, email=email)

			#create missive
			missive = Missive.objects.create(timestamp = timestamp, message = message, bulletin = bulletin)
			
			missive.save()
			bulletin.save()
			return HttpResponse('Success!')

	else:
		
		try:
			#does user exist?
			try:
				user = User.objects.get(email = sender['Email'])
			except: 
				user = User.objects.get(username = '.'.join(sender['Name'].lower().split()))
			userdata = user.userdata

			#create bulletin
			bulletin = Bulletin.objects.create(subject = subject, creation = timestamp, relevance = relevance,
											   location = 'NA', tag = tag, creator = userdata, free=False)

			#create missive
			missive = Missive.objects.create(timestamp = timestamp, message = message, bulletin = bulletin)
			
			missive.save()
			bulletin.save()
			return HttpResponse('Success!')
		
		except:
			#user does not exist
			name, email = generate_name(sender)

			#create bulletin
			bulletin = Bulletin.objects.create(subject = subject, creation = timestamp, relevance = relevance,
												location = 'NA', tag = tag, name=name, email=email, free=False)

			#create missive
			missive = Missive.objects.create(timestamp = timestamp, message = message, bulletin = bulletin)
			
			missive.save()
			bulletin.save()
			return HttpResponse('Success!')
	

def match_filter(subject, helpfilter):
	#search for a matching filter if filter does not exist
	for word in subject.split():
		try:
			#return tag
			tag = Filter.objects.get(name = word.title(), helpfilter=helpfilter)
			return tag
		except:
			pass
	#Nothing is found, return mailing_list name as placeholder
	if helpfilter: mailing_list = "Helpme"
	else: mailing_list = "Carpe"

	tag = Filter.objects.get(name = mailing_list, helpfilter=helpfilter)
	return tag

def process(inbound):

	timestamp = datetime.datetime.now()
	message = inbound.text_body()
	subject = inbound.subject()

	#remove "Re:" from subject line
	bulletin_subject = re.sub(r'Re\: ', '', subject)	

	#remove everything but latest response
	reply_end = message.find('From:')
	message = message[:reply_end]	

	print bulletin_subject
	#find bulletin and reply_thread in database that match email title
	bulletin = Bulletin.objects.get(subject__iexact = bulletin_subject)
	
	#check if reply_thread already exists, create one if not	

	sender = inbound.sender()#need to convert to userdata instance
	
	try:
		#does user exist?
		try:
			user = User.objects.get(email = sender['Email'])
		except: 
			user = User.objects.get(username = '.'.join(sender['Name'].lower().split()))
		userdata = user.userdata
		
		try: 
			reply_thread = Reply_Thread.objects.get(bulletin = bulletin)
		except: 
			reply_thread = Reply_Thread.objects.create(bulletin = bulletin)
	
		#create new reply object
		reply = Reply.objects.create(thread = reply_thread, sender = userdata, public = True, 
								     timestamp = timestamp, message = message)
		reply.save()
		return HttpResponse('Success!')

	except:
		#user does not exist - generate basic info for reply
		name, email = generate_name(sender)
		
		try: 
			reply_thread = Reply_Thread.objects.get(bulletin = bulletin, anon_email = email, anon_name = name)
		except: 
			reply_thread = Reply_Thread.objects.create(bulletin = bulletin, anon_email = email, anon_name = name)

		reply = Reply.objects.create(thread = reply_thread, name = name, email = email, public = True, 
								     timestamp = timestamp, message = message)

		reply.save()
		return HttpResponse('Success!')


	
				
			


