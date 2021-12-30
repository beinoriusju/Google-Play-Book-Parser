from bs4 import BeautifulSoup
import sys
import urllib
import json

from google_currency import convert

ERROR_REQUEST = "There was an error sending request."

#Creates the soup
def createSoup(url):
    try:
        response = urllib.request.urlopen( url )
    except urllib.error.HTTPError as e:
        print( "HTTPError with: ", url, "\t", e )
        return None
        
    the_page = response.read()

    soup = BeautifulSoup( the_page, 'lxml' )   
    
    return soup
    
def getData(soup):
    json_data = soup.find( 'script', { 'type': 'application/ld+json' } )

    return json.loads(json_data.contents[0])

def getBookTitle(data):
    return data['name']

def getBookAuthor(data):
    return ', '.join([author['name'] for author in data['author']])

def getBookPrice(data):
    expectsAcceptanceOf = data['workExample']['potentialAction']['expectsAcceptanceOf']

    real_offers = list(filter(lambda item: item.get('@type') == 'Offer', expectsAcceptanceOf))
    
    #Get first available offer
    if len(real_offers):
        return { 'amount': real_offers[0]['price'], 'currency': real_offers[0]['priceCurrency'] }

if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        print(sys.stderr, 'SYNTAX: parse_book.py [book-id]')
        sys.exit(-1)

    url = 'https://play.google.com/store/books/details/?id=' + args[0]

    soup = createSoup(url)
    data = getData(soup)

    title = getBookTitle(data)
    price = getBookPrice(data)
    author = getBookAuthor(data)

    if title and price and author:
        response = { 'title': title, 'author': author, 'price': price }
        print(json.dumps(response))
    else:
        print(ERROR_REQUEST)  
