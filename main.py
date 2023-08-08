from bs4 import BeautifulSoup 
from article_page import * 
import pandas as pd
from fastapi import FastAPI,Request,Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import asyncio,aiohttp
from fastapi.responses import RedirectResponse
import datetime

app=FastAPI()
templates = Jinja2Templates(directory="templates")

list_result=[]
list_url=[]
url_search=""

def set_url(url_search_):
    if "ftu.edu.vn" in url_search_  :
        for index_page in range (1,3):
            url=f"https://jiem.ftu.edu.vn/index.php/jiem/issue/archive/{index_page}"
            list_url.append(url)
        return True    
    else:
        return False
        #Nếu không có thì ....


async def get_page(session, url):   
    async with session.get(url) as r:
        # if r.status !=200:
        #     r.raise_for_status()
        return await r.text() # clone html in queue
    
async def get_all(session):
    tasks=[]
    for url in list_url:
        task= asyncio.create_task(get_page(session,url))
        tasks.append(task)
    results=await asyncio.gather(*tasks) # get list task ( clone all html page) in queue
    return results

async def root_data():
    async with aiohttp.ClientSession() as session:
        data= await get_all(session)   #  
        return data

def parse(results):
    list_result.clear()
    id =0
    for html in results:
        soup=BeautifulSoup(html,"html.parser") # soup=BeautifulSoup(html,"html.parser")
        media_list=soup.find("div",class_='issues media-list')
        list_issues=media_list.find_all("div",class_="issue-summary-body")
        start=datetime.datetime.now()
        x=0
        for issue in list_issues:
            print(x)
            x+=1
            title=issue.find("a", class_="title").text.strip()[:-7]
            link=issue.find("a", class_="title")["href"]
            list_page=article_page(link,title,id)
            
            for page_article in list_page:
                id+=1
                list_result.append(page_article)
        finish=datetime.datetime.now()-start
        print(finish)
           

    return 

@app.get("/list",response_class=HTMLResponse)
def home(request: Request): 
    message="NULL"
    context= {"request": request,"list_result":list_result,"message":message,"url_search":url_search}
    return templates.TemplateResponse("home.html", context)
# run

@app.get("/",response_class=HTMLResponse)
def home_search(request: Request):
    context= {"request": request,"url_search":url_search}
    return templates.TemplateResponse("home_search.html", context)

@app.post("/search",response_class=HTMLResponse)
def searchlist(request: Request,query_search: str =Form(...)):
    message=f"Find \'{query_search}\' Success"
    list_search=[article for article in list_result if query_search in article[2]]
    if not list_search:
        message="NOT FOUND"
    context= {"request": request,"list_search":list_search,"message":message,"name_query": query_search,"url_search":url_search}
    return templates.TemplateResponse("searchName.html", context)


@app.post("/list",response_class=HTMLResponse)
def home(request: Request,url_search: str=Form(...)): 
    message="NOT FOUND"
    if(set_url(url_search)==True):
        message="FOUND"     
        results=asyncio.run(root_data())  
        parse(results)
    context= {"request": request,"list_result":list_result,"message":message,"url_search":url_search}
    return templates.TemplateResponse("home.html", context)
    # with open(os.path.join(root, 'index.html')) as fh:
    #     data = fh.read()
    # return Response(content=data, media_type="text/html")
    # return render(request,'home.html',{"list_result":list_result})
    
def data_to_csv():
    df=pd.DataFrame(list_result,columns=["Id","Title","Article","Author","Date Published"])
    df['Date Published'] = pd.to_datetime(df['Date Published'],dayfirst=True,format="%d/%m/%Y")
    df.to_html("kq.csv",header=True,index=False)