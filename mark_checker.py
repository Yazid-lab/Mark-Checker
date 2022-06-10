from base64 import urlsafe_b64encode
from win10toast import ToastNotifier
import requests
from bs4 import BeautifulSoup
import json
import re
import time
import telegram_send
def extract(rows):#extract each table cell and return a list of its values
    data_list=list()
    for row in rows:
        for data in row:
            if data not in {"\n"}:
                data_list.append(data.text)
    return data_list

def strip(test):#remove new line charater from input string
    while '\n' in test:
        test.remove('\n')

#returns a list of subjects (dicts) each containing name and different marks
def get_marks(data_set):
    subjects=list()
    for data in data_set[0:]:
        strip(data)
        if (data[2] in {'1','2','3','4'}):
            data[3]=re.sub(' +',' ',data[3])
            subject={"name":data[3],"test":data[5],"tp":data[7],"exam":data[8],"avg":data[9]}
            subjects.append(subject)

        else:#first row of each extended cell
            data[4]=re.sub(' +',' ',data[4])
            subject={"name":data[4],"test":data[6],"tp":data[8],"exam":data[9],"avg":data[10]}
            subjects.append(subject)
    return subjects
    

URL_LOGIN='http://www.enit.rnu.tn/RegisterENIT/login.php?au=2122'
URL_RELEVEE_DE_NOTES=''
URL_CONSULTER_NOTES=''
LOGIN_DATA={'submitted':'1','AUA':'2122','username':'','password':'','Submit':'Submit'}
while True :    
    #create a session
    s=requests.Session()
    #login
    s.post(URL_LOGIN, data=LOGIN_DATA)
    #save marks webpage in variable MARKS_WEB_PAGE_1
    MARKS_WEB_PAGE_1 = s.get(URL_RELEVEE_DE_NOTES)
    #create an instance to scrape marks web page
    soup=BeautifulSoup(MARKS_WEB_PAGE_1.text,features="lxml")
    #find the table that contains the marks
    table=soup.find_all('table')[1]
    #extracts all the table rows
    rows=table.find_all('tr')

    #create a list containing the cells of the marks table
    table_data=[x.find_all('td') for x in rows]
    data_set=list()
    print("relevé de notes")

    #cleaning up the scraped marks and adding them to a list called data_set
    for data in table_data:
        data_set.append(extract(data))
    #getting pre saved marks
    try:# if file already exists then load the data
        f= open('marks.json',encoding='utf8')
        data=json.load(f)
    except:# if file is unexisting then set data to empty
        data=[]

    #get the subjects in json format
    subjects=get_marks(data_set)
    my_json=json.dumps(subjects,ensure_ascii=False,indent=0).encode('utf8')
    if(data==subjects):#checking if there's new marks
        print("no new marks")#no new marks found
    else:#new marks found and outputting them to the user.
        print( "NEW MARKS!!!")
        telegram_send.send(messages=["CHECK FOR NEW MARKS!"])

        for i in range(len(subjects )):
            print(subjects[i])
        with open('marks.json', 'w', encoding='utf8') as json_file:
            json_file.write(my_json.decode()) 

    #checking the other marks web page(since some marks don't show up in the first one)

    print("Consulter notes")
    #saving the HTML contents of the page in a variable called MARKS_WEB_PAGE_2
    MARKS_WEB_PAGE_2=s.get(URL_CONSULTER_NOTES)
    #instanciating a scraper on the webpage
    soup2=BeautifulSoup(MARKS_WEB_PAGE_2.text,features="lxml")
    #find the marks table
    table=soup2.find_all('table')[0]
    #getting the marks and printing them out to the user
    tbody=table.find_all('tbody')
    table_data=[x.find_all('td') for x in rows]
    for data in tbody:
        print(data.find_all('td')[0].text,data.find_all('td')[2].text,' ',data.find_all('td')[3].text)
    time.sleep(900)