#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#Importing dependencies
import requests
import time
import datetime as dt
import csv
import re
from bs4 import BeautifulSoup as BS


# In[ ]:


#Creating CSV that links collected from each store page will be added to
header = ['title','link', 'dateAccessed']
with open('ProductURL.csv', 'w', newline = '', encoding = 'UTF8') as b:
    writer = csv.writer(b)
    writer.writerow(header)
    
#Creating CSV that information from each product will be added to
productHeader = ['title', 'genre', 'price', 'quantity', 'inStock', 'UPC', 'productType', 'dateAccessed']
with open('ProductInformation.csv', 'w', newline = '', encoding = 'UTF8') as a:
    writer = csv.writer(a)
    writer.writerow(productHeader)

#Function for extracting product information
def productExtract(url):
    page = requests.get(url, headers = headers)
    soup = BS(page.content, 'html.parser')

    #Select the title
    title = soup.html.title.text
    title = title[:title.index('|')].strip()

    #Select the genre, which is only located in a breadcrumb list
    genre = soup.find('ul').text
    #Create list of breadcrumb items
    genre = genre.split('\n')
    genre = list(filter(None, genre))[-2]

    #Selecting price
    price = soup.find(class_ = 'price_color').get_text()

    #Selecting quantity and availability (inStock)
    #Returns a statement ie: 'In stock (21) available'
    availability = soup.find(class_ = 'instock availability').text

    #Selecting quantity by filtering numeric values into a list
    quantity = re.findall(r'\d+', availability)[0]

    #Using quantity to determine availability
    quantity = int(quantity)
    if quantity <= 0:
        inStock = 'no'
    else:
        inStock = 'yes'

    #Selecting UPC and product type
    UPC = soup.html.table.td.text
    productType = list(soup.find_all('td'))[1].text

    #Determine when data was accessed
    dateAccessed = dt.datetime.now().strftime("%Y-%m-%d %H:%M")

    #Write results onto CSV with product information
    results = [title, genre, price, quantity, inStock, UPC, productType, dateAccessed]
    with open('ProductInformation.csv', 'a+', newline = '', encoding = 'UTF8') as a:
        writer = csv.writer(a)
        writer.writerow(results)
        
#Function for collecting URL for every product in store page
def pageCollect(url2):
    page = requests.get(url2)
    soup = BS(page.content, 'html.parser')
    
    #Collect all containers containing product title and link
    bookContainers = soup.find_all("li", {'class':'col-xs-6 col-sm-4 col-md-3 col-lg-3'})

    for container in bookContainers:
        #Select title
        containerTitle = container.find('a').find('img').get('alt')
        
        #Select link
        href = container.find('a').get('href')
        bookLink = 'https://books.toscrape.com/catalogue/' + href
        
        #Determine when data was accessed
        dateAccessed = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
        
        #Write results onto CSV with product links
        row = (containerTitle, bookLink, dateAccessed)
        with open('ProductURL.csv', 'a+', newline = '\n', encoding = 'UTF8') as b:
            writer = csv.writer(b)
            writer.writerow(row)
        productExtract(bookLink)
        
#Finds total number of product store pages
#Returns string ie: 'Page 1 of x (x = number of pages)'
pageNum = soup.find("ul", {"class": "pager"}).text.strip()
pageTotal = int(pageNum[pageNum.index('of') + 3 : pageNum.index('next')])

#For moving between pages
#GENERATES A NEW URL
for i in range(1, pageTotal + 1):
    print('Currently parsing through page ' + str(i) + '.')
    URL = 'https://books.toscrape.com/catalogue/page-' + str(i) + '.html'
    pageCollect(URL)

