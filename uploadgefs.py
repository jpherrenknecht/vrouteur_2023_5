# coding: utf-8

#le debut de chargement des gribs intervient en heure UTC à
# 9h30(gfs06) - 15h30(gfs12) -  21h30(gfs18) - 03h30 (gfs00)
# en heure d'hiver
# 10h30(gfs06) - 16h30(gfs12) -  22h30(gfs18) - 04h30 (gfs00)

# les gribs complets sont disponibles en heure UTC à
# 11h(gfs06) - 17(gfs12) -  23(gfs18) - 05 h (gfs00)

# les gribs complets sont disponibles en heure d'hiver à
# 12h(gfs06) - 18h(gfs12) -  00(gfs18) - 06 h (gfs00)
# les gribs complets sont disponibles en heure d'ete à
# 13h(gfs06) - 19(gfs12) -  01(gfs18) - 07 h (gfs00)


import os
import sys
import time
import math

import numpy as np
import pandas as pd
import xarray as xr
from datetime import datetime
from urllib.request import urlretrieve
from urllib.error import HTTPError
from pathlib import Path
from fonctions2023   import *
from fonctions2023_2 import *
PI=math.pi
tic=time.time()
tic_formate=time.strftime(" %d %b %Y %H:%M:%S ", time.localtime(tic))
ticstruct = time.localtime()
utc = time.gmtime()
t0=time.time()
decalage = ticstruct[3] - utc[3]
leftlon, rightlon, toplat, bottomlat = 0, 360, 90, -90
basedir=os.path.dirname(os.path.abspath("__file__")) 
tic=time.time()
ticstruct = time.localtime()
utc = time.gmtime()
decalage = ticstruct[3] - utc[3]
leftlon, rightlon, toplat, bottomlat = 0, 360, 90, -90
mn_jour_utc =time.gmtime()[3]*60+time.gmtime()[4]
print()
print('mn_jour_utc',mn_jour_utc)
# Fichiers a recuperer en fonction de l'heure 
print()



# gestion des repertoires
basedir = os.path.abspath(os.path.dirname(__file__))

if basedir=='/home/jp':  
    #basedir='/home/jp/vrouteur'                                    # cas ou le programme est declenche a partir d'une tache cron 
    filename=basedir+"/gribsgefs/derniergrib.npy"
    if os.path.exists(filename)==False:                            # on teste si on est dans vrouteur sinon on est dans notebooks
        basedir='/home/jp/vrouteur_2023_5'
        filename='/home/jp/gribs/gribsgefs/derniergrib.npy'

else:
    basedir='/home/jp/gribs'


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







def file_names_gefs():
    temps_secondes=time.time()
    # date=time.strftime("%Y%m%d", time.gmtime())
    dateveille=time.strftime("%Y%m%d", time.gmtime(time.time()-86400))
    dateveille_tuple = time.gmtime(temps_secondes-86400) 
    mn_jour_utc =time.gmtime()[3]*60+time.gmtime()[4]
    date_formatcourt = time.strftime("%Y%m%d", time.gmtime())
    if (mn_jour_utc <340):     #5h 40 UTC
        filenameGefs=basedir+"/gribsgefs/gefs_"+dateveille+"-18.npy"
        tigGefs=time.mktime(datetime(dateveille_tuple[0],dateveille_tuple[1],dateveille_tuple[2],18,0,0).timetuple())+decalage*3600
    elif (mn_jour_utc<700):   # Avant 11h40 c'est le 00 qu'il faut charger 
        filenameGefs=basedir+"/gribsgefs/gefs_"+date_formatcourt+"-00.npy"
        tigGefs=time.mktime(datetime(date_tuple[0],date_tuple[1],date_tuple[2],0,0,0).timetuple())+decalage*3600
    elif (mn_jour_utc<1060):  #17h 40 UTC
        filenameGefs=basedir+"/gribsgefs/gefs_"+date_formatcourt+"-06.npy"
        tigGefs=time.mktime(datetime(date_tuple[0],date_tuple[1],date_tuple[2],6,0,0).timetuple())+decalage*3600
    elif (mn_jour_utc<1420):  #23h 40 
        filenameGefs=basedir+"/gribsgefs/gefs_"+date_formatcourt+"-12.npy"
        tigGefs=time.mktime(datetime(date_tuple[0],date_tuple[1],date_tuple[2],12,0,0).timetuple())+decalage*3600
    else:    
        filenameGefs=basedir+"/gribsgefs/gefs_"+date_formatcourt+"-18.npy"
        tigGefs=time.mktime(datetime(date_tuple[0],date_tuple[1],date_tuple[2],18,0,0).timetuple())+decalage*3600
    return filenameGefs,tigGefs

filenameGefs,tigGefs=file_names_gefs()
date  = time.strftime("%Y%m%d", time.gmtime(tigGefs))       # date du grib a charger
heure = time.strftime("%H", time.gmtime(tigGefs))           # heure du grib a charger

