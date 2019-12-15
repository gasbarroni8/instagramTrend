import re
from models import user_agents
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
# available since 2.4.0
from selenium.webdriver.support.ui import WebDriverWait 
# available since 2.26.0
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class Selenium:

	def __init__(self, browserDriver):
		
		self.chrome_options = webdriver.ChromeOptions()

		self.chrome_options.add_argument("--user-data-dir=selenium")
		self.chrome_options.add_argument("--window-size=1920,1080")
		self.chrome_options.add_argument('--headless')
		self.chrome_options.add_argument('no-sandbox')
		self.browserDriver = browserDriver

	def openrBowser(self):

		self.driver = webdriver.Chrome(self.browserDriver,chrome_options=self.chrome_options)
		self.driver.set_page_load_timeout(35)

		return self.driver

	def getSportData(self, url):

		self.driver.get(url)

		data = re.sub(r'</?\w+[^>]*>','',self.driver.page_source)

		return data


	def quitBrowser(self):

		self.driver.quit()

	def timeoutException():
		
		return TimeoutException

