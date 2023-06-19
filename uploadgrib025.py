
import json
import math
import os
import shutil
import stat
import subprocess
import time
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlretrieve

import cfgrib
import numpy as np
import requests
import xarray as xr
basedir = os.path.abspath(os.path.dirname(__file__))
print ('basedir ',basedir)
rootdir='/home/jp/gribs'
basedir=rootdir
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
        GR = np.load(f)
    with open(filenamejson, 'r') as fp:
        data = json.load(fp)
    tig=data['tig']
    indices=data['indices']
    avail_ts=data['avail_ts']
    return GR,tig,indices,avail_ts       


def nettoyage():
    '''efface les fichiers plusvieux que le delta de temps '''
    delta=3600*24
    dir=basedir+'/gribs025'   #repertoire des gribs
    for fichier in os.listdir(dir):
        mtime=os.path.getmtime(dir+'/'+fichier)
        #print(fichier,time.time()- mtime)
        # print(mtime)
        #print(time.time()-mtime)
        if time.time()-mtime >delta :
            os.unlink(dir+'/'+fichier)
    print('Effacement des fichiers de plus de 24h')        
    return None 

def fileNames():
    ''' cherche le dernier grib complet disponible au temps en secondes '''
    ''' temps_secondes est par defaut le temps instantané '''
    ''' Cherche egalement le dernier grib chargeable partiellement'''
    temps_secondes   = time.time()
    date_tuple       = time.gmtime(temps_secondes) 
    date_formatcourt = time.strftime("%Y%m%d", time.gmtime(temps_secondes))
    dateveille_tuple = time.gmtime(temps_secondes-86400) 
    dateveille_formatcourt=time.strftime("%Y%m%d", time.gmtime(temps_secondes-86400))
    mn_jour_utc =date_tuple[3]*60+date_tuple[4]

    if (mn_jour_utc <340):                   #correspond a l'heure ou le chargement est complet 5h 10 +20mn securite =5h30 soit 340mn
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
    tig      = tig384+21600

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

filename384,tig384,filename,tig,status  =fileNames()

# print('dernier fichier complet {}'.format(filename384))
# print('tig384',tig384)
# print('***************************************************************************************************************')
# print ('tig  {} soit {} '.format(tig,time.strftime(" %d %b %Y %H:%M:%S ", time.localtime(tig))) )
# print('***************************************************************************************************************')


date     = time.strftime("%Y%m%d", time.gmtime(tig384))
heure    = time.strftime("%H"    , time.gmtime(tig384))





iprev = []                 
for a in range(0, 120, 1):                              # Construit le tuple des indexs des fichiers maxi 387
    iprev += (str(int(a / 100)) + str(int((a % 100) / 10)) + str(a % 10),)
for a in range(120, 387, 3):                              # Construit le tuple des indexs des fichiers maxi 387
    iprev += (str(int(a / 100)) + str(int((a % 100) / 10)) + str(a % 10),)

#print ('size',len(iprev))
# leftlon=0
# rightlon=360
# toplat=90
# bottomlat=-90

GR025 = np.zeros((len(iprev), 721, 1440), dtype=complex)    # initialise le np array de complexes qui recoit les donnees  
for indexprev in range(len(iprev)):  # recuperation des fichiers de 0 a 384 h
#for indexprev in range(3):  # recuperation des fichiers de 0 a 384 h
    prev = iprev[indexprev]

    url="https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl?dir=%2Fgfs."+date+"%2F"+heure+"%2Fatmos&file=gfs.t"+heure+"z.pgrb2.0p25.f"+prev+"&var_UGRD=on&var_VGRD=on&lev_10_m_above_ground=on"
    nom_fichier_local = "grib_" + date + "_" + heure + "_" + prev   # nom sous lequel le  fichier est sauvegarde provisoirement
    urlretrieve(url, nom_fichier_local)   
    print('indexprev {} fichier chargé prev {}'.format(indexprev,nom_fichier_local))
    nom_fichier_local7b = "grib7b_" + date + "_" + heure + "_" + prev   # nom sous lequel le  fichier est sauvegarde provisoirement
    commande = ["/home/jp/wgrib2/grib2/wgrib2/wgrib2" , nom_fichier_local, "-set_grib_max_bits", "7" , "-set_grib_type" ,"jpeg", "-grib_out" ,  nom_fichier_local7b]
    subprocess.run(commande)
    ds = xr.open_dataset(nom_fichier_local7b, engine='cfgrib')    # exploitation du fichier et mise en memoire dans GR
    GR025[indexprev] = ds.variables['u10'].data + ds.variables['v10'].data * 1j  
    tig=ds.variables['time'].item()*1e-9
    os.remove(nom_fichier_local)
    os.remove(nom_fichier_local7b) # On efface le fichier pour ne pas encombrer
                     
    # residuel=nom_fichier_local + '.923a8.idx'
    # if os.path.exists(residuel) == True: 
    #     os.remove(residuel)                       # On efface le fichier residuel
    residuel2=nom_fichier_local7b+ '.923a8.idx'
    if os.path.exists(residuel2) == True: 
        os.remove(residuel2)                       # On efface le fichier residuel

indice384=indexprev
sauvegardeGrib(filename384,GR025,tig384,indice384,tig384+13200)
nettoyage()


# Verifications   
print()
print()
print('Upload du      {} UTC'.format(time.strftime(" %d %b %Y %H:%M:%S ", time.gmtime(tic))))
print('date  du grib  {} et heure {}'.format(date,heure))
print('tig     en UTC {}'.format(time.strftime(" %d %b %Y %H:%M:%S ", time.gmtime(tig))))
print('tic -tig en heures {:6.2f}'.format((tic-tig)/3600))
print('Grib chargé    {}'.format(filename384))
print()
print("Test indice 208,10,10,               de GR025",GR025[0,0,0])
print("Test indice 9,160,720,               de GR025",GR025[9,160,720])
print("Test indice 208,720,1439,(derniers)  de GR025",GR025 [208,720,1439])

