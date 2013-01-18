from inbound import PostmarkInbound
import json as simplejson
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import re
from models import Filter

def match_filter(subject, helpfilter):
	for word in subject.split():
		try:
			tag = Filter.objects.get(name = word.title(), helpfilter=helpfilter)
			return tag.name
		except:
			pass
	return 'None'

@csrf_exempt
def incoming(request):
	if request.method == 'POST':
		json_data = PostmarkInbound(json = request.raw_post_data)
		try:
			tag, subject = re.split(r':', json_data.subject(), 1)
			print tag, subject
		except:
			#No tag
			helpfilter = False
			result = match_filter(json_data.subject(), helpfilter)
			print result, json_data.subject()
			
		return HttpResponse('POST Request')
	return HttpResponse('GET Request')


