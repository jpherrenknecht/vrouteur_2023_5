import os
import shutil
import stat
import time
import math
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlretrieve
import cfgrib
import json
import numpy as np
import requests
import xarray as xr


basedir = os.path.abspath(os.path.dirname(__file__))
rootdir='/home/jp/gribs'
basedir=rootdir
print(basedir)



def previsiontab(tig, GR, tp, lat, lon):
    '''En entree tp lat et lon sont des np.arrays de memes dimensions '''
    '''Pour chaque point on a le temps la latitude et la longitude'''
    '''en sortie la vitesse t l angle du vent'''
    if not isinstance(lat,np.ndarray):           #permet de traiter le cas de valeurs simples 
        lat=np.array([lat])
        lon=np.array([lon]) 
    else:
        lat=lat.ravel()
        lon=lon.ravel()
    if isinstance(tp,float):                     # permet de traiter le cas une seule valeur de temps pour differents points 
        tp=np.ones(len(lat))*tp   
        
    lat=90-lat
    lon=lon%360
    dx=lon%1
    dy=lat%1
    lati=lat.astype(int)
    loni=lon.astype(int)
    itemp=(tp-tig)/3600/3
    iitemp=itemp.astype(int)
    iitemp[iitemp>127]=127
    ditemp=itemp%1    
    #fraction=(ditemp*18).astype(int)/18
    fraction=itemp 
    UV000=np.round(GR[iitemp,lati,loni],3)
    UV010=np.round(GR[iitemp,lati+1,loni],3)
    UV001=np.round(GR[iitemp,lati,(loni+1)%360],3)
    UV011=np.round(GR[iitemp,lati+1,(loni+1)%360],3)
    UV100=np.round(GR[iitemp+1,lati,loni],3)
    UV110=np.round(GR[iitemp+1,lati+1,loni],3)
    UV101=np.round(GR[iitemp+1,lati,(loni+1)%360],3)
    UV111=np.round(GR[iitemp+1,lati+1,(loni+1)%360],3)

    UVX00=UV000+fraction*(UV100-UV000)     # on interpole sur le temps
    UVX10=UV010+fraction*(UV110-UV010)
    UVX01=UV001+fraction*(UV101-UV001)
    UVX11=UV011+fraction*(UV111-UV011)
    res=UVX00+(UVX01-UVX00)*dx +(UVX10-UVX00)*dy  +(UVX11+UVX00-UVX10-UVX01)*dx*dy   #interpolation bilineaire
    vitesses=np.abs(res)* 1.94384 
    vitesses[vitesses>70] = 70 
    vitesses[vitesses<1]  = 1
    angles = (270 - np.angle(res, deg=True)) % 360
    if(vitesses.shape[0])==1:                          # permet d avoir un retour en float pour une demande simple
        vitesses=vitesses[0,0]
        angles=angles[0,0]
        
    return vitesses,angles










print('test')
tic=time.time()
ticstruct = time.localtime()
utc = time.gmtime()
decalage = ticstruct[3] - utc[3]




def sauvegardeGrib(filename,GR,tig,indices,avail_ts):
    '''genere un fichier npy  pour le gr et un fichier json pour le tig et l'indice'''
    filenamejson=filename.split('.')[0]+'.json'
    with open(filename,'wb')as f:       
        np.save (f,GR)
    # on sauve les attributs sous le meme nom dans un fichierjson
    dicogrib={'tig':tig,'indices':indices, 'avail_ts':avail_ts}
    with open(filenamejson, 'w') as fp:
        json.dump(dicogrib, fp)
    return None        


def recupereGrib (filename):
    filenamejson=filename.split('.')[0]+'.json'
    with open(filename, 'rb') as f:
        GR025 = np.load(f)

    with open(filenamejson, 'r') as fp:
        data = json.load(fp)
    tig=data['tig']
    indices=data['indices']
    avail_ts=data['avail_ts']
    return GR025,tig,indices,avail_ts       




