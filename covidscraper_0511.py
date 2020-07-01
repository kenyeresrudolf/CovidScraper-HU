# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 12:32:53 2020

@author: rudolf.kenyeres
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 13:02:15 2020

@author: rudolf.kenyeres
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np 
from openpyxl import load_workbook
import datetime as dt
import xlsappend as xls

jelenlegioldal = 0
daraboldal = 2
dataframe = pd.DataFrame()
while jelenlegioldal != daraboldal:
        url = "https://koronavirus.gov.hu/elhunytak?page=" + str(jelenlegioldal)
        try:
            response = requests.get(url,allow_redirects=False)
            html2 = response.text
            #----megtudni hány darab oldalt kell megnézni.----
            if jelenlegioldal == 0:
                daraboldal = int(((html2.split(str('">' + "utolsó »"))[0]).split('utolsó oldalra" href="/elhunytak?page=')[1]))+1
                print(str(daraboldal) + " darab oldal van.")
            #----end----
            print(str(daraboldal) + "/" + str(jelenlegioldal+1) + ". oldal táblázatát olvastam be.")
            #print(pd.read_html(html2)[0])
            dataframe = dataframe.append(pd.read_html(html2)[0])
            jelenlegioldal = jelenlegioldal + 1
        except requests.ConnectionError:
            dataframe = pd.DataFrame([["Nincs kapcsolat!","Nincs kapcsolat!","Nincs kapcsolat!","Nincs kapcsolat!"]],columns=["Nincs kapcsolat!","Nincs kapcsolat!","Nincs kapcsolat!","Nincs kapcsolat!"])
            break                  
print(dataframe)              

#defining the scrapable parts of the site
link = "https://koronavirus.gov.hu/elhunytak?page="
offset = list(range (1,daraboldal))
result = requests.get (link)
src = result.content
soup = BeautifulSoup(src, 'lxml')
age = soup.find_all("td", {"class": "views-field views-field-field-elhunytak-kor"})
gender = soup.find_all("td", {"class": "views-field views-field-field-elhunytak-nem"})
illness = soup.find_all("td", {"class": "views-field views-field-field-elhunytak-alapbetegsegek"})

#age
for i in range(0,len(offset)):
    result = requests.get (link+str(offset[i]))
    src = result.content
    soup = BeautifulSoup(src, 'lxml')
    age += soup.find_all("td", {"class": "views-field views-field-field-elhunytak-kor"})
ages_string = str(age)
ages_splitted = ages_string.split("<")
del ages_splitted[::2]
ages_splitted_short = [i.replace('td class="views-field views-field-field-elhunytak-kor">','') for i in ages_splitted]
ages_splitted_final= [s.replace(':', '') for s in ages_splitted_short]
agetable = pd.DataFrame(ages_splitted_final)
agetable[0] = agetable[0].astype(int)

#sex
for i in range(0,len(offset)):
    result = requests.get (link+str(offset[i]))
    src = result.content
    soup = BeautifulSoup(src, 'lxml')
    gender += soup.find_all("td", {"class": "views-field views-field-field-elhunytak-nem"})
genders_string = str(gender)
genders_splitted = genders_string.split("<")
del genders_splitted[::2]
genders_splitted_short = [i.replace('td class="views-field views-field-field-elhunytak-nem">','') for i in genders_splitted]
genders_splitted_final= [s.replace(':', '') for s in genders_splitted_short]
gendertable = pd.DataFrame(genders_splitted_final)
gendertable[0] = gendertable[0].astype(str)

#illnesses
for i in range(0,len(offset)):
    result = requests.get (link+str(offset[i]))
    src = result.content
    soup = BeautifulSoup(src, 'lxml')
    illness += soup.find_all("td", {"class": "views-field views-field-field-elhunytak-alapbetegsegek"})
illnesses_string = str(illness)
illnesses_splitted = illnesses_string.split("<")
del illnesses_splitted[::2]
illnesses_splitted_short = [i.replace('td class="views-field views-field-field-elhunytak-alapbetegsegek">','') for i in illnesses_splitted]
illnesses_splitted_final= [s.replace(':', '') for s in illnesses_splitted_short]
illnesstable = pd.DataFrame(illnesses_splitted_final)
illnesstable[0] = illnesstable[0].astype(str)

#creating the concatenated big DF 
bigdf = pd.concat([agetable, gendertable, illnesstable], axis=1, sort=False)
bigdf.columns = ['Age', 'Sex', 'Illness']

#splitting the illnesses column for further EDA  
new = bigdf["Illness"].str.split(",", n = 6, expand = True) 

#removing spaces
bigdf['Sex']=bigdf['Sex'].str.replace(' ','')

#removing spaces from Illlnesses, formatting
for i in range (0,6):
    new[i] = new[i].str.strip()
