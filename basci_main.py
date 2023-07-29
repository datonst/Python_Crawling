import requests
from bs4 import BeautifulSoup 
from article_page import * 
import pandas as pd
import os
id =0
list_result=[]
for index_page in range (1,3):
    url=f"https://jiem.ftu.edu.vn/index.php/jiem/issue/archive/{index_page}"
    req=requests.get(url)
    soup=BeautifulSoup(req.text,"html.parser") 
    media_list=soup.find("div",class_='issues media-list')
    list_issues=media_list.find_all("div",class_="issue-summary-body")
    for issue in list_issues:
        title=issue.find("a", class_="title").text.strip()[:-7]
        link=issue.find("a", class_="title")["href"]
        list_page=article_page(link,title,id)
        for page_article in list_page:
            id+=1
            list_result.append(page_article)
        
        
df=pd.DataFrame(list_result,columns=["Id","Title","Article","Author","Date Published"])
df['Date Published'] = pd.to_datetime(df['Date Published'],dayfirst=True,format="%d/%m/%Y")
df.to_excel("result.xlsx",header=True,index=False)


 
    

        

        
    
