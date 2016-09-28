from urlparse import parse_qs, urlparse
from pymongo import MongoClient
from bson.objectid import ObjectId
import moment

import sys
sys.path.insert(0, './config')
from config import init_config

def connect():
	client = MongoClient(init_config['mongodb']['host'])
	db = client.keepit # you can change the dbname as per you like in my case keepit
	return db

'''
Make sure the post does not exists before inserting new data
'''
def postExists(postid):
	resp = connect().fbpostqueries.count({ 'postid': str(postid) })
	if resp > 0:
		return True
	else:
		return False

'''
Insert the post
'''
def insertPost(obj):
	resp = connect().fbpostqueries.insert_one(obj)
	return resp


