from inbound import PostmarkInbound
import simplejson


def incoming(request):
	json_data = simplejson.loads(request.raw_post_data)
	print json_data
	inbound = PostmarkInbound(json=json_data)
