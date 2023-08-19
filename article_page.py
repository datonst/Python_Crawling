import requests
from bs4 import BeautifulSoup
from date_publish import *
import asyncio,aiohttp

def article_page(link,title,id):
    req=requests.get(link)
    soup=BeautifulSoup(req.text,"html.parser")
    list_article =soup.find_all("div",class_="col-md-12 pl-0")
    list_page=[]
    for article in list_article:
        id+=1
        if id>3: break 
        name_article=article.find('a').text.strip()
        author_article=article.find("div",class_="meta").text.strip()
        date= date_publish( article.find('a')["href"])
        list_page.append([id,title,name_article,author_article,date])
    return list_page
        
     


