from inbound import PostmarkInbound
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from models import Filter, Bulletin, Missive, Reply, Reply_Thread, UserData
import datetime
import re

@csrf_exempt
def standard_handler(request):
	if request.method == 'POST':
		inbound = PostmarkInbound(json = request.raw_post_data)
		if mailinglist(inbound):
			return mailinglist_process(inbound)
		else:
			return reply(inbound)

def mailinglist(inbound):
	'''Check to see if email originated in carpe or helpme'''
	return "[Carpediem]" in inbound.subject() or "[Helpme]" in inbound.subject()

def mailinglist_process(inbound):
	'''Process helpme's and carpe's'''
	if "[Carpediem]" in inbound.subject():
		return handle_mailing_list(False, inbound)					
	else:
		return handle_mailing_list(True, inbound)

def resolved(subject, message):
	regex = r'(?<!un)resolve'
	subject_match = re.search(regex, subject, flags=re.IGNORECASE)
	message_match = re.search(regex, message, flags=re.IGNORECASE)
	if message_match:
		return subject
	if subject_match:
		subject = re.sub(r'\[?resolved\]?[\:|\-]?[ ]?', '',  subject, flags=re.IGNORECASE)
		return subject
	return False

def basic_info(inbound):
	subject = inbound.subject()	
	sender = inbound.sender()
	timestamp = datetime.datetime.now()
	message = inbound.text_body()
	return subject, sender, timestamp, message

def latest_response(message):
	reply_end = message.find('From:')	
	if reply_end != -1:
		message = message[:reply_end]	
	return message

def generate_name(sender):
	name = sender['Name']
	email = sender['Email']
	return name, email

def trim_message(message):
	regex = r'On [A-Z][a-z]{2,3}\,'
	message = re.split(regex, message, 1)[0]
	return message


def reformat(message):
	message_parts = re.split(r'[\_]{20,60}', message, 1)
	message = message_parts[0]
	return message

def match_filter(subject, message, helpfilter):
	#search subject for a matching filter if filter does not exist
	for word in subject.split():
		try:
			#return tag
			tag = Filter.objects.get(name = word.title(), helpfilter=helpfilter)
			return tag
		except:
			pass
	
	#search body of email if no tag found in subject
	message = message.lower()
	for filterObject in Filter.objects.filter(helpfilter=helpfilter):
		if filterObject.name.lower() in message:
			return filterObject
		
	#Nothing is found, return mailing_list name as placeholder
	if helpfilter: mailing_list = "Helpme"
	else: mailing_list = "Carpediem"

	tag = Filter.objects.get(name = mailing_list, helpfilter=helpfilter)
	return tag

def get_user(sender):
	try:
		user = User.objects.get(email = sender['Email'])
	except: 
		user = User.objects.get(username = '.'.join(sender['Name'].lower().split()))
	return user

def handle_mailing_list(helpfilter, inbound):
	#Assign to mailing list
	if helpfilter: mailing_list = 'Helpme'
	else: mailing_list = 'Carpediem'
	subject = inbound.subject()
	
	if "Re: " in subject:
		return mailinglist_reply(inbound, mailing_list, helpfilter)
	else:
		return send_bulletin(inbound, mailing_list, helpfilter)