iprev = []                 
for a in range(0, 387, 3):                              # Construit le tuple des indexs des fichiers maxi 387
    iprev += (str(int(a / 100)) + str(int((a % 100) / 10)) + str(a % 10),)


# chargement du gefs 0.5     : #filter_gensbc.pl?
# exemple
# URL='https://nomads.ncep.noaa.gov/cgi-bin/filter_gensbc_ndgd.pl?file=gefs.t00z.ge10pt.f003.conus_ext_2p5.grib2&leftlon=0&rightlon=360&toplat=90&bottomlat=-90&dir=%2Fgefs.20221119%2F00%2Fndgd_gb2'

GR = np.zeros((len(iprev), 361, 720), dtype=complex)    # initialise le np array de complexes qui recoit les donnees  

for indexprev in range(len(iprev)):  # recuperation des fichiers de 0 a 384 h
    prev = iprev[indexprev]
    nom_fichier = "gefs_" + date + "_" + heure + "_" + prev   # nom sous lequel le  fichier est sauvegarde provisoirement
    url='https://nomads.ncep.noaa.gov/cgi-bin/filter_gensbc.pl?file=gec00.t'+heure+'z.pgrb2a.0p50_bcf'+\
            prev+'&lev_10_m_above_ground=on&var_UGRD=on&var_VGRD=on&leftlon=0&rightlon=360&toplat=90&bottomlat=-90&dir=%2Fgefs.'+date+'%2F'+heure+'%2Fpgrb2ap5_bc'
   
    try:
        urlretrieve(url, nom_fichier)
        ds = xr.open_dataset(nom_fichier, engine='cfgrib')
        time1=ds.coords["time"].data
        # print(ds.variables['u10'].data)
        GR[indexprev] = ds.variables['u10'].data + ds.variables['v10'].data * 1j
        os.remove(nom_fichier)                  # On efface le fichier pour ne pas encombrer
        print(' {} chargé '.format(nom_fichier))
        residuel=nom_fichier + '.923a8.idx'
        if os.path.exists(residuel) == True: 
            os.remove(residuel)   # On efface le fichier residuel
        indice=indexprev*3    


    except:
        try:
            # on charge l indice suivant
            prev = iprev[indexprev+1]
            nom_fichier = "gefs_" + date + "_" + heure + "_" + prev   # nom sous lequel le  fichier est sauvegarde provisoirement
            # print('prevision chargée apres l echec',prev)
            url='https://nomads.ncep.noaa.gov/cgi-bin/filter_gensbc.pl?file=gec00.t'+heure+'z.pgrb2a.0p50_bcf'+\
            prev+'&lev_10_m_above_ground=on&var_UGRD=on&var_VGRD=on&leftlon=0&rightlon=360&toplat=90&bottomlat=-90&dir=%2Fgefs.'+date+'%2F'+heure+'%2Fpgrb2ap5_bc'
            urlretrieve(url, nom_fichier)
            ds = xr.open_dataset(nom_fichier, engine='cfgrib')
            GR[indexprev+1] = ds.variables['u10'].data + ds.variables['v10'].data * 1j
            os.remove(nom_fichier)                  # On efface le fichier pour ne pas encombrer
            # print(' {} chargé '.format(nom_fichier))
            residuel=nom_fichier + '.923a8.idx'
            if os.path.exists(residuel) == True: 
                os.remove(residuel)   # On efface le fichier residuel
            GR[indexprev]=(GR[indexprev-1]+GR[indexprev+1])/2
            print (' indice interpole',(indexprev) *3)

        except:
            pass


sauvegardeGrib(filenameGefs,GR,tigGefs,384,tigGefs+13200)   # on sauvegarde sous forme d'un fichier npy et json 
filename2=basedir+"/gribsgefs/derniergrib.npy"
sauvegardeGrib(filename2,GR,tigGefs,384,tigGefs+13200)  

# on sauvegarde en hdf5

# print('\ntigGefs suivant fichier data ',time.strftime("%Y%m%d %H:%M:%S", time.gmtime(tigGefs )))
# print(indice)
# f1 = h5py.File(basedir+'/gribsgefs/'+nom_fichier, "w")
# dset1 = f1.create_dataset("dataset_01", GR.shape, dtype='complex', data=GR)
# dset1.attrs['time_grib'] = tigGefs      # transmet le temps initial du grib en temps local en s pour pouvoir faire les comparaisons
# dset1.attrs['indices'] = indice 
# f1.close()



# # sauvegarde sous le nom de dernier grib
# f1 = h5py.File(basedir+'/gribsgefs/derniergrib.hdf5', "w")
# dset1 = f1.create_dataset("dataset_01", GR.shape, dtype='complex', data=GR)
# dset1.attrs['time_grib'] = tigGefs      # transmet le temps initial du grib en temps local en s pour pouvoir faire les comparaisons
# dset1.attrs['nom']='gribsgefs/derniergrib.hdf5'
# dset1.attrs['indices'] = indice 
# f1.close()

