from bs4 import BeautifulSoup
from urlparse import parse_qs, urlparse
import moment

import database
import utility

img_skip_regex = ['-PAXP-deijE.gif', 'p32x32', '-pz5JhcNQ9P.png']

'''
Params:
@based_postid: not applicable for search query result and can be leave as '' string
@content: based content element for each post
@validateExists: in some case you just to ignore validation you can set it to False
@postToGroupMethod: 1
@query_string: Search keyword
'''
def loadPost(based_postid, content, validateExists, postToGroupMethod, query_string):
	profile_element = content.find('a', { 'class': '_5pb8' })

	# in case of scraping personal account feed, profile element are missing on post
	# skip it if occurs
	if profile_element is None:
		return 404

	fbid_url = profile_element['data-hovercard']
	fbid = utility.getFbId(fbid_url)

	profile_link = profile_element['href']
	profile_picture = profile_element.find('img')['src']

	profile_name_element = content.find('span', { 'class': 'fwb'})
	profile_name = profile_name_element.find('a').getText().encode('utf-8')

	link_date_post_element = content.find('span', { 'class': 'fsm' })
	post_link = link_date_post_element.find('a')['href']

	#in case of user sharing image or videos, usually there are two postid,
	#we need to use the postid being capture originally by the system rather than the postid for image / video
	#to get the number of shares and likes
	if not based_postid == '':
		post_id = based_postid
	else:
		post_id = utility.getPostId(post_link)
		print post_id

	if validateExists:
		# make sure skip the rest of the process if the data already existed
		# if more than 10 data existed on straight loop break the loop end the process
		if database.postExists(post_id):
			return None

	date_post = link_date_post_element.find('abbr')['data-utime']
	if not date_post == "":
		post_created_time = moment.unix(float(date_post), utc=True).date
	else:
		post_created_time = ""

	posted_to_name = ""
	posted_to_link = ""

	if postToGroupMethod == 1:
		posted_to_element = profile_name_element.find('a', { 'class': '_wpv'})
		posted_to_name, posted_to_link = loadPostToGroupLayoutNormal(posted_to_element)
	elif postToGroupMethod == 2:
		posted_to_main_element = content.find('span', { 'class': 'fcg'})

		posted_to_name, posted_to_link = loadPostToGroupLayoutShared(posted_to_main_element)

	user_content = content.find('div', { 'class': 'userContent' })

	if user_content is None:
		return 404

	status_message = user_content.find_all('p')
	post_message = ""
	if not status_message is None:
		for msg in status_message:
			post_message += msg.getText().encode('ascii', 'ignore')

	# facebook will hide extra message and it's located inside div(class='text_exposed_show')
	text_exposed = user_content.find('div', { 'class': 'text_exposed_show'})
	if not text_exposed is None:
		status_message_extra = text_exposed.find_all('p')
		if not status_message_extra is None:
			for msg in status_message_extra:
				post_message += msg.getText().encode('ascii', 'ignore')
	post_message = post_message.replace('...', '')


	# retrieve facebook video post
	video = {
		"direct_url": "",
		"embed_url": ""
	}
	if 'videos' in post_link:
		post_video_direct_url, post_video_embed_url = utility.buildEmbedVideoUrl(post_id)
		video = {
			"direct_url": post_video_direct_url,
			"embed_url": post_video_embed_url
		}


	# Start loading attachment,
	# Here we scrap information about:
	# 1. A post that sharing another profile post message
	# 2. A post that sharing another profile post message with external link
	# 3. A post that sharing external link
	based_attachment_element = content.find('div', { 'class': '_3x-2'})
	post_personal_attach, post_img_attachment = loadAttachment(based_attachment_element)

	textContent = post_message + ' ' + post_personal_attach['message'] + ' ' + post_personal_attach['attachment']['description']
	hashtag = utility.buildHashtag(textContent)

	user_post = {
		"fbid": str(fbid),
		"profile_name": str(profile_name),
		"profile_link": str(profile_link),
		"profile_picture": str(profile_picture),
		"postid": str(post_id),
		"link": str(post_link),
		"posted_to": {
			"name": str(posted_to_name),
			"link": str(posted_to_link)
		},
		"created_time": post_created_time,
		"message": post_message,
		"attachment_shared": post_personal_attach,
		"attachment_img": post_img_attachment,
		"attachment_video": video,
		"connections": {
			"likes": {
				"count": 0,
				"profiles": []
			},
			"shares": {
				"count": 0,
				"profiles": []
			},
			"comments": {
				"count": 0,
				"story": []
			}
		},
		"query_string": query_string,
		"hashtag": hashtag
	}

	return user_post


def loadPostToGroupLayoutShared(element):
	posted_to_name = ""
	posted_to_link = ""
	if not element is None:
		posted_to_element = element.find_all('a', { 'class': 'profileLink'})
		posted_to_element_text = element.getText().encode('ascii', 'ignore')

		# this is hackaround to find out either this is
		# a facebook post to a group or not
		if 'group' in posted_to_element_text:
			if len(posted_to_element) == 2:
				posted_to_name = posted_to_element[1].getText().encode('ascii', 'ignore')
				posted_to_link = posted_to_element[1]['href']

	return posted_to_name, posted_to_link

