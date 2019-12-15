import os
import sys
import time
import json
import locale
import datetime
import random
from bs4 import BeautifulSoup
from .selenium import Selenium
from .database import DataBase
from .base import Base

class Instagram(Base):
	"""docstring for ClassName"""
	def __init__(self, config):

		self.loginText = "Log In"
		# self.loginText = "登入"
		self.securityCodeText = "Send Security Code"
		# self.securityCodeText = "傳送安全碼"
		self.followText = "Follow"
		# self.followText = "追蹤"
		self.followingText = "Following"
		# self.followingText = "追蹤中"
		self.cancelFollowText = "Unfollow"
		# self.cancelFollowText = "取消追蹤"
		self.error = "Error"
		# self.error = "錯誤"
		# 資料庫
		self.dataBase = DataBase(config['DB_HOST'], config['DB_PORT'], config['DB_USERNAME'], config['DB_PASSWORD'])
		self.dataBase.use_table(config['DB_DATABASE'])

		self.username = config['USERNAME']
		self.password = config['PASSWORD']
		# 填入瀏覽器驅動
		selenium = Selenium(config['DRIVER_PATH'])
		self.driver = selenium.openrBowser()
		self._login()

		self.basePath = os.path.dirname(os.path.abspath(__file__))
		self.today = datetime.date.today()

	#登入
	def _login(self):
		#登入頁
		self.driver.get('https://www.instagram.com/accounts/login/?next=/explore/')
		#判斷已登入

		if self.driver.current_url == "https://www.instagram.com/explore/":
			print("進入頁面")
		#判斷未登入
		else:
			time.sleep(5)
			# 登入輸入
			inputAccount = self.driver.find_element_by_name("username")
			inputAccount.send_keys(self.username)
			inputPassword = self.driver.find_element_by_name("password")
			inputPassword.send_keys(self.password)
			buttonElement = self.driver.find_elements_by_tag_name("button")
			for button in buttonElement:
				print(button.text)
				#登入
				if button.text == self.loginText:
					button.submit()
					print('登入')
			time.sleep(5)
			if not self.driver.current_url == "https://www.instagram.com/explore/":
				print(self.driver.current_url)
				# 驗證帳號
				elements = self.driver.find_elements_by_tag_name("button")
				for x in elements:
					print(x.text)

				for element in elements:
					#傳送安全碼
					if element.text == self.securityCodeText:
						element.submit()
						print("傳送安全碼")
				print("請輸入安全碼")
				securityCode = input()
				print("安全碼 : " + securityCode)
				inputSecurityCode = self.driver.find_element_by_name("security_code")
				inputSecurityCode.send_keys(securityCode)
				elements = self.driver.find_elements_by_tag_name("button")
				for element in elements:
					if element.text == "提交":
						element.submit()
						time.sleep(1)
						self.driver.get('https://www.instagram.com/explore/')

	#取得tag列表
	def getHashTag(self):
		taglist = []
		for Number in range(10):
			for number in range(10):
				self.driver.get("https://www.instagram.com/directory/hashtags/"+str(Number)+"-"+str(number))
				elements = self.driver.find_element_by_tag_name("main").find_elements_by_tag_name("li")
				for element in elements:
					tag = element.find_element_by_tag_name("a").text
					taglist.append(tag)

		# taglist = ['鑫']
		self._tagListProcess(taglist)

	#處理tag
	def _tagListProcess(self, taglist):

		for tag in taglist:
			count = 0
			notNposts = False
			hashtagTrack = 0
			nposts = 0

			self.driver.get('https://www.instagram.com/explore/tags/'+str(tag))
			time.sleep(5)
			soup = BeautifulSoup(self.driver.page_source,"lxml")

			tagname = tag
			try:
				nposts = self.driver.find_element_by_tag_name("header").find_elements_by_tag_name("span")[1].text
				hashtagTrack = int(nposts.replace(',', ''))
			except:
				notNposts = True

			curTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

			sql = "SELECT * FROM `hashtag` WHERE `hashtagName` = '%s'" % \
				(tagname)
			self.dataBase.execution(sql)
			result = self.dataBase.fetch('one')
			if result == None:
				sql = "insert into `hashtag` (`hashtagName`,`hashtagTrack`, `updatetime`) values ('%s','%d','%s')" % \
					(tagname, hashtagTrack, curTime)
				self.dataBase.execution(sql)
				hashtag_id = self.dataBase.getInsterId()
			else:
				hashtag_id = result[0]
				sql = "UPDATE `hashtag` SET `hashtagTrack` = '%d', `updatetime` = '%s' WHERE `hashtagName` = '%s'" % \
					(hashtagTrack, curTime, tagname)
				self.dataBase.execution(sql)

			sql = "SELECT count(*) FROM `article_tag` WHERE hashtag_id = '%s'" % \
				(hashtag_id)
			self.dataBase.execution(sql)
			count = self.dataBase.fetch('one')

			print('hashtag_id:' + str(hashtag_id) + ' hashtagName:' + tagname)
			if count < 0:

				myli = []
				pictureLength = hashtagTrack * 60
				maxSwipe = int(pictureLength / 2000)

				for x in range(1,maxSwipe+1):
					soup = BeautifulSoup(self.driver.page_source,"lxml")
					for a in soup.find_all('a', href=True):
						myli.append(a['href'])


					newmyli = [y for y in myli if y.startswith('/p/')]

					self.driver.execute_script("window.scrollTo(0, %d);" % (2000*x))
					time.sleep(1)

					newmyli = self.removListDuplicate(newmyli)

					if len(newmyli) > 1000:
						break
				print(newmyli)

				# l2 = ['/p/B5LJ2dygjmh/']
				self._articleProcess(newmyli)

			else:
				print("count > 1000")

	# 文章處理
	def _articleProcess(self, newmyli):

		timediff = []
		for j in range(len(newmyli)):
			viewer = 0
			self.driver.get('https://www.instagram.com'+str(newmyli[j]))
			personalArticle = self.driver.find_elements_by_tag_name("section")
			if personalArticle != []:
				url = str(newmyli[j])
				print(url)

				user = personalArticle[0].find_element_by_tag_name("h2").text
				try:
					like = personalArticle[2].find_element_by_tag_name("span").text
				except:
					like = '0'

				locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' ) 
				try:
					like = locale.atoi(like)
					complex(like)
				except ValueError:
					try:
						viewer = personalArticle[2].find_element_by_tag_name("span").find_element_by_tag_name("span").text
						personalArticle[2].find_element_by_tag_name("span").find_element_by_tag_name("span").click()
						like = personalArticle[2].find_elements_by_tag_name("span")[2].text
					except:
						# 觀看數較少
						viewer = personalArticle[2].find_element_by_tag_name("span").text.split(' ')[0]
						try:
							# 觀看點讚較少
							personalArticle[2].find_element_by_tag_name("span").click()
							like = personalArticle[2].find_elements_by_tag_name("span")[1].text
						except:
							like = '0'

					viewer = locale.atoi(viewer)

					try:
						like = locale.atoi(like)
					except:
						like = '0'

				soup = BeautifulSoup(self.driver.page_source,"lxml")
				time.sleep(1)
				
				taglist = self._filter_tag(soup)

				print(user)
				print(like)
				print(taglist)

				curTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


				sql = "SELECT * FROM `user` WHERE userName = '%s'" % \
					(user)
				self.dataBase.execution(sql)
				result = self.dataBase.fetch('one')
				if result == None:
					sql = "insert into `user` (`userName`,`updatetime`) values ('%s','%s')" % \
						(user, curTime)
					self.dataBase.execution(sql)
					user_id = self.dataBase.getInsterId()
				else:
					user_id = result[0]


				sql = "SELECT * FROM `article` WHERE url = '%s'" % \
					(url)
				self.dataBase.execution(sql)
				if self.dataBase.fetch('one') == None:
					sql = "insert into `article` (`user_id`, `url`,`like`, `viewer`, `updatetime`) values ('%s','%s','%d','%d','%s')" % \
						(user_id, url, like, viewer, curTime)
					self.dataBase.execution(sql)
				else:
					sql = "UPDATE `article` SET `like` = '%d', `viewer` = '%d', `updatetime` = '%s' WHERE `url` = '%s'" % \
						(like, viewer, curTime, url)
					self.dataBase.execution(sql)

				sql = "SELECT article_id FROM `article` WHERE url = '%s'" % \
					(url)
				self.dataBase.execution(sql)

				article_id = self.dataBase.fetch('one')

				sql = "DELETE FROM `article_tag` WHERE article_id = '%d'" % \
					(article_id)
				self.dataBase.execution(sql)

				for tag in taglist:

					sql = "SELECT * FROM `hashtag` WHERE hashtagName = '%s'" % \
						(tag)
					self.dataBase.execution(sql)

					if self.dataBase.fetch('one') == None:
						sql = "insert into `hashtag` (`hashtagName`, `hashtagTrack`, `updatetime`) values ('%s','%d','%s')" % \
							(tag, 0, curTime)
						self.dataBase.execution(sql)

					sql = "SELECT hashtag_id FROM `hashtag` WHERE hashtagName = '%s'" % \
						(tag)
					self.dataBase.execution(sql)

					hashtag_id = self.dataBase.fetch('one')

					sql = "insert into `article_tag` (`article_id`, `hashtag_id`, `updatetime`) values ('%d','%d','%s')" % \
						(article_id, hashtag_id, curTime)
					self.dataBase.execution(sql)

				# self._tagListProcess(taglist)

				for i in soup.findAll('time'):
					if i.has_attr('datetime'):
						timediff.append(i['datetime'])
						#print(i['datetime'])

	# 過濾tag
	def _filter_tag(self, soup):
		desc = ""
		taglist = []
		for item in soup.findAll('a'):
			desc = desc + " " + str(item.string)

			# Extract tag list from Instagram post description
			taglist = desc.split()
			taglist = [x for x in taglist if x.startswith('#')]
			index = 0
			while index < len(taglist):
				taglist[index] = taglist[index].strip('#')
				index += 1

		return taglist

	def followUser(self):

		followList = []
		checkOverUserList = []
		checkOverUserListFilePath = self.basePath+'/json/checkOverUserList.json'
		followListFilePath = self.basePath+'/json/'+str(self.today)+'-followList.json'

		sql = "SELECT userName, follows, beFollows FROM `user`"
		self.dataBase.execution(sql)
		users = self.dataBase.fetch('all')

		if os.path.isfile(checkOverUserListFilePath):
			with open(checkOverUserListFilePath, 'r') as i:
				checkOverUserList = json.load(i)

		if os.path.isfile(followListFilePath):
			with open(followListFilePath, 'r') as i:
				followList = json.load(i)

		users = [l for l in users if not l[0] in checkOverUserList]

		# users = [('l_jh10000',0,0)]
		for user in users:
			
			print('用戶:'+user[0])
			try:
				userName = user[0]
				follows = user[1]
				beFollows = user[2]
				url = 'https://www.instagram.com/'+user[0]
				self.driver.get(url)

				soup = BeautifulSoup(self.driver.page_source,"lxml")

				# user.append(user)
				time.sleep(1)
				personalArticle = self.driver.find_elements_by_tag_name("section")
				userInformation = personalArticle[0].find_element_by_tag_name("section").find_element_by_tag_name("ul").find_elements_by_tag_name("span")
			
				locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' )
				articles = locale.atoi(userInformation[1].text.split(' ')[0])
				try:
					beFollows = locale.atoi(userInformation[2].text.split(' ')[0])
				except:
					beFollows = locale.atoi(userInformation[2].get_attribute("title"))
				try:	
					follows = locale.atoi(userInformation[3].text.split(' ')[0])
				except:
					follows = locale.atoi(userInformation[3].get_attribute("title"))

				curTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

				# print('用戶:'+userName)
				print('文章數:'+str(articles))
				print('追蹤數:'+str(follows))
				print('被追蹤數:'+str(beFollows))

				sql = "UPDATE `user` SET `articles` = '%d', `follows` = '%d', `beFollows` = '%d', `updatetime` = '%s' WHERE `userName` = '%s'" % \
					(articles, follows, beFollows, curTime, userName)
				self.dataBase.execution(sql)

				if follows > beFollows and follows >= 400:
					buttonElement = self.driver.find_elements_by_tag_name("button")
					# for button in buttonElement:
					# 	if button.text == self.followText:
					# 		button.click()
					# 		print('追隨')

					followList.append(userName)
			
				if not userName in checkOverUserList:
					checkOverUserList.append(userName)

				if len(followList) >= 50:
					break

				if len(checkOverUserList)%100 == 0:
					print("暫停15分鐘")
					time.sleep(random.randint(900, 1200))

			except:
				try:
					if self.driver.find_element_by_tag_name("h2").text == self.error:
						break
				except:
					print("error")

			time.sleep(random.randint(15,60))
			print("----------")
			
		print('followList:'+str(len(followList)))
		print('checkOverUserList:'+str(len(checkOverUserList)))

		with open(followListFilePath,"w") as f, open(checkOverUserListFilePath,"w") as i:
			json.dump(followList, f)
			json.dump(checkOverUserList, i)
			print("加载入文件完成...")

	def unfollowUser(self):

		threeDaysAgo = self.today + datetime.timedelta(days=-3)

		followListFilePath = self.basePath+'/json/'+str(threeDaysAgo)+'-followList.json'

		if os.path.isfile(followListFilePath):
			with open(followListFilePath, 'r') as f:
				followList = json.load(f)

		for user in followList:
			print("用戶: "+user)

			url = 'https://www.instagram.com/'+user
			self.driver.get(url)
			
			followingButton = self.driver.find_elements_by_tag_name("button")
			for button in followingButton:
				if button.text == self.followingText:
					button.click()
					cancelFollowButton = self.driver.find_elements_by_tag_name("button")
					for button in cancelFollowButton:
						if button.text == self.cancelFollowText:
							button.click()
							print("取消追蹤")
							break

			time.sleep(5)


	def getFollowList(self):

		followListFilePath = self.basePath+'/json/'+str(self.today)+'-followList.json'

		print(self.today)
		print("--------")
		if os.path.isfile(followListFilePath):
			with open(followListFilePath, 'r') as i:
				followList = json.load(i)

		for user in followList:
			print("https://www.instagram.com/"+user)
















