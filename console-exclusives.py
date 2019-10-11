import requests
# pip install --upgrade beautifulsoup4
from bs4 import BeautifulSoup
from urlparse import urljoin, urlsplit, urlunsplit
import re
import operator
import logging
import time

logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.DEBUG)

#
# Get main site URL for traversals and rebuilding page URLs
#
def get_base_url(url):
    split_url = urlsplit(url)
    return split_url.scheme+"://"+split_url.netloc

#
# Find next page link
#
def next_page(soup, url):
    next_page = soup.find("a", string=re.compile('^next'))
    if next_page:
        url = urljoin(get_base_url(url),next_page.get('href'))
    else:
        url = False
    
    return url
    
#
# Get game_list of Wii exclusives from Wikipedia
#
def get_exclusives_game_list_from_wiki(url):
    games={}

    while url:
        
        # Get page content
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')

        # Grab DIV that contains game names to omit other text
        div = soup.find("div", class_="mw-category")
        
        # Grab all the title text
        for link in div.find_all('a'):
            games[link.get('title').encode("ascii","ignore")]=""

        url = next_page(soup, url)
        time.sleep(2)
        logging.info('Sleeping for 2 seconds to prevent ban...')

    #
    # Add missing exclusives
    #

    # TODO Fix this!!
    games['Super Mario Galaxy']=""
    games['Super Mario Galaxy 2']=""

    return games

def get_scores_and_update(game_list,url):

    headers = {
            'user-key': 'ca3cdbfca7c461c0c72e702a58657bfc',
            'Accept': 'application/json'
        }

    base_url = "https://api-v3.igdb.com/games/"


    r = requests.get('https://api-v3.igdb.com/games/?fields=name&platforms={2}', headers=headers)

"""     while url:
        #for i in range (currentPage, maxPage):
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        headers={'User-Agent':user_agent,} 
        page = requests.get(url,headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')

        # Minimize search to game layer
        div = soup.find("div", class_="product_condensed")

        for product in div.find_all("div", class_="product_wrap"):
            product_title = product.contents[1].text.strip()
            if product_title in game_list:
                product_metascore=product.contents[3].text.strip().encode()
                game_list[product_title]=product_metascore

        url=next_page(soup,url)
        time.sleep(2)
        logging.info('Sleeping for 2 seconds to prevent ban...') """

    return game_list

def sortedByValue(game_list):
    return sorted(game_list.items(), key=operator.itemgetter(1))


url1 = "https://en.wikipedia.org/w/index.php?title=Category:Wii-only_games"
url2 = "https://www.metacritic.com/browse/games/score/metascore/all/wii/filtered?sort=desc"
game_list = get_scores_and_update(get_exclusives_game_list_from_wiki(url1),url2)
sorted_list = sortedByValue(game_list)

mx = len(max((sub[0] for sub in sorted_list),key=len))
for row in sorted_list:
    print(" ".join(["{:<{mx}}".format(ele,mx=mx) for ele in row]))
