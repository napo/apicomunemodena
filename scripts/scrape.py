# -*- coding: utf-8 -*-
"""eventi_modena.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1xbzQ-X6k-mPAOtBQxaYtwGFCUsaywt5m
"""

import warnings
import pandas as pd
import requests
import geopandas as gpd
from datetime import date
from zipfile import ZipFile
import os
warnings.filterwarnings("ignore")

intestazione = {'Accept': 'application/json'}
url_api = "https://www.comune.modena.it/api/"
url_search = url_api + "@querystring-search"

oggi = date.today()
oggi = oggi.strftime("%Y-%m-%d")
oggi += " 00:00"

parametri = {
    "b_size": 100000,
	"fullobjects": 1,
	"query": [{
		"i": "portal_type",
		"o": "plone.app.querystring.operation.selection.any",
		"v": ["Event"]
	}, {
		"i": "start",
		"o": "plone.app.querystring.operation.date.largerThan",
		"v": oggi
	}]
}

richiesta = requests.post(url_search, headers=intestazione,json=parametri)

richiesta.encoding = 'utf-8'
dati = richiesta.json()

eventi = pd.DataFrame(dati['items'])

filter=['@id','categoria_evento','city','street','created',
'description','effective','email','start','end','geolocation','image','image_caption','modified','nome_sede',
'orari','patrocinato_da','prezzo','reperibilita','telefono','title',
'ulteriori_informazioni','web','whole_day','zip_code']

eventi = eventi[filter]
eventi['pagina_web'] = eventi['@id'].apply(lambda x: x.replace('/api', ""))
del eventi['@id']
eventi['cap'] = eventi.zip_code.apply(lambda x: 41123 if(x == None) else x)
del eventi['cap']

eventi = eventi.rename(columns={'title': 'nome', "street": "via",
                       "zip_code": "cap", "modified": "data_ultima_modifica"})
eventi = eventi.rename(columns={'city': 'città', "street": "via", "description": "descrizione",
                       "created": "data_creazione", "end": "fine", "start": "inizio"})
eventi = eventi.rename(
    columns={'image': 'immagine', 'whole_day': 'giornata_intera'})
eventi = eventi.rename(columns={'ulteriori_informazioni': 'extrainfo'})
#events=events.rename(columns={'organizzato_da_esterno':'org_esterna'})
#events=events.rename(columns={"descrizione_estesa":"desc_estesa"})

eventi['latitudine'] = eventi.geolocation.apply(
    lambda x:  x['latitude'] if(x != None) else x)
eventi['longitudine'] = eventi.geolocation.apply(
    lambda x:  x['longitude'] if(x != None) else x)
eventi['longitudine'] = eventi.longitudine.apply(
    lambda x: 10.92572 if(x == None) else x)
eventi['latitudine'] = eventi.latitudine.apply(
    lambda x: 44.64582 if(x == None) else x)
eventi['longitudine'] = eventi.longitudine.apply(
    lambda x: 10.92572 if(x == 0) else x)
eventi['latitudine'] = eventi.latitudine.apply(
    lambda x: 44.64582 if(x == 0) else x)
eventi['longitudine'] = eventi.longitudine.apply(
    lambda x: 10.92572 if(pd.isna(x)) else x)
eventi['latitudine'] = eventi.latitudine.apply(
    lambda x: 44.64582 if(pd.isna(x)) else x)
del eventi['geolocation']

def categoriaEvento(e):
    categoria = ""
    for c in e:
        categoria = categoria + "," + c
    categoria = categoria.lstrip(",")
    return categoria


eventi['categoria_evento'] = eventi['categoria_evento'].apply(
    lambda x: categoriaEvento(x))

def desc(value):
    desc = ""
    try:
        for i in range(len(value['blocks'])):
            for k in list(value['blocks'].keys()):
                bk = value['blocks'][k]
                for b in bk['text']['blocks']:
                    desc = desc + " " + b['text']
    except KeyError:
        pass
    desc = desc.replace(";", " ")
    return desc

eventi['extrainfo'] = eventi['extrainfo'].apply(lambda x: desc(x))
eventi['immagine'] = eventi['immagine'].apply(lambda x: x['download'])
eventi.rename(columns={'image_caption': 'desc_img'}, inplace=True)
eventi.rename(columns={'effective': 'data_pubblicazione'}, inplace=True)
eventi['prezzo'] = eventi['prezzo'].apply(lambda x: desc(x))
eventi['orari'] = eventi['orari'].apply(lambda x: desc(x))

eventi['cap'] = eventi.cap.apply(lambda x: 41123 if(x == None) else x)

eventi.web = eventi.web.apply(lambda x: "" if (str(x) == "[]") else x)
eventi.web = eventi.web.apply(lambda x: "" if (x == None) else x)

eventi['città'] = eventi['città'].apply(lambda x: "Modena" if(x == None) else x)

eventi.replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"], value=["",""], regex=True, inplace=True)

eventi.to_csv("docs/eventi/eventi_modena.csv",sep=";",index=False)

eventi.to_csv("docs/eventi/eventi_modena.tsv",sep="\t",index=False,line_terminator="\r\n")

geo_events = gpd.GeoDataFrame(
    eventi, geometry=gpd.points_from_xy(eventi['longitudine'], eventi['latitudine']))

geo_events.set_crs(4326, inplace=True)
os.chdir("docs/eventi")
geo_events.to_file("eventi_modena.shp", encoding='utf-8')
zipObj = ZipFile('eventi_modena.zip', 'w')
zipObj.write('eventi_modena.shp')
zipObj.write('eventi_modena.shx')
zipObj.write('eventi_modena.prj')
zipObj.write('eventi_modena.dbf')
zipObj.close()

eventi.longitudine = eventi.longitudine.apply(lambda x: str(x).replace(".",","))
eventi.latitudine = eventi.latitudine.apply(lambda x: str(x).replace(".",","))

eventi.to_csv("eventi_modena_coordinate_con_virgola.csv",sep=";",index=False)

eventi.to_excel("eventi_modena.xlsx",index=False, sheet_name="eventi")