new.rename(columns={0: "Illness1", 1:"Illness2", 2:"Illness3",3:"Illness4",4:"Illness5",5:"Illness6",6:"Illness7"} ,inplace = True)

#merging dfs
merged = pd.concat([bigdf,new], axis=1, sort=False)
merged.drop(['Illness'], axis = 1, inplace = True)

#calculating the nr. illnesses by removing the nulls 
nulls = merged.isnull().sum(axis=1)
merged['Illnessnumber']= 7 - nulls

#genedrsplit
mergedmale = merged[merged['Sex'].str.contains("Férfi")]
mergedfemale = merged[merged['Sex'].str.contains("Nő")]

##EDA

#searching the most common illnesses (male)
illzmale = mergedmale.iloc[:,2:9].copy()
illzmalevert=illzmale['Illness1'].append(illzmale['Illness2']).reset_index(drop=True)
illzmalevert=illzmalevert.append(illzmale['Illness3']).reset_index(drop=True)
illzmalevert=illzmalevert.append(illzmale['Illness4']).reset_index(drop=True)
illzmalevert=illzmalevert.append(illzmale['Illness5']).reset_index(drop=True)
illzmalevert=illzmalevert.append(illzmale['Illness6']).reset_index(drop=True)
illzmalevert=illzmalevert.append(illzmale['Illness6']).reset_index(drop=True)
illzmalevert.dropna(inplace=True)

#searching the most common illnesses (female)
illzfemale = mergedfemale.iloc[:,2:9].copy()
illzfemalevert=illzfemale['Illness1'].append(illzfemale['Illness2']).reset_index(drop=True)
illzfemalevert=illzfemalevert.append(illzfemale['Illness3']).reset_index(drop=True)
illzfemalevert=illzfemalevert.append(illzfemale['Illness4']).reset_index(drop=True)
illzfemalevert=illzfemalevert.append(illzfemale['Illness5']).reset_index(drop=True)
illzfemalevert=illzfemalevert.append(illzfemale['Illness6']).reset_index(drop=True)
illzfemalevert=illzfemalevert.append(illzfemale['Illness6']).reset_index(drop=True)
illzfemalevert.dropna(inplace=True)

#searching the most common illnesses (total) 
illz = merged.iloc[:,2:9].copy()
illzvert=illz['Illness1'].append(illz['Illness2']).reset_index(drop=True)
illzvert=illzvert.append(illz['Illness3']).reset_index(drop=True)
illzvert=illzvert.append(illz['Illness4']).reset_index(drop=True)
illzvert=illzvert.append(illz['Illness5']).reset_index(drop=True)
illzvert=illzvert.append(illz['Illness6']).reset_index(drop=True)
illzvert=illzvert.append(illz['Illness6']).reset_index(drop=True)

illzvert.dropna(inplace=True)

#top10 illness
top10illz=illzvert.value_counts()[:10].index.tolist()
top10illz=pd.DataFrame(top10illz)

#most common illness
topill=illzvert.value_counts()[:1].index.tolist()

#list os all unique illness
Illzunique=illzvert.unique().tolist()
Illzunique=pd.DataFrame(Illzunique)

#creating new df from the parameters which are calculated 
calculated = pd.DataFrame(columns = ['Date','Total Deaths', 'New Deaths', 'Mean_Age/Total','Mean_Age/Today','Men%', 'Average Number of Illnesses', 'Most Common Illness']) 
calculated.Date = pd.Series(dt.datetime.now())
calculated['Mean_Age/Total'] = merged["Age"].mean()
calculated['Total Deaths'] = merged["Age"].count()
calculated['Most Common Illness']=illzvert.value_counts()[:1].index.tolist()
#share of men in total
a=merged['Sex'].str.count('Férfi').sum()
calculated['Men%'] = a/calculated['Total Deaths']

#avg nr of illnesses
calculated['Average Number of Illnesses'] = merged["Illnessnumber"].mean()
nulls = merged.isnull().sum(axis=1).tolist()

#index adjustment
merged.index = merged.index + 1
calculated.index = calculated.index+1 

#excel -export - rewriting tables
with pd.ExcelWriter('covid_death_total.xlsx') as writer:
    merged.to_excel(writer,sheet_name = 'base')
    illzvert.to_excel(writer, sheet_name = 'illztotal')
    top10illz.to_excel(writer, sheet_name = 'top10illz')
    Illzunique.to_excel(writer, sheet_name = 'illzunique')
    illzmalevert.to_excel(writer, sheet_name = 'illzmale')
    illzfemalevert.to_excel(writer, sheet_name = 'illzfemale')

#excel -export -- appending tables
xls.append_df_to_excel('covid_death_calcs.xlsx', calculated, sheet_name='calcs', startrow = None, header = False)