def reply(inbound):

	subject, sender, timestamp, message = basic_info(inbound)

	#remove "Re:" from subject line
	bulletin_subject = re.sub(r'Re\: ', '', subject)	

	#remove everything but latest response
	message = latest_response(message)

	#remove replies
	message = trim_message(message) 
	
	#find bulletin and reply_thread in database that match email title
	bulletin = Bulletin.objects.get(subject__iexact = bulletin_subject)
	
	#check if reply_thread already exists, create one if not	

	sender = inbound.sender()#need to convert to userdata instance
		
	if resolved(bulletin_subject, message):
		bulletin.resolved = True
		bulletin.save()
		return HttpResponse('Success!')
	
	try:
		#does user exist?
		user = get_user(sender)
		userdata = user.userdata

		print ("Bulletin creator: %s\nUser.userdata: %s" %(str(bulletin.creator), str(user.userdata)))
		if bulletin.creator == user.userdata:
			#create missive
			missive = Missive.objects.create(timestamp = timestamp, message = message, bulletin = bulletin)
			missive.save()
			return HttpResponse('Success!')
		
		try: 
			reply_thread = Reply_Thread.objects.get(bulletin = bulletin)
		except: 
			reply_thread = Reply_Thread.objects.create(bulletin = bulletin)
	
		#create new reply object
		reply = Reply.objects.create(thread = reply_thread, sender = userdata, public = False, 
								     timestamp = timestamp, message = message)
		reply.save()
		reply_thread.save()
		return HttpResponse('Success!')

	except:
		#user does not exist - generate basic info for reply
		name, email = generate_name(sender)

		if bulletin.anon_name == name:
			#create missive
			missive = Missive.objects.create(timestamp = timestamp, message = message, bulletin = bulletin)
			missive.save()
			return HttpResponse('Success!')
		
		#another candidate for **kwargs
		try: 
			reply_thread = Reply_Thread.objects.get(bulletin = bulletin, anon_email = email, anon_name = name, anon = True)
		except: 
			reply_thread = Reply_Thread.objects.create(bulletin = bulletin, anon_email = email, anon_name = name, anon = True)

		reply = Reply.objects.create(thread = reply_thread, anon=True, public = False, 
								     timestamp = timestamp, message = message)

		reply.save()
		reply_thread.save()
		return HttpResponse('Success!')

def mailinglist_reply(inbound, mailing_list, helpfilter):
	#send reply
	subject, sender, timestamp, message = basic_info(inbound)

	#remove tag from subject line
	regex = r'\[' + mailing_list + '\] '
	subject = re.sub(regex, '', subject)

	#remove "Re:" from subject line
	bulletin_subject = re.sub(r'Re\: ', '', subject)

	#remove everything but latest response
	message = latest_response(message)
	message = trim_message(message) 

	if resolved(bulletin_subject, message):
		bulletin_subject = resolved(bulletin_subject, message)
		bulletin = Bulletin.objects.get(subject__iexact = bulletin_subject, helpbulletin=helpfilter)
		bulletin.resolved = True
		bulletin.save()
		return HttpResponse('Success!')
	
	#find bulletin and reply_thread in database that match email title
	bulletin = Bulletin.objects.get(subject__iexact = bulletin_subject, helpbulletin=helpfilter)

	try:
		#does user exist?
		user = get_user(sender)

		if bulletin.creator == user.userdata:
			#create missive
			missive = Missive.objects.create(timestamp = timestamp, message = message, bulletin = bulletin)
			missive.save()
			return HttpResponse('Success!')

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
		reply_thread.save()
		return HttpResponse('Success!')

	except:
		#user does not exist - generate basic info for reply
		name, email = generate_name(sender)

		if bulletin.anon_name == name:
			#create missive
			missive = Missive.objects.create(timestamp = timestamp, message = message, bulletin = bulletin)
			missive.save()
			return HttpResponse('Success!')
		
		try: 
			reply_thread = Reply_Thread.objects.get(bulletin = bulletin, anon_email = email, anon_name = name, anon=True)
		except: 
			reply_thread = Reply_Thread.objects.create(bulletin = bulletin, anon_email = email, anon_name = name, anon=True)

		reply = Reply.objects.create(thread = reply_thread, public = True,
									 timestamp = timestamp, message = message, anon = True)

		reply.save()
		reply_thread.save()
		return HttpResponse('Success!')

