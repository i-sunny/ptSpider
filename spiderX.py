#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import urllib
import cookielib
from bs4 import BeautifulSoup
import re
import string
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

auth_url = 'https://pt.sjtu.edu.cn/takelogin.php'
home_url = 'https://pt.sjtu.edu.cn/'
users_list_url = 'https://pt.sjtu.edu.cn/users.php'

#登陆认证
def login_auth():
	# username & password
	login_data = {
	    "username": "sunxiaooo",
	    "password": "xxx",
	    "checkcode": "XxXx"
	}
	# urllib encode
	post_data=urllib.urlencode(login_data)

	headers = {
	'Host': 'pt.sjtu.edu.cn',
	'Connection': 'keep-alive',
	'Content-Length': '49',
	'Cache-Control': 'max-age=0',
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
	'Origin': 'https://pt.sjtu.edu.cn',
	'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36',
	'Content-Type': 'application/x-www-form-urlencoded',
	'Referer': 'https://pt.sjtu.edu.cn/login.php',
	'Accept-Encoding': 'gzip, deflate',
	'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
	'Cookie': 'PHPSESSID=vjqhtpunc7aakrvusi3ks3rpt7; __utmt=1; c_expiresintv=0; bgPicName=Default;\
	 __utma=248584774.1990402960.1429710825.1429757282.1429939009.5; __utmb=248584774.16.10.1429939009; __utmc=248584774;\
	  __utmz=248584774.1429710825.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)'
	}

	# init a CookieJar to handle Cookie
	cookieJar = cookielib.CookieJar()
	# 实例化一个opener, 进行登录认证
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar))
	req = urllib2.Request(auth_url, post_data, headers) 
	content = opener.open( req )
	return opener


#访问网页
def visit_url(opener, url):
	# 访问网页 自动带着cookie信息
	try:
		content = opener.open(url)
	except urllib2.HTTPError as e:
		print type(e)
		return 'MyError'
	except httplib.BadStatusLine as e:
		print type(e)
		return 'MyError'

	doc = content.read()
	content.close()
	return  doc


TRIES = 5
def main():
	#登陆认证
	for retry in range(TRIES):
		opener = login_auth()
		if opener != '':
			break
	if opener == '':
		print "Fail to login!"
	else:
		print 'Login succesful!'
	## --------------------会员列表页数据抓取-----------------##
	#访问会员列表首页
	list_head_doc = visit_url(opener, users_list_url)

	soup = BeautifulSoup(list_head_doc)
	page_outer = soup.html.body.findAll(attrs = {"class" : "outer"})
	keyword = re.compile("users\.php.*page=.*")                   # 正则表达式 "users.php**page=**"
	page_nums = soup.findAll(attrs = {"href" : keyword})
	page_nums.pop()
	last_list = (page_nums.pop())['href']                               #获取最后页地址
	           
	lists_nums = int(re.sub(".*=", '', last_list))               #会员列表总页数

	#----------------每页会员列表分析------------------#
	list_url_base = "https://pt.sjtu.edu.cn/users.php?&page="    #会员列表页基地址
	user_file = file('spider.txt', 'w')           # open for 'w'riting

	class Torrent:
		def __init__(self):
			self.title = ''
			self.tid = ''

	class UserID:
		def __init__(self):
			self.title = ''
			self.regtime = ''
			self.sex = ''
			self.level = ''
			self.user_id = ''
			self.tlst = []               #会员种子列表

	user = UserID()
	torrent = Torrent()


	#for i in range(lists_nums+ 1):   #i = 0 to lists_nums
	for i in range(200):
		list_url = list_url_base + str(i)              #每页用户列表完整地址
		for retry in range(TRIES):
			list_doc = visit_url(opener, list_url)
			if list_doc != 'MyError':
				break
		if list_doc == 'MyError':            		#访问超时
			print "##Time Out## User List Page: " + str(i)
			continue
		#抓取每页所有会员信息
		soup = BeautifulSoup(list_doc)
		page_outer = soup.html.body.findAll(attrs = {"class" : "outer"})
		soup = BeautifulSoup(str(page_outer))
		keyword = re.compile("userdetails\.php.*id=")             # "userdetails.php**id="
		user_id = soup.findAll(attrs={"href" : keyword})
		for j in range(len(user_id)):
			user = UserID()
			user_id[j] = user_id[j]['href']                       #获取会员id地址
			user.uid = re.sub(".*=", '', user_id[j])       #'userdetails.php?id=xxxx' --> 'xxxx'

			#打开每一个用户主页
			print 'Capture User Page --> userID: ' + user.uid	
			#userid_url = home_url + 'userdetails.php?id=' + user.uid
			#userid_doc = visit_url(opener, userid_url)
			#分析会员详细信息

			#soup = BeautifulSoup(userid_doc)
			#page_outer = soup.html.body.findAll(attrs = {"class" : "outer"})
			#soup = BeautifulSoup(str(page_outer))
			#userid_profile = soup.findAll(attrs = {"class" : "main"})
			#user.title = userid_profile[0].tr.td.b.text            	 #获取会员名
			#userid_details = userid_profile[1].tr.td.table        	 #会员详细信息
			#if userid_details.find(text = re.compile(ur'对不起')):    #过滤访问被限的账号
			#	continue
			
			#userid_regtime = userid_details.find(text = ur'加入日期').parent.parent.nextSibling.text   #账号注册日期
			#user.regtime = (userid_regtime.split(' '))[0]
			
			#user.sex = userid_details.find(text = ur'性别').parent.parent.nextSibling.img['alt']     #账号性别

			#user.level = userid_details.find(text = ur'等级').parent.parent.nextSibling.img['alt']     #账号性别
			line = "UID: " + user.uid + '\n'
			user_file.write(line)

			#完成的种子
			user_torrents_url = home_url + "viewusertorrents.php?&id=" + user.uid + "&show=completed"   #https://pt.sjtu.edu.cn/viewusertorrents.php?&id=xxxx&show=completed
			for retry in range(TRIES):
				torrents_doc = visit_url(opener, user_torrents_url)
				if torrents_doc != 'MyError':
					break
			if torrents_doc == 'MyError':            		#访问超时
				print "##Time Out## User Torrent List: " + str(i)
				continue
			if torrents_doc == '':
				continue

			soup = BeautifulSoup(torrents_doc)
			keyword  = re.compile("details\.php\?id=.*")                   # "details.php?id=**"
			torrents = soup.table.findAll(attrs = {"href" : keyword})     #该账号所有已经下载的种子信息
			for k in range(len(torrents)):
				url = torrents[k]['href']                                        #该种子相对路径  details.php?id=xxxxx&hit=1
				torrent.tid = url.split('=')[1].split('&')[0]               #种子ID   details.php?id=xxxxx&hit=1 --> xxxxx
				#torrent.title = torrents[k]['title']                           #种子标题
				#user.tlst.append(torrent)                                   #将该种子加入会员种子列表
				user_file.write('TID: ' + torrent.tid  + '\n')

	user_file.close()


if __name__ == '__main__':
	main()
	print "Spider Complete!"
