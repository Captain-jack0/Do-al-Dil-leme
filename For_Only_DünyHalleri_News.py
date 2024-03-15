#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 15 09:50:02 2024

@author: merye
"""

import pandas as pd
#Veri Kazıma
from bs4 import BeautifulSoup as bs
import requests 
#Konsol Güzelleştirme
from IPython.display import clear_output

sections = [           
            "https://www.dunyahalleri.com/category/teknoloji-bilim/page/",
            "https://www.dunyahalleri.com/category/internet-girisimler/page/",
            "https://www.dunyahalleri.com/category/tasarim-inovasyon/page/"
            ]

urls = []
#Öncelikle bir Kategori seçiyoruz.
for section in sections:
    #Kategorinin içerisinde sırayla 100 sayfa gezineceğiz.
    for i in range(1,100):
        try:
            #Öncelikle URL'imizi oluşturuyoruz. Örneğin;
            #https://www.dunyahalleri.com/category/kultur-sanat/page/25
            newurl = section+str(i)
            print(newurl)
            
            #Url'nin içerisindeki bütün html dosyasını indiriyoruz.
            html = requests.get(newurl).text
            soup = bs(html, "lxml")
            
            #Yukarıdaki şemadada görüldüğü gibi bütün makaleler bu  element'in içerisinde yer alıyor.
            #Bizde bütün makaleleri buradan tags adında bir değişkene topluyoruz.
            tags = soup.findAll("div", class_="row row-eq-height herald-posts")[0]
            
            #Sırayla bütün makalelere girip, href'in içerisindeki linki urls adlı listemize append ediyoruz.
            for a in tags.find_all('a', href=True):
                urls.append((section.split("/")[4],a['href']))
        except IndexError:
            break
        
        
urldata = pd.DataFrame(urls)
urldata.columns = ["Kategori","Link"]
urldata.head()

urldata = urldata.drop_duplicates()
urldata.to_csv('urldata.csv')

def GetData(url):
    try:
        #Url içerisindeki html'i indiriyoruz.
        html = requests.get(url).text
        soup = bs(html, "lxml")
        
        #Belirlediğimiz element'in altındaki bütün p'leri seçiyoruz.
        body_text = soup.findAll("div", class_="tldr-post-content")[0].findAll('p')
        
        #Body_text adındaki metni tek bir string üzerinde topluyoruz.
        body_text_big = ""
        for i in body_text:
            body_text_big = body_text_big +i.text
        
        #Başlığı ve zamanı'da element isimlerinden bu şekilde seçip, metinlerini alıyoruz.
        header = soup.find("h1", class_="entry-title h1").text
        timestamp = soup.find("span", class_="updated").text
        
        #Özetin bulunduğu element'in metin kısmını alıyoruz.
        summarized = soup.find("div", class_="tldr-sumamry").text
        return ((url,header,body_text_big,summarized,timestamp))
    
    #Link boş ise verilen hata üzerine Boş Data mesajını dönüyor.
    except IndexError:
        return ("Boş Data")
    
    #Eğer link haftalık özet ise özet kısmı olmadığından oraya haftalık özet yazıp, sonuçlar o şekilde dönüyor.
    except AttributeError:
        return ((url,header,body_text_big,"Haftalık Özet",timestamp))
    
bigdata = []
k = 0
for i in urldata.Link:
    clear_output(wait=True)
    print(k)
    bigdata.append(GetData(i))
    k = k + 1
    
bigdatax = pd.DataFrame(bigdata)
bigdatax.drop([5,6,7],axis=1,inplace=True)
bigdatax.drop(bigdatax[bigdatax[0]=="B"].index,axis=0,inplace=True)
bigdatax.columns = ["Link","Başlık","Body_text","Summarized_Text","TimeStamp"]
bigdatax = bigdatax.loc[bigdatax.Link.drop_duplicates().index]
bigdatax.index = range(0,len(bigdatax))
bigdatax.head()