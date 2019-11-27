import sys
import requests
import pprint
import re

from bs4 import BeautifulSoup
from bs4.diagnose import diagnose
from urllib.parse import urlparse
from collections import OrderedDict

def get_html_from_url(url):
  headers = {'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:54.0) Gecko/20100101 Firefox/54.0'}
  result = requests.get(url, headers=headers)
  return result.content

def get_url_from_href(href):
  parsed_uri = urlparse(URL)
  parsed_url_root = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
  return '{}{}'.format(parsed_url_root, href)

def get_item_name(item_html):
  return ' '.join(item_html.select('.pod-plp__description a')[0].stripped_strings).replace('Best Seller ', '')

def get_item_url(item_html):
  href = item_html.find('a', attrs={'data-podaction': 'product image'})['href']
  return get_url_from_href(href)

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
    return None

  savings_text = savings_html.text.strip()
  matches = re.search('\$(?P<dollars>\d+(?:\.\d+)?) \((?P<percent>\d+)\%\)', savings_text)
  if matches:
    return matches.groupdict()

  return None

def get_items(pages):
  items = []

  for page in pages:
    soup = BeautifulSoup(page, 'html5lib')

    divs = soup.find_all('div', class_='pod-inner')

    for div in divs:
      item = {}
      try:
        item_name = get_item_name(div)
        item['name'] = item_name

        item_url = get_item_url(div)
        item['url'] = item_url

        item_price = get_item_price(div)
        item['price'] = item_price

        item_savings = get_item_savings(div)
        if item_savings is None:
          continue

        item['savings'] = item_savings
        item['dollar_savings'] = float(item_savings['dollars'])
        item['percent_savings'] = float(item_savings['percent'])
      except:
        print("💩 Error getting item and details. Skipping")
        continue

      items.append(item)

  pprint.pprint(sorted(items, key = lambda i: i['percent_savings'],reverse=False))


def get_html_pages(url):
  pages = []
  next_page = url

  while next_page:
    html = get_html_from_url('{url}'.format(url = next_page))
    pages.append(html)

    soup = BeautifulSoup(html, 'html5lib')
  
    next_page = soup.find('a', class_='hd-pagination__link', attrs={ 'title': 'Next' })

    if next_page:
      next_page = get_url_from_href(next_page['href'])
    else:
      next_page = False

  return pages




if len(sys.argv) == 1:
  print("You will need to provide the url to scrap for dealz. 👌")
  sys.exit(0)

URL = sys.argv[1]
pages = get_html_pages(URL)
get_items(pages)