def send_bulletin(inbound, mailing_list, helpfilter):
	subject, sender, timestamp, message = basic_info(inbound)

	#remove mailing_list from subject line
	regex = r'\[' + mailing_list + '\] '
	subject = re.sub(regex, '', subject)

	#remove replies from message
	message = trim_message(message) 

	#send bulletin
	tag = match_filter(subject, message, helpfilter)
	relevance = datetime.datetime.now() + datetime.timedelta(1)

	data = {'subject': subject, 'sender': sender, 'timestamp': timestamp, 'message': message, 
			'tag':tag, 'relevance':relevance, 'helpfilter':helpfilter}
	
	#resolve bulletin if needed
	if resolved(subject, message):
		try:
			subject = resolved(subject, message)
			bulletin = Bulletin.objects.get(subject__iexact = subject, helpbulletin=helpfilter)
			bulletin.resolved = True
			bulletin.save()
			return HttpResponse('Success!')
		except:
			#bulletin DNE
			pass

	#generate new bulletin
	if helpfilter:
		return send_help_bulletin(data)
	else:
		return send_want_bulletin(data)

def send_help_bulletin(data): #should use **kwargs here
	subject, sender, timestamp, message = data['subject'], data['sender'], data['timestamp'], data['message']
	tag, relevance, helpfilter = data['tag'], data['relevance'], data['helpfilter']
	
	message = reformat(message)

	try:
		#does user exist?
		user = get_user(sender)
		userdata = user.userdata

		
		if bulletin.creator == user.userdata:
			#create missive
			missive = Missive.objects.create(timestamp = timestamp, message = message, bulletin = bulletin)
			missive.save()
			return HttpResponse('Success!')

		#create bulletin
		bulletin = Bulletin.objects.create(subject = subject, creation = timestamp, relevance = relevance,
										   location = 'NA', tag = tag, creator = userdata, helpbulletin = helpfilter)

		#create missive
		missive = Missive.objects.create(timestamp = timestamp, message = message, bulletin = bulletin)
		
		missive.save()
		bulletin.save()
		return HttpResponse('Success!')
	
	except:
		#user does not exist
		name, email = generate_name(sender)

		#create bulletin
		bulletin = Bulletin.objects.create(subject = subject, creation = timestamp, relevance = relevance, helpbulletin = helpfilter,
											location = 'NA', tag = tag, anon_name=name, anon_email = email, anon = True)

		#create missive
		missive = Missive.objects.create(timestamp = timestamp, message = message, bulletin = bulletin)
		
		missive.save()
		bulletin.save()
		return HttpResponse('Success!')


def send_want_bulletin(data): #should use **kwargs here
		subject, sender, timestamp, message = data['subject'], data['sender'], data['timestamp'], data['message']
		tag, relevance, helpfilter = data['tag'], data['relevance'], data['helpfilter']

		message = reformat(message)
		
		try:
			#does user exist?
			user = get_user(sender)
			userdata = user.userdata

			if bulletin.creator == user.userdata:
				#create missive
				missive = Missive.objects.create(timestamp = timestamp, message = message, bulletin = bulletin)
				missive.save()
				return HttpResponse('Success!')

			#create bulletin
			bulletin = Bulletin.objects.create(subject = subject, creation = timestamp, relevance = relevance,
											   location = 'NA', tag = tag, creator = userdata, free=False, helpbulletin = helpfilter)

			#create missive
			missive = Missive.objects.create(timestamp = timestamp, message = message, bulletin = bulletin)
			
			missive.save()
			bulletin.save()
			return HttpResponse('Success!')
		
		except:
			#user does not exist
			name, email = generate_name(sender)

			#create bulletin
			bulletin = Bulletin.objects.create(subject = subject, creation = timestamp, relevance = relevance, helpbulletin = helpfilter,
												location = 'NA', tag = tag, anon_name = name, anon_email = email, anon = True, free = False)

			#create missive
			missive = Missive.objects.create(timestamp = timestamp, message = message, bulletin = bulletin)
			
			missive.save()
			bulletin.save()
			return HttpResponse('Success!')
