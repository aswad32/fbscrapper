from pymongo import MongoClient
from bson.objectid import ObjectId

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup

import time
import sys
sys.path.insert(0, 'functions')
import database
import framework
from config import init_config

dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 "
    "(KHTML, like Gecko) Chrome/15.0.87"
)

driver = webdriver.PhantomJS(r'phantomjs/phantomjs.exe')
driver.maximize_window()

driver.get('http://www.facebook.com')
elem = driver.find_element_by_id('email')
elem.send_keys(init_config['username'])
elem = driver.find_element_by_id('pass')
elem.send_keys(init_config['pwd'])
elem.send_keys(Keys.RETURN)


query_collection = init_config['query']

for qs in query_collection:
	print "Executing query string -> " + qs
	time.sleep(10)
	try:
		driver.get("https://www.facebook.com/search/latest/?q=" + qs)
	except Exception, e:
		driver.close()
		driver.quit()
		sys.exit()


	driver.implicitly_wait(10)

	range_max = 1; #change this variable if you want to scroll more feed from the search query
	for a in range(1, range_max):
		driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
		time.sleep(10)

	html = driver.find_element_by_id('pagelet_loader_initial_browse_result').get_attribute('innerHTML')
	data = html.encode('ascii', 'ignore').strip()

	post = []

	soup = BeautifulSoup(data, 'html.parser')

	for content in soup.find_all('div', { 'class': ['_5bl2 ', '_3u1', '_41je']}):
		userPost = framework.loadPost('',content, True, 1, qs)

		if not userPost is None:

			resp = database.insertPost(userPost)
			if not resp is None:
				print "Data has been saved \n"
			else:
				print "Failed to saved data \n"
		else:
			print "Data already been saved on previous query"

	html = ""
	data =  ""
	soup = None

driver.close()
driver.quit()
sys.exit()