def fileNames():
    ''' cherche le dernier grib complet disponible au temps en secondes '''
    ''' temps_secondes est par defaut le temps instantané '''
    ''' Cherche egalement le dernier grib chargeable partiellement'''
    temps_secondes=time.time()
    date_tuple       = time.gmtime(temps_secondes) 
    date_formatcourt = time.strftime("%Y%m%d", time.gmtime(temps_secondes))
    dateveille_tuple = time.gmtime(temps_secondes-86400) 
    dateveille_formatcourt=time.strftime("%Y%m%d", time.gmtime(temps_secondes-86400))
    mn_jour_utc =date_tuple[3]*60+date_tuple[4]
  

    if (mn_jour_utc <340):
        filename384=basedir+"/gribs025/gfs_"+dateveille_formatcourt+"-18.npy"
        tig384=time.mktime(datetime(dateveille_tuple[0],dateveille_tuple[1],dateveille_tuple[2],18,0,0).timetuple())+decalage*3600
    elif (mn_jour_utc<700):   
        filename384=basedir+"/gribs025/gfs_"+date_formatcourt+"-00.npy"
        tig384=time.mktime(datetime(date_tuple[0],date_tuple[1],date_tuple[2],0,0,0).timetuple())+decalage*3600
    elif (mn_jour_utc<1060): 
        filename384=basedir+"/gribs025/gfs_"+date_formatcourt+"-06.npy"
        tig384=time.mktime(datetime(date_tuple[0],date_tuple[1],date_tuple[2],6,0,0).timetuple())+decalage*3600
    elif (mn_jour_utc<1420):   
        filename384=basedir+"/gribs025/gfs_"+date_formatcourt+"-12.npy"
        tig384=time.mktime(datetime(date_tuple[0],date_tuple[1],date_tuple[2],12,0,0).timetuple())+decalage*3600
    else:    
        filename384=basedir+"/gribs025/gfs_"+date_formatcourt+"-18.npy"
        tig384=time.mktime(datetime(date_tuple[0],date_tuple[1],date_tuple[2],18,0,0).timetuple())+decalage*3600

    # nom du fichier suivant le 384
    date     = time.strftime("%Y%m%d", time.gmtime(tig384 +21600))
    heure    = time.strftime("%H", time.gmtime(tig384+21600))
    filename = basedir+"/gribs025/gfs_"+date+"-"+heure+".npy"
    tig =tig384+21600

    # on considere que l'on ne peut commencer a charger le fichier suivant que 9h40 apres le tig du precedent  
    # Exemle grib 06 UTC disponible à 9h40 UTC grib 12 disponible a 15 h40
    if temps_secondes-tig384> 34500 :             
        print ('Fichier partiel  {} '.format(filename))
        status='chargeable'
    else: 
        status='nonchargeable'

    # renvoie le nom du fichier complet384 disponible et son tig384, 
    # le nom du fichier suivant et son tig et son statut 'chargeable' ou 'nonchargeable'  
    # print ('tig384  dans filenames',time.strftime(" %d %b %Y %H: %M: %S ", time.localtime(tig384)))
    return filename384,tig384,filename,tig,status  


# on charge le nom du grib disponible

filename384,tig384,filename,tig,status  =fileNames()



print ('Fichier' , filename)


GR025,tig,indices,avail_ts  =recupereGrib (filename384)
print('tig',tig)


# print(GR[0,0,0])
# print(GR[1,1,1])
# print(GR[1,10,10])

#GR = np.zeros((len(iprev), 721, 1440), dtype=complex)

#on va faire une prevision en 0.25
# recherche des indices
tic =time.time()
lat=49
lon=-3
tp=tig+3600*3
tp=tic

print('***************************************************************************************************************')
print ('tig  {}'.format(time.strftime(" %d %b %Y %H:%M:%S ", time.gmtime(tig))) )
print ('tp   {}'.format(time.strftime(" %d %b %Y %H:%M:%S ", time.gmtime(tp))) )
print('***************************************************************************************************************')










