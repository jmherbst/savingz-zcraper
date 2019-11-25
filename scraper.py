import sys
import requests
import re

from bs4 import BeautifulSoup
from bs4.diagnose import diagnose

def get_html_from_url(url):
  headers = {'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:54.0) Gecko/20100101 Firefox/54.0'}
  result = requests.get(url, headers=headers)
  return result.content

def get_item_name(item_html):
  return ' '.join(item_html.select('.pod-plp__description a')[0].stripped_strings).replace('Best Seller ', '')

def get_item_price(item_html):
  item_price = ""
  price_elements = item_html.select('.overflow__inner .price__numbers')[0]
  item_price = "{leading_format}{price}.{trailing_format}".format(leading_format = price_elements.find_all('span')[0].text.strip(),
                                                                  price = price_elements.find('span').next_sibling.strip(),
                                                                  trailing_format = price_elements.find_all('span')[1].text.strip(),
                                                           )
  return item_price

def get_item_savings(item_html):
  '''Returns associated list of savings.
     Key: 
       'dollars',
       'percent',
  '''
  item_savings = {'dollars': '', 'percent': ''}
  savings_html = item_html.select_one('div.price__message')

  if savings_html == None:
    print("No savings info to be found 😩")
    return item_savings

  savings_text = savings_html.text.strip()
  matches = re.search('(?P<dollars>\$\d+(?:\.\d+)?) \((?P<percent>\d+\%)\)', savings_text)
  if matches:
    return matches.groupdict()

  return item_savings

def get_items(html):
  item = {}

  soup = BeautifulSoup(html, 'html5lib')

  items = soup.find_all('div', class_='pod-inner')

  for item in items:
    item_name = get_item_name(item)
    print(item_name)
    item['name'] = item_name

    item_price = get_item_price(item)
    print(item_price)
    item['price'] = item_price

    item_savings = get_item_savings(item)
    print(item_savings) 
    item['savings'] = item_savings

def get_html_pages(url):
  pages = []

  html = get_html_from_url('{url}'.format(url = url))
  pages.append(html)

  return html




if len(sys.argv) == 1:
  print("You will need to provide the url to scrap for dealz. 👌")
  sys.exit(0)

html = get_html_pages(sys.argv[1])
get_items(html)




