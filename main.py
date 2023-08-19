from bs4 import BeautifulSoup 
from article_page import * 
import pandas as pd
import uvicorn
from fastapi import FastAPI,Request,Form,File,UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import asyncio,aiohttp
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse,FileResponse
import datetime
from fastapi.staticfiles import StaticFiles
import os
import pathlib
app=FastAPI()
templates = Jinja2Templates(directory="templates")

app.mount('/static', StaticFiles(directory='static', html=True), name='static')  #-> Đây là thêm thư mục static


BASE_DIR= os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR=os.path.join(BASE_DIR,"uploads")

list_result=[]
list_url=[]
reload=False
g_url_crawling=""
isRunAPI=False
stopAPI=False
def set_url(url_crawling):
    global g_url_crawling,isRunAPI
    if g_url_crawling != url_crawling : 
        g_url_crawling=url_crawling
        isRunAPI=False
    if "ftu.edu.vn" in g_url_crawling  :
        list_url.clear()
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
    global isRunAPI,stopAPI
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
            if stopAPI ==True: break
            title=issue.find("a", class_="title").text.strip()[:-7]
            link=issue.find("a", class_="title")["href"]
            list_page=article_page(link,title,id)
            
            for page_article in list_page:
                id+=1
                list_result.append(page_article)
            if id>3: break
        finish=datetime.datetime.now()-start
        print(finish)
    isRunAPI=False   
    return 


def stopRunAPI():
    global stopAPI
    stopAPI=True
    while (isRunAPI):   #wait until API done
        continue;
    stopAPI=False
    return

@app.get("/",response_class=HTMLResponse)
def home(request: Request):

    context= {"request": request,"url_crawling":g_url_crawling}
    return templates.TemplateResponse("home.html", context)



@app.post("/search",response_class=HTMLResponse)  #chuẩn phải là get nếu làm backend dùng SQL Select * query, chứ không tạo ra list mới
def searchlist(request: Request,query_search: str =Form(...)):
    message=f"Find \'{query_search}\' Success"
    list_search=[article for article in list_result if query_search in article[2]]
    if not list_search:
        message="NOT FOUND"
    context= {"request": request,"list_search":list_search,"message":message,"name_query": query_search,"url_crawling":g_url_crawling}
    return templates.TemplateResponse("searchName.html", context)

@app.get("/crawling",response_class=HTMLResponse)
def getCrawling(request: Request): 
    message="NULL"
    context= {"request": request,"list_result":list_result,"message":message,"url_crawling":g_url_crawling}
    return templates.TemplateResponse("crawling.html", context)
# run

@app.post("/crawling",response_class=HTMLResponse)
def postCrawling(request: Request,url_crawling: str=Form(...)):
    global isRunAPI,stopAPI
    message="NOT FOUND"
    if(isRunAPI) :
        stopRunAPI()
        # context= {"request": request,"message":message,"url_crawling":url_crawling}
        # return templates.TemplateResponse("load_data.html", context) 
    if(set_url(url_crawling)==True):
        message="FOUND" 
        if isRunAPI==False:
            isRunAPI=True
            # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            results=asyncio.run(root_data())  
            parse(results)

    context= {"request": request,"list_result":list_result,"message":message,"url_crawling":g_url_crawling}
    return templates.TemplateResponse("crawling.html", context)


@app.post("/csv")
def data_to_csv():
    df=pd.DataFrame(list_result,columns=["Id","Title","Article","Author","Date Published"])
    df['Date Published'] = pd.to_datetime(df['Date Published'],dayfirst=True,format="%d/%m/%Y")
    df.to_csv("kq.csv",header=True,index=False)
    this_path=pathlib.Path(__file__).parent  # or pathlib.PurePath()
    path= this_path /"kq.csv"
    headers = {'Content-Disposition': 'attachment; filename="kq.csv"'}
    return FileResponse(path, headers=headers,media_type='text/csv')

# https://www.youtube.com/watch?v=m6Ma6B6VlFs
# https://stackoverflow.com/questions/64489679/download-pdf-file-using-pdfkit-and-fastapi/71728386#71728386
@app.post("/excel")
def data_to_excel():
    df=pd.DataFrame(list_result,columns=["Id","Title","Article","Author","Date Published"])
    df['Date Published'] = pd.to_datetime(df['Date Published'],dayfirst=True,format="%d/%m/%Y")
    df.to_excel("result.xlsx",header=True,index=False)
    this_path=pathlib.Path(__file__).parent  # or pathlib.PurePath()
    path= this_path /"result.xlsx"
    headers = {'Content-Disposition': 'attachment; filename="result.xlsx"'}
    return FileResponse(path, headers=headers,media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')




# if __name__=='__main__':
#     uvicorn.run(apphost="127.0.0.1",port=8000)