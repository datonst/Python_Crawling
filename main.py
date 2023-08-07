import requests
from bs4 import BeautifulSoup 
from article_page import * 
import pandas as pd
import os
from fastapi import FastAPI,Request,Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
app=FastAPI()
templates = Jinja2Templates(directory="templates")


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
        
    if(id>3): break

@app.post("/search",response_class=HTMLResponse)
def searchlist(request: Request,query_search: str =Form(...)):
    message=f"Find \'{query_search}\' Success"
    list_search=[article for article in list_result if query_search in article[2]]
    print(list_search)
    if not list_search:
        message="NOT FOUND"
    context= {"request": request,"list_search":list_search,"message":message,"name_query": query_search}
    return templates.TemplateResponse("searchName.html", context)

@app.get("/",response_class=HTMLResponse)
def home(request: Request): 
    context= {"request": request,"list_result":list_result}
    return templates.TemplateResponse("home.html", context)
    # with open(os.path.join(root, 'index.html')) as fh:
    #     data = fh.read()
    # return Response(content=data, media_type="text/html")
    # return render(request,'home.html',{"list_result":list_result})
    
df=pd.DataFrame(list_result,columns=["Id","Title","Article","Author","Date Published"])
df['Date Published'] = pd.to_datetime(df['Date Published'],dayfirst=True,format="%d/%m/%Y")
df.to_html("kq.csv",header=True,index=False)
