from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup as soup
import time

#functions
def sep_name(string):
	'''
	Separates the name and package size
	>>> name = "Purina Tidy Cats Cat Litter 4-In-1 Strength Clumping for Multiple Cats - 20 Lb"
	>>> separated = sep_name(name)
	>>> separated[0]
	'Purina Tidy Cats Cat Litter 4-In-1 Strength Clumping for Multiple Cats'
	>>> separated[1]
	'20 Lb'

	'''
	sep = string.split("-")
	#name has no hyphen
	if len(sep) <= 2:
		return sep

	num = -1
	#find index to split
	for i, charac in enumerate(sep):
		if charac[0] == " " and charac.strip()[0].isdigit():
			if i == 0:
				break
			num = i
			break
	sep[0:num] = ['-'.join(sep[0:num])]
	sep[1:] = ['-'.join(sep[1:])]
	return sep



#vars

GOOGLE_CHROME_BIN = "/app/.apt/usr/bin/google-chrome"
CHROMEDRIVER_PATH = "/app/.chromedriver/bin/chromedriver"

# open webdriver, get url
url = "https://shop.vons.com/welcome.html"
#driver = webdriver.Chrome()

chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = GOOGLE_CHROME_BIN
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, chrome_options=chrome_options)
driver.get(url)
time.sleep(3)

#input zip code
inputElement = driver.find_element_by_id("zipcode")
inputElement.send_keys('91775')
inputElement.send_keys(Keys.ENTER)
time.sleep(3)

#go into popular items page
link = driver.find_element_by_link_text('VIEW ALL')
link.click()
time.sleep(3)

#get page source, find the containers
html = driver.page_source
page_soup = soup(html, "html.parser")
containers = page_soup.findAll('product-item', {'class':'col-xs-12 col-sm-6 col-md-4'})

#write to file
filename = "products.csv"
f = open(filename, "w")

headers = "Item Name, Package Size, Price Per, Item Price\n"

f.write(headers)

#fill in csv
for container in containers:
	#get name
	item_name = container.h3.a.text.strip()

	#get package size
	hiph = False
	#check if package size exists in name
	for charac in item_name:
		if charac == "-":
			hiph = True
			break
	if hiph:
		sep = sep_name(item_name)
		item_name = sep[0].strip()
		package_size = sep[1].strip()
	#no package size (usually fruits/veggies)
	else:
		package_size = "Each"

	#get price per
	price_per = container.p.span.text.strip()

	#get price
	price_container = container.findAll("div", {"class":"product-price-con"})
	price = price_container[0].text
	if ("Original" in price) and ("Your" in price):
		price = price.split("Y", 1)[0].strip().strip("Original Price")
	elif "Your" in price:
		price = price.strip().strip("Your Price")
	elif "Original" in price:
		price = price.strip().strip("Original Price")

	f.write(item_name + "," + package_size + "," + price_per + "," + price + "\n")

f.close()