def loadPostToGroupLayoutNormal(element):
	posted_to_name = ""
	posted_to_link = ""
	if not element is None:
		posted_to_name = element.getText().encode('utf-8')
		posted_to_link = element['href']

	return posted_to_name, posted_to_link

def loadAttachment(based_attachment_element):
	if not based_attachment_element is None:
		based_element = based_attachment_element.find('div', {'class': '_5r69'})
		if not based_element is None:
			owner_element = based_element.find('span', { 'class': 'fwb'})

			if not owner_element is None:
				owner_name = owner_element.getText().encode('ascii', 'ignore').strip()
				owner_account = (owner_element.find('a')['href']).encode('ascii', 'ignore').strip()
				owner_fbid_url = owner_element.find('a')['data-hovercard']
				owner_fbid = utility.getFbId(owner_fbid_url)
			else:
				owner_name = ""
				owner_account = ""
				owner_fbid = ""

			time_element = based_element.find('div', {'class': '_5pcp'})
			if not time_element is None:
				time_post = str(time_element.find('abbr')['data-utime'])
				#update time epoch to utc datetime
				created_time = moment.unix(float(time_post), utc=True).date
			else:
				created_time = ""

			#post_link_element
			post_link_element = based_element.find('a', {'class': '_5pcq'})
			if not post_link_element is None:
				share_post_link = post_link_element['href'].encode('ascii', 'ignore').strip()
				share_post_id = utility.getPostId(share_post_link)
			else:
				share_post_link = ""
				share_post_id = ""

			post_element = based_element.find('div', { 'class': '_5pco' })

			if not post_element is None:
				post_element_paragraph = post_element.find_all('p')
				posts = ""
				for msg in post_element_paragraph:
					posts += msg.getText().encode('ascii', 'ignore').strip()

				# facebook will hide extra message and it's located inside div(class='text_exposed_show')
				text_exposed = based_element.find('div', { 'class': 'text_exposed_show'})
				if not text_exposed is None:
					posts_extra = text_exposed.find_all('p')
					for msg in posts_extra:
						posts += msg.getText().encode('ascii', 'ignore').strip()

				posts = posts.replace('...', '')
			else:
				posts = ""

			# retrieve facebook video post
			video = {
				"direct_url": "",
				"embed_url": ""
			}

			if 'videos' in share_post_link:
				print "share post id", share_post_id
				post_video_direct_url, post_video_embed_url = utility.buildEmbedVideoUrl(share_post_id)
				video = {
					"direct_url": post_video_direct_url,
					"embed_url": post_video_embed_url
				}

			# retrieve attachment link
			external_attachment = externalAttachment(based_element)

			post_personal_attach = {
				"owner" : {
					"fbid": str(owner_fbid),
					"name": str(owner_name),
					"account": str(owner_account)
				},
				"postid": str(share_post_id),
				"created_time": created_time,
				"message": str(posts),
				"link": str(share_post_link),
				"attachment_video": video,
				"attachment": external_attachment
			}
		else:
			#in case the post only contains external web link attachment
			external_attachment = externalAttachment(based_attachment_element)

			post_personal_attach = {
				"owner" : {
					"fbid": "",
					"name": "",
					"account": ""
				},
				"created_time": "",
				"message": "",
				"link": "",
				"postid": "",
				"attachment_video": {
					"direct_url": "",
					"embed_url": ""
				},
				"attachment": external_attachment
			}


		#get the share picture
		post_img_element = based_attachment_element.find_all('img', {'class': 'img'})
		post_img_attachment = imgAttachment(post_img_element)

		return post_personal_attach, post_img_attachment

def externalAttachment(basedElement):
	attachment_title = ""
	attachment_link = ""
	attachment_desc = ""
	attachment_source = ""
	externalElement = basedElement.find('div', { 'class': '_6m3' })
	if not externalElement is None:
		title = externalElement.find('div', { 'class': '_6m6'})
		attachment_title = title.getText().encode('ascii', 'ignore').strip()

		attachment_link_element = externalElement.findNext('a', {'class': '_52c6'})
		if not attachment_link_element is None:
			attachment_link = attachment_link_element['href'].encode('ascii', 'ignore').strip()

		attachment_desc_element = externalElement.find('div', {'class': '_6m7'})
		if not attachment_desc_element is None:
			attachment_desc = attachment_desc_element.getText().encode('ascii', 'ignore').strip()

		attachment_source = externalElement.find('div', {'class': '_59tj'}).getText().encode('ascii', 'ignore').strip()

	return {
		"title": str(attachment_title) ,
		"description": str(attachment_desc),
		"link": str(attachment_link) ,
		"source": str(attachment_source)
	}

def imgAttachment(imgElement):
	post_img_attachment = []
	if not imgElement is None:
		for img in imgElement:
			img_src = str(img['src'])
			if not any(x in img_src for x in img_skip_regex):
				post_img_attachment.append(str(img['src']))

	return post_img_attachment


'''
Check the layout for type of account that do the post
permalinkPost = pages
stream_pagelet = personal
pagelet_group_mall = group
'''
def checkLayoutAccount(based):

	postElement = None

	element = [
		{'selector': 'class', 'name': 'permalinkPost'},
		{'selector': 'id', 'name': 'stream_pagelet'},
		{'selector': 'id', 'name':'pagelet_group_mall'}
	]

	for el in element:
		postElement = based.find('div', { el['selector'] : el['name'] })
		if not postElement is None:
			break;

	return postElement