def previsiontab025(tig, GR025, tp, lat, lon):
    # le cas plusieurs temps differents n'est pas traite 
    if not isinstance(lat,np.ndarray):           #permet de traiter le cas de valeurs simples 
        lat=np.array([lat])
        lon=np.array([lon]) 
    else:
        lat=lat.ravel()
        lon=lon.ravel()
    if (tp-tig) <120*3600:
        itemp=(tp-tig)/3600
        print('(tp-tig)/3600 ',(tp-tig)/3600)
        print('on est dans le cas indice inferieur a 120')
       
      
    else:
        itemp=(((tp-tig)-(120*3600))/3600/3)+120
    iitemp=int(itemp)
    iitemp=np.ones(len(lat))*iitemp          # permet de traiter le cas une seule valeur de temps pour differents points # le cas plusieurs temps differents n'est pas traite    
    iitemp[iitemp>207]=207                      # si le temps est superieur a tig +384h on ramene a 381h (indice 207) pour pouvoir interpoler entre 207 et 208
    ditemp=itemp%1   
    
    lat=(90-lat)*4
    lon=(lon%360)*4
    lati  =lat.astype(int)
    loni  =lon.astype(int)
    iitemp=iitemp.astype(int)
    dx=lon%1
    dy=lat%1
    fraction=ditemp 
    # print()
    # print('lat    ',lat   )
    # print('lon    ',lon   )
    # print('tp     ',tp    )
    # print()
    # print('iitemp ',iitemp )
    # print('lati   ',lati  )
    # print('loni   ',loni  )
    # print('itemp  ',itemp )
    # print ('fraction',fraction)
    
    # print('ditemp ',ditemp )
    # print('dx     ',dx    )
    # print('dy     ',dy    )
    # print(' indices ',iitemp,lati,loni)
    # print ('itemp',itemp)

    
    UV000=np.round(GR025[iitemp,lati,loni],3)
    UV010=np.round(GR025[iitemp,(lati+1)%720,loni],3)
    UV001=np.round(GR025[iitemp,lati,(loni+1)%1440],3)
    UV011=np.round(GR025[iitemp,(lati+1)%720,(loni+1)%1440],3)

    UV100=np.round(GR025[iitemp+1,lati,loni],3)
    UV110=np.round(GR025[iitemp+1,(lati+1)%720,loni],3)
    UV101=np.round(GR025[iitemp+1,lati,(loni+1)%1440],3)
    UV111=np.round(GR025[iitemp+1,(lati+1)%720,(loni+1)%1440],3)

    UVX00=UV000+fraction*(UV100-UV000)     # on interpole sur le temps
    UVX10=UV010+fraction*(UV110-UV010)
    UVX01=UV001+fraction*(UV101-UV001)
    UVX11=UV011+fraction*(UV111-UV011)
    res=UVX00+(UVX01-UVX00)*dx +(UVX10-UVX00)*dy  +(UVX11+UVX00-UVX10-UVX01)*dx*dy   #interpolation bilineaire
    vitesses=np.abs(res)* 1.94384
    vitesses[vitesses>70] = 70 
    vitesses[vitesses<1]  = 1
    angles = (270 - np.angle(res, deg=True)) % 360
    return vitesses, angles    

#****************************************************************************************************************************

print("Test indice 208,10,10,               de GR025",GR025[0,0,0])
print("Test indice 9,160,720,               de GR025",GR025[9,160,720])
print('Test indice 208,720,1439,(derniers) de GR025 ',GR025 [208,720,1439])
print('tig {}  en UTC {}'.format(tig,time.strftime(" %d %b %Y %H:%M:%S ", time.gmtime(tig))))




# test avec 2 points et un temps 
lat=np.array([49,47.333])
lon=np.array([-3,-5.6666])
tp=tig+3600*6


vitesses, angles=previsiontab025(tig, GR025, tp, lat, lon)
print('\nresultat fonction pour tp= tig+ {}h'.format((tp-tig)/3600))
print('angles  ',angles)
print('vitesses',vitesses)



