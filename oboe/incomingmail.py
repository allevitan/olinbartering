from inbound import PostmarkInbound
import json as simplejson
from django.http import HttpResponse


def incoming(request):
	json_data = simplejson.loads(request.raw_post_data)
	return HttpResponse(json_data)
	inbound = PostmarkInbound(json=json_data)
