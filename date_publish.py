import requests
from bs4 import BeautifulSoup

def date_publish(link):
    req=requests.get(link)
    soup=BeautifulSoup(req.text,"html.parser")
    date= soup.find("div",class_="list-group-item date-published")
    return date.text.strip()[16:].strip()
    
    
     


