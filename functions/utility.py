
from urlparse import parse_qs, urlparse
import urllib
import json

'''
Access user fbid from post being scrapped, 
example : /ajax/hovercard/user.php?id=684848775&extragetparams=%7B%22hc_ref%22%3A%22NEWSFEED%22%2C%22fref%22%3A%22nf%22%7D
'''
def getFbId(hovercard_url):
	url = hovercard_url.split('?')[1]
	return parse_qs(url)['id'][0].replace("\r\n", "")

'''
Facebook have wide variety of URL formatting but each URL contains postid for the particular post that we scrapping,
below are most use URL for post.
- https://www.facebook.com/photo.php?fbid=336576623397916&set=a.152082791847301.1073741828.100011367422621&type=3
- /permalink.php?story_fbid=336990686689843&id=100011367422621
- https://www.facebook.com/media/set/?set=a.381794285338690.1073741947.100005243644525&type=3
- /bazooka.penaka.3720/posts/161654117597544
- /shekhanuar.alkhattab/videos/172420779845422/
- /groups/643968408983786/permalink/1069548199759136/
'''
def getPostId(url):
	proc_url = urlparse(url)
	proc_query = parse_qs(proc_url.query)
	if 'fbid' in proc_query:
		post_id = proc_query['fbid'][0]
	elif 'story_fbid' in proc_query:
		post_id = proc_query['story_fbid'][0]
	elif 'set' in proc_query:
		pre_post_id = proc_query['set'][0].split('.')
		post_id = pre_post_id[1]
	else:
		proc_path = proc_url.path
		pre_post_id = proc_path.split('/')
		if len(pre_post_id) <= 5:
			post_id = pre_post_id[3]
		else:
			post_id = pre_post_id[4]
	return post_id

'''
Sample facebook video url, it is important to note the video post id must be correct in order to get the real url
Embed video url
- https://www.facebook.com/video/embed?video_id=1051396234975127
Direct link to video (the request will return json data with HD source and SD source of the video)
- https://www.facebook.com/video/video_data/?video_id=668662573312263
!important:
Issues with direct link url, it has expiry based to the timestamp the url has been generated on request,
if the url expired, the video wont show anymore.
'''
def buildEmbedVideoUrl(postId):
	json_data = urllib.urlopen('https://www.facebook.com/video/video_data/?video_id=' + postId).read()
	try:
		parse_json = json.loads(json_data)

		video_direct_url = ""
		video_embed_url = "https://www.facebook.com/video/embed?video_id=" + postId
		if 'hd_src_no_ratelimit' in parse_json:
			video_direct_url = parse_json['hd_src_no_ratelimit']
		else:
			video_direct_url = parse_json['sd_src_no_ratelimit']
	except Exception, e:
		video_direct_url = ""
		video_embed_url = "https://www.facebook.com/video/embed?video_id=" + postId

	return video_direct_url, video_embed_url

'''
Building hashtag from message / shared message / attachment description
'''
def buildHashtag(textContent):
	hashtag = {tag.strip("#").replace('.', '').replace(',', '').lower() for tag in textContent.split() if tag.startswith("#")}
	return list(hashtag)