import os
import time
import math

import numpy as np
import pandas as pd
import xarray as xr
import json
import folium
from scipy.interpolate import RegularGridInterpolator,interp2d,interpn
from datetime import datetime
from urllib.request import urlretrieve
from urllib.error import HTTPError
from pathlib import Path
from websocket import create_connection



#fonctions
#chaine_to_dec''' Transforme les chaines latitude et longitude en un tuple (y,x) '''
# chaine_to_dec_tab
# pos_dec_mn
# pos_dec_mn_string
# file_names
# file_names2
# chargement_384
# chargement_grib
# chargement_dernier():
# prevision(tig, GR, tp, latitude, longitude)
# previsionbis
# prevision2
# prevision3
# prevision5
# prevision_tableau
# prevision_tableau2
# meteo_tableau
# twa(cap, dvent):    '''retourne la valeur absolue de la twa'''
# def ftwao( HDG,TWD):    '''retourne un ndarray de twa orientees babord<0 tribord>0 à partir de ndarray HDG et TWD'''    
# def signetwa(HDG,TWD):   
# def fcap(twao,twd):
# def rangenavi(capa, capb):    ''' donne les caps entre les deux bornes en tenant compte du passage a 360'''  
# def range_cap(direction_objectif, direction_vent, a_vue_objectif, angle_pres, angle_var):
# def dist_cap(D,A):    ''' retourne la distance et l'angle du deplacement entre le depart et l'arrivee 
# def dist_cap_ortho(lati,lngi,latfi,lngfi):    '''donnees en coordonnees decimaux resultat en miles nautiques '''
# def dist_cap4(points,A):   ''' points est une  liste de points a 2 dimensions , a est un point complexe '''
# def depl(y0,x0, vit ,cap, dt ):    '''Deplacement depuis yo,xo avec vitesse cap et intervalle de temps '''
# def deplacement2(x0,y0,d_t,HDG,TWD,VT,A,twa,penalite):    ''' fonction donnant le tuple point d arrivée en fonction des coordonnées du point de depart ''' 
# def dist_cap4(points,A):    ''' points est une  liste de points a 2 dimensions , a est un point complexe '''''' on retourne un tableau des distances et des caps '''
# def depl(y0,x0, vit ,cap, dt ):    '''Deplacement depuis yo,xo avec vitesse cap et intervalle de temps '''
# def uv2ds(u,v): ''' angle defini par u v'''
# def deplacement2(x0,y0,d_t,HDG,TWD,VT,A,twa,penalite):    ''' fonction donnant le tuple point d arrivée en fonction des coordonnées du point de depart ''' 
# def to_pandas_csv(chemincomplet,nomcsv):   
# def opti(twa, tws,tab_twa , tab_tws  ,polaires): '''Optimise la twa lorsqu elle est autour des valeurs de vmgmax'''
# def opti2 ''' la meme ?
# def foil(ttwa,ttws,speedRatio,twaMin,twaMax,twaMerge,twsMin,twsMax,twsMerge):
# def recupere_polaires(bateau ,nom_fichier):   
# def ccw(A,B,C):'''la fonction renvoie true si rotation anti horaire '''
# def intersect (A,B,C,D):    ''' verifie si AB et CD se coupent  
    
    
    
PI=math.pi
tic=time.time()
ticstruct = time.localtime()
utc = time.gmtime()
decalage = ticstruct[3] - utc[3]
leftlon, rightlon, toplat, bottomlat = 0, 360, 90, -90
date_tuple       = time.gmtime(tic) 
workdir=os.getcwd()
#basedir = os.path.abspath(os.path.dirname(__file__))



# filename=basedir+"/gribsvr/derniergrib.hdf5"
#     if os.path.exists(filename)==True:


basedir=os.path.dirname(os.path.abspath("__file__"))
if basedir=='/home/jp':                                     # cas ou le programme est declenche a partir d'une tache cron 
    try :
        filename=basedir+"/gribsvr/derniergrib.hdf5"
        if os.path.exists(filename)==True:
            basedir='/home/jp/vrouteur'    
    except: 
        basedir='/home/jp/Documents/notebooks'       

                                     
    




#date  = time.strftime("%Y%m%d", time.gmtime(tig384 ))
#heure = time.strftime("%H", time.gmtime(tig384))
iprev = []                 
for a in range(0, 387, 3):                              # Construit le tuple des indexs des fichiers maxi 387
    iprev += (str(int(a / 100)) + str(int((a % 100) / 10)) + str(a % 10),)
#print ('Decalage horaire/ utc {} '.format(decalage))

ix = np.arange(129)  # temps
iy = np.arange(181)  # latitudes
iz = np.arange(361)  # longitudes
#print(tic)

def chaine_to_dec(latitude, longitude):
    ''' Transforme les chaines latitude et longitude en un tuple (y,x) '''
    ''' Les latitudes nord sont positives pour permettre de tracer directement dans folium '''
    degre = int(latitude[0:3])
    minutes = int(latitude[4:6])
    secondes = int(latitude[7:9])
    lat = degre + minutes / 60 + secondes / 3600
    if latitude[10] == 'S':
        lat = -lat
    degre = int(longitude[0:3])
    minutes = int(longitude[4:6])
    secondes = int(longitude[7:9])
    long = degre + minutes / 60 + secondes / 3600
    if longitude[10] == 'W':
        long = -long
    return (lat, long)        



def chaine_to_dec_tab(latitude, longitude):
    ''' Transforme les chaines latitude et longitude en un tuple (y,x) '''
    ''' Les latitudes nord sont positives pour permettre de tracer directement dans folium '''
    tab=[]
    degre = int(latitude[0:3])
    minutes = int(latitude[4:6])
    secondes = int(latitude[7:9])
    lat = degre + minutes / 60 + secondes / 3600
    if latitude[10] == 'S':
        lat = -lat
    tab.append(lat)    
    degre = int(longitude[0:3])
    minutes = int(longitude[4:6])
    secondes = int(longitude[7:9])
    long = degre + minutes / 60 + secondes / 3600
    if longitude[10] == 'W':
        long = -long
    tab.append(long)
    return tab     


def pos_dec_mn(lat,lng):
    ''' transforme les degres decimaux en mn sec '''
    
    abso1= abs(lat)
    degre1=math.floor(abso1)
    min1=math.floor((abso1-degre1)*60)
    sec1=round(((abso1-degre1)*60-min1)*60)
    if lat>0:
        H1='N'
    else:
        H1='S'
    abso2= abs(lng)
    degre2=math.floor(abso2)
    min2=math.floor((abso2-degre2)*60)
    sec2=round(((abso2-degre2)*60-min2)*60)
    if lng:
        H2='E'
    else:
        H2='W'
    print ('Lat {}-{}-{} {}       Lng {}-{}-{} {}\n'.format(degre1,min1,sec1,H1,degre2,min2,sec2,H2))
    
    return degre1,min1,sec1,H1,degre2,min2,sec2,H2
    
def pos_dec_mn_string(lat,lng):
    ''' transforme les degres decimaux en mn sec '''
    '''retourne une chaine'''
    
    abso1= abs(lat)
    degre1=math.floor(abso1)
    min1=math.floor((abso1-degre1)*60)
    sec1=round(((abso1-degre1)*60-min1)*60)
    if lat>0:
        H1='N'
    else:
        H1='S'
    abso2= abs(lng)
    degre2=math.floor(abso2)
    min2=math.floor((abso2-degre2)*60)
    sec2=round(((abso2-degre2)*60-min2)*60)
    if lng:
        H2='E'
    else:
        H2='W'
    print ('Lat {}-{}-{} {}       Lng {}-{}-{} {}\n'.format(degre1,min1,sec1,H1,degre2,min2,sec2,H2))
    latstring= str(degre1)+'-'+str(min1)+'-'+str(sec1)+H1
    lngstring = str(degre2)+'-'+str(min2)+'-'+str(sec2)+H2
    return latstring,lngstring



# def chargement_dernier():
#     basedir=os.path.dirname(os.path.abspath("__file__"))
#     if basedir=='/home/jp':  
#         basedir='/home/jp/vrouteur'                                    # cas ou le programme est declenche a partir d'une tache cron 
#         filename=basedir+"/gribs/derniergrib.hdf5"
#         if os.path.exists(filename)==False:
#             basedir='/home/jp/Documents/notebooks'
#             filename=basedir+"/gribs/derniergrib.hdf5"
           
#     else:     
#         filename=basedir+"/gribs/derniergrib.hdf5"

   
#     if os.path.exists(filename) == True:     # si le fichier existe on le charge direct
#         f2 = h5py.File(filename, 'r')
#         dset1 = f2['dataset_01']
#         GR = dset1[:]
#         tig = dset1.attrs['time_grib']
#         indice=dset1.attrs['dernier_a_jour']
#         nomfichier=dset1.attrs['nom']

#         f2.close() 
#     return    tig,GR,nomfichier,indice




# def chargement_dernier_vr():
#     basedir=os.path.dirname(os.path.abspath("__file__"))
#     if basedir=='/home/jp':  
#         basedir='/home/jp/vrouteur'                                    # cas ou le programme est declenche a partir d'une tache cron 
#         filename=basedir+"/gribsvr/derniergrib.hdf5"
#         if os.path.exists(filename)==False:
#             basedir='/home/jp/Documents/notebooks'
#             filename=basedir+"/gribsvr/derniergrib.hdf5"
           
#     else:     
#         filename=basedir+"/gribsvr/derniergrib.hdf5"
    

#     if os.path.exists(filename) == True:     # si le fichier existe on le charge direct
       
#         f1 = h5py.File(filename, 'r')
#         dset1 = f1['dataset_01']
#         GRVR = dset1[:]
#         tigvr = dset1.attrs['time_grib']
#         indices  = dset1.attrs['indices']   # Le grib est completement a jour  l'indice est enregistre dans le fichier filename
#         f1.close()
      
#     return    tigvr,GRVR,filename,indices


# def chargement_dernier_gefs():
#     basedir=os.path.dirname(os.path.abspath("__file__"))
#     if basedir=='/home/jp':  
#         basedir='/home/jp/vrouteur'                                    # cas ou le programme est declenche a partir d'une tache cron 
#         filename=basedir+"/gefs/derniergrib.hdf5"
#         if os.path.exists(filename)==False:
#             basedir='/home/jp/Documents/notebooks'
#             filename=basedir+"/gefs/derniergrib.hdf5"
           
#     else:     
#         filename=basedir+"/gefs/derniergrib.hdf5"
    

#     if os.path.exists(filename) == True:     # si le fichier existe on le charge direct
       
#         f1 = h5py.File(filename, 'r')
#         dset1 = f1['dataset_01']
#         GRGEFS = dset1[:]
#         tigGEFS = dset1.attrs['time_grib']
#         indices  = dset1.attrs['indices']   # Le grib est completement a jour  l'indice est enregistre dans le fichier filename
#         f1.close()
      
#     return    tigGEFS,GRGEFS,filename,indices





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



def prevision(tig, GR, tp, latitude, longitude):
    ''' Barbare mais  1/20eme du temps de regulargridinterpolator !! '''
    ''' Attention Cette version utilise un systeme de coordonnees du type folium'''
    itemp = (tp - tig) / 3600 / 3
    ilati = 90-latitude
    ilong = (longitude) % 360
    iitemp=math.floor(itemp)
    iilati=math.floor(ilati)
    iilong=math.floor(ilong)

    #print ('indices',itemp,ilati,ilong)
    ditemp=itemp%1
    dilati=ilati%1
    dilong=ilong%1
    v000=GR[iitemp][iilati][iilong]
    v010=GR[iitemp][iilati+1][iilong]
    v001=GR[iitemp][iilati][iilong+1]
    v011=GR[iitemp][iilati+1][iilong+1]
    v0x0=v000+dilati*(v010-v000)
    v0x1=v001+dilati*(v011-v001)
    v0xx=v0x0+dilong*(v0x1-v0x0)
    v100=GR[iitemp+1][iilati][iilong]
    v110=GR[iitemp+1][iilati+1][iilong]
    v101=GR[iitemp+1][iilati][iilong+1]
    v111=GR[iitemp+1][iilati+1][iilong+1]
    v1x0=v100+dilati*(v110-v100)
    v1x1=v101+dilati*(v111-v101)
    v1xx=v1x0+dilong*(v1x1-v1x0)
    vxxx=v0xx+ditemp*(v1xx-v0xx)   
    
    vit_vent_n = np.abs(vxxx) * 1.94384
    #minoration a 2 de la vitesse des vents
    #vit_vent_n[vit_vent_n<2] = 2

    angle_vent = (270 - np.angle(vxxx, deg=True)) % 360
    return vit_vent_n, angle_vent    

def previsionbis(tig, GR, tp, latitude, longitude):
    ''' Barbare mais  1/20eme du temps de regulargridinterpolator !! '''
    ''' Attention Cette version utilise les coordonnees folium'''
    ''' pour etre coherent avec zezo dans cette version le temps est interpolé en premier'''


    itemp = (tp - tig) / 3600 / 3
    ilati = 90-latitude
    ilong = (longitude) % 360
    iitemp=math.floor(itemp)
    iilati=math.floor(ilati)
    iilong=math.floor(ilong)

    #print ('indices',itemp,ilati,ilong)
    ditemp=itemp%1
    dilati=ilati%1
    dilong=ilong%1
    # on va arrondir le temps par fraction de 10mn
    fraction=math.floor(ditemp*18)/18

    v000=GR[iitemp][iilati][iilong]
    v010=GR[iitemp][iilati+1][iilong]
    v001=GR[iitemp][iilati][iilong+1]
    v011=GR[iitemp][iilati+1][iilong+1]
    v100=GR[iitemp+1][iilati][iilong]
    v110=GR[iitemp+1][iilati+1][iilong]
    v101=GR[iitemp+1][iilati][iilong+1]
    v111=GR[iitemp+1][iilati+1][iilong+1]

    
     # ici on interpole sur le temps au quatre points 
    vx00=v000+fraction*(v100-v000)
    vx10=v010+fraction*(v110-v010)
    vx01=v001+fraction*(v101-v001)
    vx11=v011+fraction*(v111-v011)

    # on fait ensuite une interpolation bilineaire sur les latitudes
    vxx0=vx00+ dilati*(vx10-vx00)
    vxx1=vx01+ dilati*(vx11-vx01)
    # puis sur la longitude
    vxxx=vxx0+dilong*(vxx1-vxx0)


    vit_vent_n = np.abs(vxxx) * 1.94384
    #minoration a 2 de la vitesse des vents
    #vit_vent_n[vit_vent_n<2] = 2

    angle_vent = (270 - np.angle(vxxx, deg=True)) % 360
    return vit_vent_n, angle_vent    


def prevision2(tig, GR, tp, latitude, longitude):
    ''' Barbare mais  1/20eme du temps de regulargridinterpolator !! '''
    ''' Prevision 2 teste une autre approche de l interpolation'''

    itemp = (tp - tig) / 3600 / 3
    ilati = 90-latitude
    ilong = (longitude) % 360
    iitemp=math.floor(itemp)
    iilati=math.floor(ilati)
    iilong=math.floor(ilong)

    #print ('indices',itemp,ilati,ilong)
    ditemp=itemp%1
    dilati=ilati%1
    dilong=ilong%1


    v000=GR[iitemp][iilati][iilong]
    v010=GR[iitemp][iilati+1][iilong]
    v001=GR[iitemp][iilati][iilong+1]
    v011=GR[iitemp][iilati+1][iilong+1]
    v0x0=v000+dilati*(v010-v000)
    v0x1=v001+dilati*(v011-v001)
    v0xx=v0x0+dilong*(v0x1-v0x0)
    v100=GR[iitemp+1][iilati][iilong]
    v110=GR[iitemp+1][iilati+1][iilong]
    v101=GR[iitemp+1][iilati][iilong+1]
    v111=GR[iitemp+1][iilati+1][iilong+1]
    v1x0=v100+dilati*(v110-v100)
    v1x1=v101+dilati*(v111-v101)
    v1xx=v1x0+dilong*(v1x1-v1x0)
    vxxx=v0xx+ditemp*(v1xx-v0xx)   
    


    mv000=np.abs(v000)
    mv010=np.abs(v010)
    mv001=np.abs(v001)
    mv011=np.abs(v011)
    mv100=np.abs(v100)
    mv110=np.abs(v110)
    mv101=np.abs(v101)
    mv111=np.abs(v111)
    mv0x0=mv000+dilati*(mv010-mv000)
    mv0x1=mv001+dilati*(mv011-mv001)
    mv0xx=mv0x0+dilong*(mv0x1-mv0x0)
    mv1x0=mv100+dilati*(mv110-mv100)
    mv1x1=mv101+dilati*(mv111-mv101)
    mv1xx=mv1x0+dilong*(mv1x1-mv1x0)
    mvxxx=mv0xx+ditemp*(mv1xx-mv0xx)   

    vit_vent_n2= mvxxx * 1.94384
    #minoration a 2 de la vitesse des vents
    #vit_vent_n[vit_vent_n<2] = 2

    angle_vent = (270 - np.angle(vxxx, deg=True)) % 360
    return vit_vent_n2, angle_vent    

def prevision3(tig, GR, tp, latitude, longitude):
    ''' Barbare mais  1/20eme du temps de regulargridinterpolator !! '''
    ''' Prevision 2 teste une autre approche de l interpolation'''

    itemp = (tp - tig) / 3600 / 3
    ilati = 90-latitude
    ilong = (longitude) % 360
    iitemp=math.floor(itemp)
    iilati=math.floor(ilati)
    iilong=math.floor(ilong)

    #print ('indices',itemp,ilati,ilong)
    ditemp=itemp%1
    dilati=ilati%1
    dilong=ilong%1
# on va arrondir le temps par fraction de 10mn
    fraction=math.floor(ditemp*18)/18

    v000=GR[iitemp][iilati][iilong]
    v010=GR[iitemp][iilati+1][iilong]
    v001=GR[iitemp][iilati][iilong+1]
    v011=GR[iitemp][iilati+1][iilong+1]
    v100=GR[iitemp+1][iilati][iilong]
    v110=GR[iitemp+1][iilati+1][iilong]
    v101=GR[iitemp+1][iilati][iilong+1]
    v111=GR[iitemp+1][iilati+1][iilong+1]

 # ici on interpole sur le temps au quatre points 
    vx00=v000+fraction*(v100-v000)
    vx10=v010+fraction*(v110-v010)
    vx01=v001+fraction*(v101-v001)
    vx11=v011+fraction*(v111-v011)

    # on fait ensuite une interpolation bilineaire sur les latitudes
    vxx0=vx00+ dilati*(vx10-vx00)
    vxx1=vx01+ dilati*(vx11-vx01)
    # puis sur la longitude
    vxxx=vxx0+dilong*(vxx1-vxx0)

    # on fait la meme interpolation mais sur les modules
    
    mv000=np.abs(v000)
    mv010=np.abs(v010)
    mv001=np.abs(v001)
    mv011=np.abs(v011)
    mv100=np.abs(v100)
    mv110=np.abs(v110)
    mv101=np.abs(v101)
    mv111=np.abs(v111)

    mvx00=mv000+fraction*(mv100-mv000)
    mvx10=mv010+fraction*(mv110-mv010)
    mvx01=mv001+fraction*(mv101-mv001)
    mvx11=mv011+fraction*(mv111-mv011)

    # on fait ensuite une interpolation bilineaire sur les latitudes
    mvxx0=mvx00+ dilati*(mvx10-mvx00)
    mvxx1=mvx01+ dilati*(mvx11-mvx01)
    # puis sur la longitude
    mvxxx=mvxx0+dilong*(mvxx1-mvxx0)
    speed_s=mvxxx
    speed_uv=np.abs(vxxx)
    vit_vent_n2= speed_s * 1.94384 

    #vit_vent_n2= (speed_s+speed_uv)/2 * 1.94384      # on prend la moyenne et on divise par 2


    #minoration a 2 de la vitesse des vents
    #vit_vent_n[vit_vent_n<2] = 2

    angle_vent = (270 - np.angle(vxxx, deg=True)) % 360
    return vit_vent_n2, angle_vent    



def prevision5(tig, GR, tp, latitude, longitude):
    ''' Barbare mais  1/20eme du temps de regulargridinterpolator !! '''
    ''' Prevision 2 teste une autre approche de l interpolation'''
    ''' Prevision5 arrondit le temps par portion de 10 mn '''
    ''' prevision5 fait ensuite la moyenne de speed s et speed uv '''
    ''' la majoration des vents <2 N est prise en compte '''
    
    
    itemp = (tp - tig) / 3600 / 3
    ilati = 90-latitude
    ilong = (longitude) % 360
    iitemp=math.floor(itemp)
    iilati=math.floor(ilati)
    iilong=math.floor(ilong)
    iitemp=min(iitemp,127) 
    #print ('indices',itemp,ilati,ilong)
    ditemp=itemp%1
    dilati=ilati%1
    dilong=ilong%1
# on va arrondir le temps par fraction de 10mn
    fraction=math.floor(ditemp*18)/18

    v000=round(GR[iitemp][iilati][iilong],3)
    v010=round(GR[iitemp][iilati+1][iilong],3)
    v001=round(GR[iitemp][iilati][(iilong+1)%360],3)
    v011=round(GR[iitemp][iilati+1][(iilong+1)%360],3)
    v100=round(GR[iitemp+1][iilati][iilong],3)
    v110=round(GR[iitemp+1][iilati+1][iilong],3)
    v101=round(GR[iitemp+1][iilati][(iilong+1)%360],3)
    v111=round(GR[iitemp+1][iilati+1][(iilong+1)%360],3)

 # ici on interpole sur le temps au quatre points 
    vx00=v000+fraction*(v100-v000)
    vx10=v010+fraction*(v110-v010)
    vx01=v001+fraction*(v101-v001)
    vx11=v011+fraction*(v111-v011)

    # on fait ensuite une interpolation bilineaire sur les latitudes
    vxx0=vx00+ dilati*(vx10-vx00)
    vxx1=vx01+ dilati*(vx11-vx01)
    # puis sur la longitude
    vxxx=vxx0+dilong*(vxx1-vxx0)

    # on fait la meme interpolation mais sur les modules
    
    mv000=np.abs(v000)
    mv010=np.abs(v010)
    mv001=np.abs(v001)
    mv011=np.abs(v011)
    mv100=np.abs(v100)
    mv110=np.abs(v110)
    mv101=np.abs(v101)
    mv111=np.abs(v111)

    mvx00=mv000+fraction*(mv100-mv000)
    mvx10=mv010+fraction*(mv110-mv010)
    mvx01=mv001+fraction*(mv101-mv001)
    mvx11=mv011+fraction*(mv111-mv011)

    # on fait ensuite une interpolation bilineaire sur les latitudes
    mvxx0=mvx00+ dilati*(mvx10-mvx00)
    mvxx1=mvx01+ dilati*(mvx11-mvx01)
    # puis sur la longitude
    mvxxx=mvxx0+dilong*(mvxx1-mvxx0)
    speed_s=mvxxx
    speed_uv=np.abs(vxxx)


    vit_vent_n= (speed_s+speed_uv)/2 * 1.94384  # on prend la moyenne et on divise par 2
    #minoration a 2 de la vitesse des vents
    if (vit_vent_n<2):
        vit_vent_n=2

    angle_vent = (270 - np.angle(vxxx, deg=True)) % 360
    return vit_vent_n, angle_vent   

def prevision5_vr(tig,GR,tp,latitude,longitude):
    ''' tig est le temps du grib, GR est le fichier grib,  tp le moment de la prevision en secondes, lat et lng les latitudes et longitudes'''
    ''' tp  doit etre en secondes UTC comparables a tig'''
    itemp = (tp - tig) / 3600 / 3
    ilati = 90-latitude
    ilong = (longitude) % 360
   
    iitemp=math.floor(itemp)
    iilati=math.floor(ilati)
    iilong=math.floor(ilong)
    iitemp=min(iitemp,127)          # securite si depassement de temps 
    # print ('indices dans prev',itemp,ilati,ilong)
    # print ('indices entiers dans prev',iitemp,iilati,iilong)
    ditemp=itemp%1
    dilati=ilati%1
    dilong=ilong%1
    # on va arrondir le temps par fraction de 10mn
    fraction=math.floor(ditemp*18)/18
    
    v000=np.round(GR[iitemp][iilati][iilong],3)
    v010=np.round(GR[iitemp][iilati+1][iilong],3)
    v001=np.round(GR[iitemp][iilati][iilong+1],3)
    v011=np.round(GR[iitemp][iilati+1][iilong+1],3)
    v100=np.round(GR[iitemp+1][iilati][iilong],3)
    v110=np.round(GR[iitemp+1][iilati+1][iilong],3)
    v101=np.round(GR[iitemp+1][iilati][iilong+1],3)
    v111=np.round(GR[iitemp+1][iilati+1][iilong+1],3)
    
     # ici on interpole sur le temps au quatre points 
    vx00=v000+fraction*(v100-v000)
    vx10=v010+fraction*(v110-v010)
    vx01=v001+fraction*(v101-v001)
    vx11=v011+fraction*(v111-v011)

    # on fait ensuite une interpolation bilineaire sur les latitudes
    vxx0=vx00+ dilati*(vx10-vx00)
    vxx1=vx01+ dilati*(vx11-vx01)
    # puis sur la longitude
    vxxx=vxx0+dilong*(vxx1-vxx0)

    # on fait la meme interpolation mais sur les modules
    
    mv000=np.abs(v000)
    mv010=np.abs(v010)
    mv001=np.abs(v001)
    mv011=np.abs(v011)
    mv100=np.abs(v100)
    mv110=np.abs(v110)
    mv101=np.abs(v101)
    mv111=np.abs(v111)

    mvx00=mv000+fraction*(mv100-mv000)
    mvx10=mv010+fraction*(mv110-mv010)
    mvx01=mv001+fraction*(mv101-mv001)
    mvx11=mv011+fraction*(mv111-mv011)

    # on fait ensuite une interpolation bilineaire sur les latitudes
    mvxx0=mvx00+ dilati*(mvx10-mvx00)
    mvxx1=mvx01+ dilati*(mvx11-mvx01)
    
    # puis sur la longitude
    mvxxx=mvxx0+dilong*(mvxx1-mvxx0)
    speed_s=mvxxx
    speed_uv=np.abs(vxxx)


    vit_vent_n= (speed_s+speed_uv)/2 * 1.94384  # on prend la moyenne et on divise par 2
    #minoration a 2 de la vitesse des vents
    if (vit_vent_n<2):
        vit_vent_n=2
    
    # angle= 270-(math.atan2(v,u)*180/math.pi)
    angle_vent = (270 - np.angle(vxxx, deg=True)) % 360
    return vit_vent_n, angle_vent  

def f(deg): return abs(math.sin(deg/180 * math.pi))
def uv2s(u,v): return(u*u+v*v)**.5
def uv2d(u,v): return math.atan2(u,v)*180/math.pi+180

def prevision6(tig, GR, tp, latitude, longitude):
    ''' Barbare mais  1/20eme du temps de regulargridinterpolator !! '''
    ''' Prevision6 integre le calcul de type zezo'''
    itemp = (tp - tig) / 3600 / 3
    ilati = 90-latitude
    ilong = (longitude) % 360
    iitemp=math.floor(itemp)
    iilati=math.floor(ilati)
    iilong=math.floor(ilong)

    #print ('indices',itemp,ilati,ilong)
    ditemp=itemp%1
    dilati=ilati%1
    dilong=ilong%1
# on va arrondir le temps par fraction de 10mn
    fraction=math.floor(ditemp*18)/18
   
    
    v000=GR[iitemp][iilati][iilong] *3.6
    v010=GR[iitemp][iilati+1][iilong] *3.6
    v001=GR[iitemp][iilati][iilong+1] *3.6
    v011=GR[iitemp][iilati+1][iilong+1]*3.6
    v100=GR[iitemp+1][iilati][iilong] *3.6
    v110=GR[iitemp+1][iilati+1][iilong] *3.6
    v101=GR[iitemp+1][iilati][iilong+1] *3.6
    v111=GR[iitemp+1][iilati+1][iilong+1] *3.6

    #print('interpolation temporelle')
    vx00=v000+fraction*(v100-v000)
    vx10=v010+fraction*(v110-v010)
    vx01=v001+fraction*(v101-v001)
    vx11=v011+fraction*(v111-v011)
    u1=vx10.real
    u2=vx11.real
    u3=vx00.real
    u4=vx01.real
    
    v1=vx10.imag
    v2=vx11.imag
    v3=vx00.imag
    v4=vx01.imag
   
    # on calcule l angle aux 4 points
    d1 =(270 - np.angle(vx10, deg=True)) % 360
    d2 =(270 - np.angle(vx11, deg=True)) % 360
    d3 =(270 - np.angle(vx00, deg=True)) % 360
    d4 =(270 - np.angle(vx01, deg=True)) % 360
    
    
    s1=uv2s(u1,v1)
    s2=uv2s(u2,v2)
    s3=uv2s(u3,v3)
    s4=uv2s(u4,v4)
 
    x=dilong
    y=dilati
    
    u=(u2+u3-u1-u4)*x*y +(u4-u3)*x +(u1-u3)*y + u3
    v=(v2+v3-v1-v4)*x*y +(v4-v3)*x +(v1-v3)*y + v3
    speed_s  = (s2+s3-s1-s4)*x*y +(s4-s3)*x +(s1-s3)*y + s3
    speed_uv = uv2s(u,v)
    angle_uv=uv2d(u,v)

    cs_uv=uv2s((u1+u2+u3+u4)/4 ,(v1+v2+v3+v4)/4)
    cs_avg=(s1+s2+s3+s4)/4
    cs_ratio=cs_uv/cs_avg
    c=[0,0,0,0]
    if x<.5 :                           # on est cote gauche 
        if y<.5:  
            c[0]=f(d1-d2)
            c[1]=cs_ratio
            c[2]=1
            c[3]=f(d3-d4)
        else:
            y-=0.5
            c[0]=1
            c[1]=f(d1-d2)
            c[2]=f(d1-d3)
            c[3]=cs_ratio
    else: 
        if y<.5: 
            x-=0.5
            c[0]=cs_ratio
            c[1]=f(d2-d4)
            c[2]=f(d3-d4)
            c[3]=1
        else:   
            y-=0.5
            c[0]=f(d1-d2)
            c[1]=1
            c[2]=cs_ratio
            c[3]=f(d2-d4)  
    x*=2
    y*=2
    c_coeff=(c[1]+c[2]-c[0]-c[3])*x*y +(c[3]-c[2])*x +(c[0]-c[2])*y +c[2]
    s_coeff= (speed_uv/speed_s)**(1-c_coeff**.7)
    speed_s *=s_coeff
    speed=speed_s/1.852
    speed=max(speed,2)                    # si la vitesse est inferieure a 2
    return speed, angle_uv   


def previsiongefs(tigGEFS, GR, tp, latitude, longitude):
    ''' Barbare mais  1/20eme du temps de regulargridinterpolator !! '''
    ''' Attention Cette version utilise un systeme de coordonnees du type folium'''
    itemp = (tp - tigGEFS) / 3600 / 3
    
    ilati = 180-latitude*2
    ilong = (longitude*2) % 720
    
    iitemp=math.floor(itemp)
    
    iilati=math.floor(ilati)
    iilong=math.floor(ilong)

    #print ('indices',itemp,ilati,ilong)
    ditemp=itemp%1
    dilati=ilati%1
    dilong=ilong%1
    v000=GR[iitemp][iilati][iilong]
    v010=GR[iitemp][iilati+1][iilong]
    v001=GR[iitemp][iilati][(iilong+1)%720]
    v011=GR[iitemp][iilati+1][(iilong+1)%720]
    v0x0=v000+dilati*(v010-v000)
    v0x1=v001+dilati*(v011-v001)
    v0xx=v0x0+dilong*(v0x1-v0x0)
    v100=GR[iitemp+1][iilati][iilong]
    v110=GR[iitemp+1][iilati+1][iilong]
    v101=GR[iitemp+1][iilati][(iilong+1)%720]
    v111=GR[iitemp+1][iilati+1][(iilong+1)%720]
    v1x0=v100+dilati*(v110-v100)
    v1x1=v101+dilati*(v111-v101)
    v1xx=v1x0+dilong*(v1x1-v1x0)
    vxxx=v0xx+ditemp*(v1xx-v0xx)   

    vit_vent_n = np.abs(vxxx) * 1.94384
    #minoration a 2 de la vitesse des vents
    vit_vent_n=max(vit_vent_n,2)

    angle_vent = (270 - np.angle(vxxx, deg=True)) % 360
    return vit_vent_n, angle_vent    

# def previsiontab(tig, GR, tp, lat, lon):
#     '''lat et lon sont des latitudes et longitudes'''
#     '''tp est une valeur mais a voir si on ne peut pas metttre un np.array de temps'''
#     lat=90-lat
#     lon=lon%360
#     dx=lon%1
#     dy=lat%1
#     lati=lat.astype(int)
#     loni=lon.astype(int)
#     itemp=(tp - tig) / 3600 / 3
#     ditemp=itemp%1
#     iitemp=math.floor(itemp)
#     fraction=math.floor(ditemp*18)/18     #temps arrondi par fractions de 10 mn

#     UV000=np.round(GR[iitemp,lati,loni],3)
#     UV010=np.round(GR[iitemp,lati+1,loni],3)
#     UV001=np.round(GR[iitemp,lati,loni+1],3)
#     UV011=np.round(GR[iitemp,lati+1,loni+1],3)

#     UV100=np.round(GR[iitemp+1,lati,loni],3)
#     UV110=np.round(GR[iitemp+1,lati+1,loni],3)
#     UV101=np.round(GR[iitemp+1,lati,loni+1],3)
#     UV111=np.round(GR[iitemp+1,lati+1,loni+1],3)

#     UVX00=UV000+fraction*(UV100-UV000)     # on interpole sur le temps
#     UVX10=UV010+fraction*(UV110-UV010)
#     UVX01=UV001+fraction*(UV101-UV001)
#     UVX11=UV011+fraction*(UV111-UV011)

#     res=UVX00+(UVX01-UVX00)*dx +(UVX10-UVX00)*dy  +(UVX11+UVX00-UVX10-UVX01)*dx*dy   #interpolation bilineaire
#     vitesses=np.abs(res)* 1.94384 
#     angles = (270 - np.angle(res, deg=True)) % 360
#     return vitesses,angles

def previsiontabgefs(tig, GR, tp, lat, lon):
    '''lat et lon sont des np array de latitudes et longitudes'''
    '''tp est une valeur mais a voir si on ne peut pas metttre un np.array de temps'''
    
    if not isinstance(lat,np.ndarray):           #permet de traiter le cas de valeurs simples 
        lat=np.array([lat])
        lon=np.array([lon]) 
    else:
        lat=lat.ravel()
        lon=lon.ravel()
    
    
    
    if isinstance(tp,float):                     # permet de traiter le cas une seule valeur de temps pour differents points 
        tp=np.ones(len(lat))*tp   
    
    
    
    
    lat=2*(90-lat)
    lon=(2*lon)%720
    dx=lon%1
    dy=lat%1
    
    lati=lat.astype(int)
    loni=lon.astype(int)
    
    itemp=(tp - tig) / 3600 / 3
    ditemp=itemp%1
    # iitemp=math.floor(itemp)
    iitemp=itemp.astype(int)
    iitemp[iitemp>127]=127
       
    fraction=(ditemp*18).astype(int)/18       #temps arrondi par fractions de 10 mn
    UV000=np.round(GR[iitemp,lati,loni],3)
    UV010=np.round(GR[iitemp,lati+1,loni],3)
    UV001=np.round(GR[iitemp,lati,(loni+1)%720],3)
    UV011=np.round(GR[iitemp,lati+1,(loni+1)%720],3)

    UV100=np.round(GR[iitemp+1,lati,loni],3)
    UV110=np.round(GR[iitemp+1,lati+1,loni],3)
    UV101=np.round(GR[iitemp+1,lati,(loni+1)%720],3)
    UV111=np.round(GR[iitemp+1,lati+1,(loni+1)%720],3)

    UVX00=UV000+fraction*(UV100-UV000)     # on interpole sur le temps
    UVX10=UV010+fraction*(UV110-UV010)
    UVX01=UV001+fraction*(UV101-UV001)
    UVX11=UV011+fraction*(UV111-UV011)

    res=UVX00+(UVX01-UVX00)*dx +(UVX10-UVX00)*dy  +(UVX11+UVX00-UVX10-UVX01)*dx*dy   #interpolation bilineaire
    vitesses=np.abs(res)* 1.94384 
    vitesses[vitesses>70] = 70 
    vitesses[vitesses<2]  = 2    
    angles = (270 - np.angle(res, deg=True)) % 360
    return vitesses,angles




# la meme chose mais avec en plus un tableau de temps 
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


# Les fonctions suivantes sont obsoletes previsiontab et previsiontabtemps etant plus rapides     


def prevision_tableau(tig,GR,tp,pointsxy):
    '''vitesse 30%superieure a prevision_tableau3 avec RegularGridInterpolator'''
    v= np.zeros(len(pointsxy))
    a= np.zeros(len(pointsxy))
    for i in range(len(pointsxy)):
        v[i],a[i]=prevision(tig, GR, tp, pointsxy[i,1],pointsxy[i,0])
    return v,a

def prevision_tableau2 (GR,temp,point):       # optimisation  comme precedente sans effet
    ''' calcule les previsions a partir d'une liste des temps par rapport au depart et des points sous forme complexe'''
    temps = temp.reshape((1, -1))    #-3600              # Ajustement VR 3600 
    points=point.reshape((1, -1))
    fn3 = RegularGridInterpolator((ix, iy, iz), GR)
    tab_itemp=temps.reshape((1,-1))/ 3600 / 3
    ilati = np.imag(points) + 90
    ilong = np.real(points) %360
    e = np.concatenate(( tab_itemp.T, ilati.T, ilong.T), axis=1)
    prevs = fn3((e))   #prevs est un tableau de complexes des vecteurs du vent aux differents points
    vitesse = np.abs(prevs) * 1.94384
    angle_vent = (270 - np.angle(prevs, deg=True)) % 360
    return vitesse, angle_vent







def meteo_tableau(tig,GR,tp,lat,lng):
    '''calcul d'un tableau des tws et twd aux differents points'''
    '''tp est une valeur unique'''
    '''regulargrid interpolator n apporte rien '''
    v= np.zeros(len(lat))
    a= np.zeros(len(lng))
    for i in range(len(lat)):
        v[i],a[i]=prevision5_vr(tig, GR, tp, lat[i],lng[i])  # latitude en premier 
    return v,a








def meteo_tableau_range(tig,GR,T,lat,lng):

    '''calcul d'un tableau des tws et twd aux differents points'''
    '''T est un tableau de temps'''
    
    v= np.zeros(len(lat))
    a= np.zeros(len(lng))
    for i in range(len(lat)):
        v[i],a[i]=prevision5_vr(tig, GR, T[i], lat[i],lng[i])  # latitude en premier 
    return v,a


def ftwa(cap, dvent):
    '''retourne la valeur absolue de la twa'''
    twa = 180 - abs(((360 - dvent + cap) % 360) - 180)
    return twa     


def ftwaos(cap, dvent):
    '''twa orientee simple avec des valeurs float'''
    twa=(cap-dvent+360)%360
    if twa<180:
        twa=-twa
    else:
        twa=360-twa
    return twa   



def ftwao_old( HDG,TWD):
    '''retourne un nparray de twa orientees babord<0 tribord>0 à partir de ndarray HDG et TWD'''
    A=np.mod((HDG-TWD+360),360)
    return np.where(A<180,-A,360-A)

def ftwao(HDG,TWD):
    return np.mod((TWD-HDG+540),360)-180
 

def signetwa(HDG,TWD):
    A=np.mod((HDG-TWD+360),360)
    return np.where(A<180,-A,360-A)
    

def fcap(twao,twd):
    ''' retourne le cap en fonction de la twaorientée et de la direction du vent '''
    cap=(360+twd-twao)%360
    return cap


def cap_dep_ar(ydep,xdep,yar,xar):
    '''donne le cap en degres du point de depart vers le point d arrivee definis par leur coords'''
    cap=math.atan2(xar-xdep,(yar-ydep)/(math.cos(ydep*math.pi/180)))*180/math.pi
    cap=(cap+360)%360
    return cap

def rangenavi(capa, capb):
    ''' donne les caps entre les deux bornes en tenant compte du passage a 360'''
    '''@jit ralentit'''
    if capb > capa:
        range = np.arange(capa, capb, 1)
    else:
        range = np.concatenate((np.arange(0, capb + 1, 1), np.arange(capa, 360, 1)), axis=0)
    return range


def range_cap(direction_objectif, direction_vent, a_vue_objectif, angle_pres, angle_var):
    '''Retourne les caps utiles a parcourir elimine les pres et vent arriere trop serres'''
    '''pas d'acceleration avec @jit '''
    ''' pas utilise dans la deerniere version pour eviter les boucles (a voir?)'''
    direction_vent, direction_objectif = int(direction_vent), int(direction_objectif)
    cap1 = (direction_vent + angle_pres) % 360
    cap2 = (direction_vent - angle_pres + 1) % 360
    cap3 = (180 + direction_vent + angle_var) % 360
    cap4 = (180 + direction_vent - angle_var + 1) % 360
    cap5 = (direction_objectif - a_vue_objectif) % 360
    cap6 = (direction_objectif + a_vue_objectif) % 360
    z1 = rangenavi(cap1, cap4)
    z2 = rangenavi(cap3, cap2)
    z3 = rangenavi(cap5, cap6)
    range1 = np.intersect1d(z1, z3)
    range2 = np.intersect1d(z2, z3)

    rangetotal = np.concatenate((range1, range2), axis=0)
    return rangetotal

def dist_cap(D,A):
    ''' retourne la distance et l'angle du deplacement entre le depart et l'arrivee 
    les points de depart et arrivee sont sous forme complexe'''
    ''' Le calcul est en geometrie plane '''
    coslat= np.cos(D.imag * math.pi / 180)
    C=(A.real-D.real)*coslat +(A.imag-D.imag)*1j
    return np.abs(C), (450 + np.angle(C, deg=True)) % 360    

def dist_cap_ortho(lati,lngi,latfi,lngfi):
    '''donnees en coordonnees decimaux resultat en miles nautiques '''
    latirad=lati*math.pi/180
    latfrad=latfi*math.pi/180
    lb_m_la=(lngfi-lngi)*math.pi/180
    cosfia=math.cos(latirad)
    sinfia=math.sin(latirad)
    sinfib=math.sin(latfrad)
    cosfib=math.cos(latfrad)
    cos_lb_m_la=math.cos(lb_m_la)
    sin_lb_m_la=math.sin(lb_m_la)
    capo= math.atan(cosfib*sin_lb_m_la/(cosfia*sinfib-sinfia*cosfib*cos_lb_m_la))*180/math.pi
    if (latfi-lati)<0:
	    capo=180+capo
    else :
        capo=(capo+360)%360
    dist= math.acos(sinfia*sinfib+cosfia*cosfib*cos_lb_m_la)/math.pi*180*60
   
    return dist,capo







def dist_cap4(points,A):
    ''' points est une  liste de points a 2 dimensions , a est un point complexe '''
    ''' on retourne un tableau des distances et des caps '''
    #print(points.shape)
    D=points[0]+points[1]*1j   # on transforme les points en points complexes
    C = A - D
    return np.abs(C), (450 + np.angle(C, deg=True)) % 360

def depl(y0,x0, vit ,cap, dt ):
    '''Deplacement depuis yo,xo avec vitesse cap et intervalle de temps '''
    y1=y0+vit*dt/3600/60*math.cos(cap*math.pi/180)
    x1=x0+vit*dt/3600/60*math.sin(cap*math.pi/180)/math.cos(y0*math.pi/180)
    return y1,x1

def deplacement2(x0,y0,d_t,HDG,TWD,VT,A,twa,penalite):
    ''' fonction donnant le tuple point d arrivée en fonction des coordonnées du point de depart ''' 
    ''' c'est cette fonction qui sert dans le calcul des isochrones '''
    ''' ameliore deplacement de 30% '''
    # integre une penalite si la nouvelle twa est de signe inverse de la nouvelle
    if penalite !=0 :   
        TWAO=ftwaov2( HDG,TWD)                      #twa orientee sur chaque point 
        Virement=np.where(TWAO*twa>0,False,True)    #si twa precedent du meme signe produit > 0 donc pas de virement donc Virement=False = 0 
        # s'il y a virement on est penalise de la duree en secondes donc pour dt =600 s on est penalise de 100s si penalite =100
        # avec winchs pros 50% pendant 75 s =32 s
        DT=np.ones(len(VT))*(d_t-Virement*penalite)
        HDG_R = HDG * math.pi / 180     # cap en radians
        X= x0+ DT / 3600 / 60 * VT * (np.sin(HDG_R) / math.cos(y0 * math.pi / 180)) 
        Y= y0- DT / 3600 / 60 * VT * np.cos(HDG_R)
    else :
        HDG_R = HDG * math.pi / 180     # cap en radians
        X= x0+ d_t / 3600 / 60 * VT * (np.sin(HDG_R) / math.cos(y0 * math.pi / 180)) 
        Y= y0- d_t / 3600 / 60 * VT * np.cos(HDG_R)

    
    Di,Ca=dist_cap(X+Y*1j, A)

    return X,Y,Di,Ca

#polaires=json.load(open('../../routeur2021/static/js/polars.json'))

# filename='/home/jphe/routeur2021/static/js/polars.json'
# with open(filename, 'r') as fichier:                      # change dans fichier courants
#      data1 = json.load(fichier)
        
# bateau='Class40'
# angle_twa_pres = data1[bateau]["pres_mini"]
# angle_twa_ar   = data1[bateau]["var_mini"]
# tab_tws        = data1[bateau]["tab_tws"]                 # necessaire pour faire les interpolations
# tab_twa        = data1[bateau]["tab_twa"]
# polaires       = data1[bateau]["polaires"]
# polaires2=np.ravel(polaires)                              # aplatissement pour calcul gpu

def recherche (twa,tab_twa):
    ''' recherche l'indice d'une twa ou tws dans le tableau '''
    k=0
    while (twa > tab_twa[k]):
        k+=1
    return k

def polaire_simple(twa,  tws, tab_twa , tab_tws  ,polaires2):
    ''' Calcule les polaires a partir de la twa tws tab_twa tab_tws et tableau des polaires '''
    nb_tws=len(tab_tws)
    n1=recherche (twa,tab_twa)
    n2=recherche (tws,tab_tws)
    vitesse1=polaires2 [(n1-1)*nb_tws +(n2-1)]
    vitesse2=polaires2 [n1*nb_tws +(n2-1)]
    vitesse3=polaires2 [(n1-1)*nb_tws +n2]
    vitesse4=polaires2 [n1*nb_tws +n2]
    dx=twa-tab_twa[n1-1]
    dy=tws-tab_tws[n2-1]
    deltax=tab_twa[n1]-tab_twa[n1-1]
    deltay=tab_tws[n2]-tab_tws[n2-1]
    dftwa=vitesse2-vitesse1
    dftws=vitesse3-vitesse1
    dftwatws=vitesse1+vitesse4-vitesse2-vitesse3
    vitesse=dftwa*dx/deltax +dftws*dy/deltay +dftwatws*dx*dy/deltax/deltay +vitesse1
    return vitesse     


def polaire_simple2(twa,  tws, polairesunit):
    dtwa=twa%1
    dtws=tws%1
    twai=int(twa)
    twsi=int(tws)
   
    vit00=polairesunit[twsi,twai]
    vit10=polairesunit[twsi+1,twai]
    vit01=polairesunit[twsi,(twai+1)%180]
    vit11=polairesunit[twsi+1,(twai+1)%180]
    vit=vit00+(vit01-vit00)*dtwa +(vit10-vit00)*dtws  +(vit11+vit00-vit10-vit01)*dtwa*dtws
    return vit




def vit_polaires(polairesunit,twss,twaos):
    '''polairesunit est le tableau des polaires mis a 1 par 1 '''
    ''' TWS le tableau des vitesses de vent '''
    ''' TWA le tableau des TWA eventuellement orientees'''
    twas=np.abs(np.ravel(twaos))
    twasi=twas.astype(int)
    dtwas=twas%1
    twssi=twss.astype(int)
    dtwss=twss%1
    vit00=polairesunit[twssi,twasi]
    vit10=polairesunit[twssi+1,twasi]
    vit01=polairesunit[twssi,(twasi+1)%180]
    vit11=polairesunit[twssi+1,(twasi+1)%180]
    vit=vit00+(vit01-vit00)*dtwas +(vit10-vit00)*dtwss  +(vit11+vit00-vit10-vit01)*dtwas*dtwss   #interpolation bilineaire
    return vit 



def vit_polaires10 (polairesunit10,twss,twaos):
    twss  =np.around(twss*10,0).astype(int)
    twaos =np.around(np.abs(twaos*10),0).astype(int)
    return polairesunit10[twss,twaos]



def polaire_vect(polaires,tab_twa, tab_tws,TWS,TWD,HDG):
    '''Retourne un tableau de polaires en fonction des polaires bateau  de TWS TWD et HDG'''
    '''TWS true Wind speed, TWD true wind direction , HDG caps'''
    '''Les trois tableaux doivent avoir la meme dimension'''
   
    TWA=(180 - np.abs(((360 - TWD + HDG) % 360) - 180)).reshape((-1, 1))
    TWS2=TWS.reshape((-1, 1))
    donnees=np.concatenate((TWA,TWS2),axis=1)
    valeurs = interpn((tab_twa, tab_tws), polaires, donnees, method='linear')
    return valeurs









def polaire_vect_twa(polaires,tabtwa, tabtws,TWS,TWAO):
    '''Retourne un tableau de polaires en fonction des polaires bateau  de TWS TWD et HDG'''
    '''TWS true Wind speed, TWD true wind direction , HDG caps'''
    '''Les trois tableaux doivent avoir la meme dimension'''
   
    TWA=np.abs(TWAO)
    TWS2=TWS.reshape((-1, 1))
    donnees=np.concatenate((TWA,TWS2),axis=1)
    valeurs = interpn((tabtwa, tabtws), polaires, donnees, method='linear')
    return valeurs


def polaire2_vectv2(polaires,tabtwa, tabtws,vit_vent,angle_vent,tableau_caps):
    '''il n'y a qu'une vitesse et un angle mais plusieurs caps '''
    ''' 20% plus performant que la fonction de base'''
    #transformation tableau de caps en un point en tableau de donnees (twa , vit_vent)
    l=len(tableau_caps)
    twax = 180 - np.abs(((360 - angle_vent + tableau_caps) % 360) - 180)  # broadcasting
    twa  = twax.reshape(-1,1)
    for i in range (len(twa)):
        if twa[i]<30:
            twa[i]=30
    vvent = (np.ones(l)*vit_vent).reshape(-1,1)
    donnees= np.concatenate((twa,vvent), axis = 1) 
    valeurs = interpn((tabtwa, tabtws), polaires, donnees, method='linear')
    return valeurs

def polaire3_vect(polaires,tab_twa, tab_tws,TWS,TWD,HDG):
    '''Retourne un tableau de polaires en fonction des polaires bateau  de TWS TWD et HDG'''
    '''TWS true Wind speed, TWD true wind direction , HDG caps'''
    '''Les trois tableaux doivent avoir la meme dimension'''
    TWA=(180 - np.abs(((360 - TWD + HDG) % 360) - 180)).reshape((-1, 1))
    TWS2=TWS.reshape((-1, 1))
    donnees=np.concatenate((TWA,TWS2),axis=1)
    valeurs = interpn((tab_twa, tab_tws), polaires, donnees, method='linear')
    return valeurs


def vmgmax(tws,tabtwa,tabtws):
    '''Donne les vmgmax au pres et vent arriere et les angles de vent correspondant '''
    TWA =np.arange(30,60,0.1).reshape((-1, 1))
    TWA2=np.arange(135,160,0.1).reshape((-1, 1))
    TWA=np.concatenate((TWA,TWA2),axis=0)
    TWS=(np.ones(len(TWA))*tws).reshape((-1, 1))
    donnees=np.concatenate((TWA,TWS),axis=1)
    valeurs = interpn((tabtwa, tabtws), polaires, donnees, method='linear')
    costwa=np.cos(TWA*math.pi/180)
    VMG=valeurs*costwa.T
    vmgmax=np.max(VMG)
    vmgmin=np.min(VMG)
    twamax=TWA[np.argmax(VMG,axis=1),0][0]
    twamin=TWA[np.argmin(VMG,axis=1),0][0]
    return twamax,vmgmax,twamin,vmgmin



def vmg():
    ''' retourne un tableau des vmgmax pour les forces de vent entre 0 et 35 Noeuds '''
    TWS=np.arange(0,35,0.1)
    VMG=np.zeros((len(TWS),5))
    VMG[:,0]=TWS
    for i in range (len(TWS)):    
        VMG[i,1]=vmgmax(TWS[i])[0]
        VMG[i,2]=vmgmax(TWS[i])[1]
        VMG[i,3]=vmgmax(TWS[i])[2]
        VMG[i,4]=vmgmax(TWS[i])[3]
    return VMG    


def to_pandas_csv(chemincomplet,nomcsv):
    N       = chemincomplet[: ,0]
    lat     = chemincomplet[: ,1]
    lng     = chemincomplet[: ,2]
    T       = chemincomplet[: ,3]
    tws     = chemincomplet[: ,4]
    twd     = chemincomplet[: ,5]
    cap     = chemincomplet[: ,6]
    twa     = chemincomplet[: ,7]
    vitesse = chemincomplet[: ,8]
    

    df=pd.DataFrame({'N':N,'lat':lat ,'lng' :lng,'T_s':T,'tws':tws,'twd':twd,'cap':cap,'twa':twa,'speed':vitesse})
    #df=pd.DataFrame({'T':temps_tab ,'T_s':temps_s_tab ,'lat' :lat_tab,'lng' :lng_tab,'tws' :tws_tab,'twd' :twd_tab,'cap' :cap_tab ,'twa' :twa_tab,'speed':speed_tab})
    df.to_csv(nomcsv)      # exportation en csv
   # print(df.head(5))
   # print(df.tail(5))


    return None


def vents_encode2(tig,GR,latini,latfin,longini,longfin):
    ''' extrait du grib GR les donnees entre ini et fin sur 24 h et l'exporte en json pour utilisation sur site web '''
    #les latitudes et longitudes sont en coordonnees leaflet positives au nord la latitude initiale est la plus petite (plus au sud )
    # on les transforme en indices grib
    ilatini=90 -latini    #ilatini est l'indice de grib dans GR ( ex pour latini= 60 nord ilatini=30)
    ilatfin=90 -latfin
    # pour les longitudes longini est la plus a l'ouest 

    if (longini <longfin) :
        U10=GR[0:12,ilatini:ilatfin,longini:longfin].real
        V10=GR[0:12,ilatini:ilatfin,longini:longfin].imag
    else :
        fin = 360-longini         # sert a determiner la coupe a la fin 
        debut =longfin+1
        U10=np.concatenate((GR[0:12,ilatini:ilatfin,longini:360].real,GR[0:12,ilatini:ilatfin,0:longfin].real),axis=2)
        V10=np.concatenate((GR[0:12,ilatini:ilatfin,longini:360].imag,GR[0:12,ilatini:ilatfin,0:longfin].imag),axis=2)
   
    u10=[arr.tolist() for arr in U10]
    v10=[arr.tolist() for arr in V10]
    return u10,v10    


def voile_utilisee (twao,tws,voileant,tab_twa,tab_tws,toutespolaires,nbvoiles):
    '''retourne la voile utilisee et la vitesse polaire atteinte '''
    ''' si la voile ant est dans la marge de tolerance de 1.014 conserve la voile anterieure '''
    twa=abs(twao)
    vitesses =np.zeros(nbvoiles)          # tableau destine a recevoir les vitesses pour les differentes voiles
    n1=recherche (twa,tab_twa) -1         #donne l indice au dessus 
    n2=recherche (tws,tab_tws) -1
    deltax=tab_twa[n1+1]-tab_twa[n1]
    deltay=tab_tws[n2+1]-tab_tws[n2]
    dx=twa-tab_twa[n1]
    dy=tws-tab_tws[n2]


    # print('len(typevoile',len(typevoile))    
    for i in range(nbvoiles):
        v00=toutespolaires[n1,n2,i]
        v10=toutespolaires[n1+1,n2,i]
        v01=toutespolaires[n1,n2+1,i]
        v11=toutespolaires[n1+1,n2+1,i]
        dfx0=v10-v00
        dfx1=v11-v01
        fx0=v00+(dx*dfx0)/deltax
        fx1=v01+(dx*dfx1)/deltax
        fxy=fx0+  dy* (fx1-fx0)/deltay
        vitesses[i]=fxy
        
        # on rajoute le hull et foils
        coefffoil=foil(twa,tws,speedRatio,twaMin,twaMax,twaMerge,twsMin,twsMax,twsMerge)
        vitesses[i]=vitesses[i]*hull*coefffoil
       
    # meilleure voile
    vitessemaxi=np.max(vitesses)
    indice     =np.argmax(vitesses)
    #calcul de la vitesse avec la voile anterieure
    
    
    if indice!=voileant :
        rapport=max(vitessemaxi,vitesses[voileant])/min(vitessemaxi,vitesses[voileant])
        # print('Rapport',rapport)
        vitessemaxiant=vitesses[voileant] 
        chgt=1
        # print ('indice,vitessemaxi,voileant,vitessemaxiant',indice,vitessemaxi,voileant,vitessemaxiant)
        if rapport<1.014:
            indice=voileant
    else :
        chgt=0
    #print ('Indice voile {} voile utilisee :  {} vitesse : {:6.3f} ' .format(i,voile[indice],vitessemaxi))
       
    return vitessemaxi,vitesses,indice,typevoile[indice],chgt

def vmgmaxspeed(tws,tab_twa , tab_tws  ,polaires):
    '''donne les valeurs de vmgmax et speedmax ainsi que les angles pour une force de vent'''
    '''Attention ici tab twa tabtws polaires sont des valeurs globales'''
    TWA =np.arange(30,160,0.1).reshape((-1, 1))
    TWS=(np.ones(len(TWA))*tws).reshape((-1, 1))
    donnees=np.concatenate((TWA,TWS),axis=1)
    valeurs = interpn((tab_twa, tab_tws), polaires, donnees, method='linear')
    costwa=np.cos(TWA*math.pi/180)
    VMG=valeurs*costwa.T
    vmgmax=np.max(VMG)
    vmgmin=np.min(VMG)
    twamax=TWA[np.argmax(VMG,axis=1),0][0]
    twamin=TWA[np.argmin(VMG,axis=1),0][0]
    speedmax=np.max(valeurs)
    twaspeedmax=TWA[np.argmax(valeurs,axis=0),0]
    return twamax,vmgmax,twamin,vmgmin,twaspeedmax,speedmax


def opti(twa, tws,tab_twa , tab_tws  ,polaires):
    '''Optimise la twa lorsqu elle est autour des valeurs de vmgmax'''
    ''' entree une twa et une tws'''
    ''' sortie la twa optimisee si pas proche de 3 valeur '''
    twamax,vmgmax,twamin,vmgmin,twaspeedmax,speedmax=vmgmaxspeed(tws,tab_twa , tab_tws  ,polaires)
    #print (twamax,vmgmax,twamin,vmgmin,twaspeedmax,speedmax)
    signe=twa/(abs(twa)+0.0001)
    if abs(twa)-twamax<3:
        twar=round((twamax*signe),0)
    elif abs(abs(twa)-twamin)<3:
        twar=round((twamin*signe),0)
    elif   abs(abs(twa)-twaspeedmax)<2: 
        twar=round(twaspeedmax*signe)
    #bannissement des valeurs hors laylines    
    elif abs(twa)<twamax:
        twar=twamax*signe
    elif abs(twa)>twamin:
        twar=round(twamin*signe)
    else:
        twar=twa     
    return twar    



def opti2(twa, tws,tab_twa , tab_tws  ,polaires):
    '''Optimise la twa lorsqu elle est autour des valeurs de vmgmax'''
    ''' entree une twa et une tws'''
    ''' sortie la twa optimisee si pas proche de 3  ---'''
    twamax,vmgmax,twamin,vmgmin,twaspeedmax,speedmax=vmgmaxspeed(tws,tab_twa , tab_tws  ,polaires)
    #print (twamax,vmgmax,twamin,vmgmin,twaspeedmax,speedmax)
    signe=twa/(abs(twa)+0.0001)
    if abs(twa)-twamax<3:
        twar=round((twamax*signe),1)
    elif abs(abs(twa)-twamin)<3:
        twar=round((twamin*signe),1)

    elif   abs(abs(twa)-twaspeedmax)<2: 
        twar=round((twaspeedmax*signe),1)
    #bannissement des valeurs hors laylines    
    elif abs(twa)<twamax:
        twar=twamax*signe
    elif abs(twa)>twamin:
        twar=round((twamin*signe),1)
    else:
        twar=0     
    return twar    



def prevision0(tig, GR, tp, latitude, longitude):
    ''' Barbare mais  1/20eme du temps de regulargridinterpolator !! '''
    ''' Attention Cette version utilise les coordonnees folium'''
    itemp = (tp - tig) / 3600 / 3
    ilati = 90-latitude
    ilong = (longitude) % 360
    iitemp=math.floor(itemp)
    iilati=math.floor(ilati)
    iilong=math.floor(ilong)

    v000=GR[iitemp][iilati][iilong]
    v010=GR[iitemp][iilati+1][iilong]
    v001=GR[iitemp][iilati][iilong+1]
    v011=GR[iitemp][iilati+1][iilong+1]
    
    v100=GR[iitemp+1][iilati][iilong]
    v110=GR[iitemp+1][iilati+1][iilong]
    v101=GR[iitemp+1][iilati][iilong+1]
    v111=GR[iitemp+1][iilati+1][iilong+1]
    
  
    ditemp=itemp%1
    dilati=ilati%1
    dilong=ilong%1

    # le deuxieme indice est la latitude le troisieme la longitude
    v0x0=v000+dilati*(v010-v000)
    v0x1=v001+dilati*(v011-v001)
    v0xx=v0x0+dilong*(v0x1-v0x0)

  
    v1x0=v100+dilati*(v110-v100)
    v1x1=v101+dilati*(v111-v101)
    v1xx=v1x0+dilong*(v1x1-v1x0)


    #interpolation finale entre les deux valeurs temporelles
    vxxx=v0xx+ditemp*(v1xx-v0xx)   
    
    vit_vent_n = np.abs(vxxx) * 1.94384
    #minoration a 2 de la vitesse des vents
    #vit_vent_n[vit_vent_n<2] = 2

    angle_vent = (270 - np.angle(vxxx, deg=True)) % 360
    return vit_vent_n, angle_vent    


def prevision7(tig, GR, tp, latitude, longitude):

    ''' Cette fonction est destinée à simuler le calcul de zezo en js '''
    itemp = (tp - tig) / 3600 / 3
    ilati = 90-latitude
    ilong = (longitude) % 360
    iitemp=math.floor(itemp)
    iilati=math.floor(ilati)
    iilong=math.floor(ilong)

    v000=GR[iitemp][iilati][iilong]
    v010=GR[iitemp][iilati+1][iilong]
    v001=GR[iitemp][iilati][iilong+1]
    v011=GR[iitemp][iilati+1][iilong+1]

    ditemp=itemp%1
    dilati=ilati%1
    dilong=ilong%1

    # notation zezo
    x= dilati
    y =dilong


    print ('valeur de v000 {}'.format (v000))
    print ('test extraction partie reelle     composante u pour lat0lng0  {}'.format (v000.real))
    print ('test extraction partie imaginaire composante v pour lat0lng0  {}'.format (v000.imag))



    u1=[v010.real,v011.real,v000.real,v001.real]      # ce tableau recoit les valeurs de u pour le temps 1 soit iitemp
    v1=[v010.imag,v011.imag,v000.imag,v001.imag]      # ce tableau recoit les valeurs de v pour le temps 1 
    # premier terme lon0 lat1  v010
    # deuxieme      lon1 lat1  v011
    # troisieme     lon0 lat0  v000
    # quatrieme     lon1 lat0  v001
 
    print ('valeur de u1 : {}'.format (u1))
    print ('valeur de v1 : {}'.format (v1))
    
    print()


    u2=[0,0,0,0]      # ce tableau recoit les valeurs de u pour le temps 2 
    v2=[0,0,0,0]      # ce tableau recoit les valeurs de v pour le temps 2 
    # premier terme lon0 lat1
    # deuxieme      lon1 lat1 
    # troisieme     lon0 lat0
    # quatrieme     lon1 lat0



    return None 


def extraction(tig, GR, tp, latitude, longitude):

    itemp = (tp - tig) / 3600 / 3
    ilati = 90-latitude
    ilong = (longitude) % 360
    iitemp=math.floor(itemp)
    iilati=math.floor(ilati)
    iilong=math.floor(ilong)

    v000=GR[iitemp][iilati][iilong]
    v010=GR[iitemp][iilati+1][iilong]
    v001=GR[iitemp][iilati][iilong+1]
    v011=GR[iitemp][iilati+1][iilong+1]
    
    v100=GR[iitemp+1][iilati][iilong]
    v110=GR[iitemp+1][iilati+1][iilong]
    v101=GR[iitemp+1][iilati][iilong+1]
    v111=GR[iitemp+1][iilati+1][iilong+1]

    u1=[v010.real,v011.real,v000.real,v001.real]      # ce tableau recoit les valeurs de u pour le temps 1 soit iitemp
    v1=[v010.imag,v011.imag,v000.imag,v001.imag]      # ce tableau recoit les valeurs de v pour le temps 1 
    u2=[v110.real,v111.real,v100.real,v101.real]      # ce tableau recoit les valeurs de u pour le temps 1 soit iitemp
    v2=[v110.imag,v111.imag,v100.imag,v101.imag]      # ce tableau recoit les valeurs de v pour le temps 1 

    return u1,v1,u2,v2

def uv2ds(u,v):
    ''' fonction destinée à reproduire la fonction correpondante de zezo'''

    # angle1 = math.atan2(v,u)*180 /math.pi
    # angle= (450 -angle1)%360        # verifié
    #angle_vent = (270 - np.angle(vxxx, deg=True)) % 360      avec np array sans inversion uv 
    angle = (math.atan2(u,v)*180 /math.pi)%360       # verifie 
      
    return angle

def prevision8(tig, GR, tp, latitude, longitude):
    ''' Cette fonction est destinée à simuler le calcul de zezo en js '''
    
    
    itemp = (tp+1 - tig) / 3600 / 3   # le +1s est pour les erreurs d'arrondi 
    ilati = 90-latitude
    ilong = (longitude) % 360
    iitemp=math.floor(itemp)
    iilati=math.floor(ilati)
    iilong=math.floor(ilong)
    wu=[0,0,0,0]
    wv=[0,0,0,0]
    s= [0,0,0,0]
    d= [0,0,0,0]

    # a l 'indice de temps t
    v000=GR[iitemp][iilati][iilong]
    v010=GR[iitemp][iilati+1][iilong]
    v001=GR[iitemp][iilati][iilong+1]
    v011=GR[iitemp][iilati+1][iilong+1]

    # a l indice de temps +1
    v100=GR[iitemp+1][iilati][iilong]
    v110=GR[iitemp+1][iilati+1][iilong]
    v101=GR[iitemp+1][iilati][iilong+1]
    v111=GR[iitemp+1][iilati+1][iilong+1]

    ditemp=itemp%1
    dilati=ilati%1
    dilong=ilong%1

    # notation zezo
    y= dilati
    x =dilong
    lon1=iilong
    lat1=iilati
    fraction=math.floor(ditemp*18)/18

    print()
    print ('indice latitude      ',ilati)
    print ('indice longitude     ',ilong)
    print ('lat1                 ',lat1)
    print ('lon1                 ',lon1)
    print ('x                    ',x)
    print ('y                    ',y)

    print ('indice temps         ',itemp)
    print ('fraction 3h          ',ditemp)
    print ('fraction 3h arrondie ',fraction)

    # print()
    # print ('valeur de v010 {}'.format (v010))
    # print ('valeur de v011 {}'.format (v011))
    # print ('valeur de v000 {}'.format (v000))    
    # print ('valeur de v001 {}'.format (v001))
    # print()
    
    
    # print ('test extraction partie reelle     composante u pour lat0lng0  {}'.format (v000.real))
    # print ('test extraction partie imaginaire composante v pour lat0lng0  {}'.format (v000.imag))



    u1=[v010.real,v011.real,v000.real,v001.real]      # ce tableau recoit les valeurs de u pour le temps 1 soit iitemp
    v1=[v010.imag,v011.imag,v000.imag,v001.imag]      # ce tableau recoit les valeurs de v pour le temps 1 
    u2=[v110.real,v111.real,v100.real,v101.real]      # ce tableau recoit les valeurs de u pour le temps 1 soit iitemp
    v2=[v110.imag,v111.imag,v100.imag,v101.imag]      # ce tableau recoit les valeurs de v pour le temps 1 
   
   
    # premier terme lon0 lat1  v010
    # deuxieme      lon1 lat1  v011
    # troisieme     lon0 lat0  v000
    # quatrieme     lon1 lat0  v001
 
    print ('valeur de u1 : {}'.format (u1))
    print ('valeur de v1 : {}'.format (v1))
    print ('valeur de u2 : {}'.format (u2))
    print ('valeur de v2 : {}'.format (v2))
    print()

    # premiere interpolation sur le temps  NB pourrait etre faite avec du np.array sans boucle 
  
    for i in range (4):
        wu[i] =  u1[i] * (1.0-fraction) + u2[i] * fraction
        wv[i] =  v1[i] * (1.0-fraction) + v2[i] * fraction
        s[i]  =   (wu[i]**2 +wv[i]**2)**0.5
        d[i]  =   uv2ds(wu[i],wv[i])+180

    print()
    print('wu',wu)
    print('wv',wv)
    print('s',s)
    print('d',d)
    print()

    u = (wu[1]+wu[2]-wu[0]-wu[3])*x*y + (wu[3]-wu[2])*x + (wu[0]-wu[2]) * y + wu[2]    #interpolation bilinaire sur u   au temps interpole 
    v = (wv[1]+wv[2]-wv[0]-wv[3])*x*y + (wv[3]-wv[2])*x + (wv[0]-wv[2]) * y + wv[2]    # interpolation bilinaire sur v

    print('u : ',u)
    print('v : ',v)
    print()
  
    speed_s = (s[1]+s[2]-s[0]-s[3])*x*y + (s[3]-s[2])*x + (s[0]-s[2]) * y + s[2]
    speed_uv= math.sqrt(u*u + v*v )
    print ('speed_s ', speed_s) 
    print ('speed_uv', speed_uv)

    print()
    # ut=[0,1,1,1,0,-1,-1,-1,]
    # vt=[1,1,0,-1,-1,-1,0,1]

    # res= uv2d(ut,vt)
    # print ('res',res)

    #angle_vent = (270 - np.angle(vxxx, deg=True)) % 360
    angle_vent = 1000
    return speed_s, angle_vent    

def foil(ttwa,ttws,speedRatio,twaMin,twaMax,twaMerge,twsMin,twsMax,twsMerge):
    '''calcule le coeff des foils en fonction de la twa et tws'''
    if ((ttwa>twaMin-twaMerge)and(ttwa<twaMax+twaMerge)and(ttws>twsMin-twsMerge)and(ttws<twsMax+twsMerge)):
        if (ttwa>twaMin-twaMerge) and (ttwa<(twaMin)):
            coeff1=(ttwa-twaMin+twaMerge)/twaMerge
        else :
            coeff1=1
        if (ttwa>(twaMax)) and (ttwa<(twaMax+twaMerge)):
            coeff2=(ttwa-twaMax)/twaMerge
        else :
            coeff2=1  
        if (ttws>twsMin-twsMerge) and (ttws<(twsMin)):
            coeff3=(ttws-twsMin+twsMerge)/twsMerge
        else :
            coeff3=1  
        if (ttws>(twsMax)) and (ttws<(twsMax+twsMerge)):
            coeff4=(ttws-twsMax)/twsMerge
        else :
            coeff4=1  

        # print ('coeffs',coeff1,coeff2,coeff3,coeff4)    
        coeff=1+(speedRatio-1)*coeff1*coeff2*coeff3*coeff4
    else :
        coeff=1    
    #print ('Coeff  foils : ',coeff )
    return coeff




def recupere_polaires(bateau ,nom_fichier):

    with open(nom_fichier, 'r') as fichier:
        data2 = json.load(fichier)                  # ca c'est le json complet avec tous les bateaux
        polairesjson=data2[bateau]                          # ca c'est le fichier json pour le bateau uniquement
    #bateau="mono/imoca_60_foils"

    tabtws= np.asarray(data2[bateau]['polar']['tws'])                                            
    tabtwa= np.asarray(data2[bateau]['polar']['twa'])
    l1=data2[bateau]['polar']['tws']
    l2=data2[bateau]['polar']['twa']
    bateau=(data2[bateau]['polar']['label'])
    # print('\nbateau',bateau)
    # print ('tabtws', tabtws)  
    # print('tabtwa',tabtwa)     
    # print ('data2',data2[bateau]['polar']['sail'])
    nbtws=len(tabtws)
    nbtwa=len(tabtwa)
    nb= len(data2[bateau]['polar']['sail'])
    voile=[]
    toutespolaires=np.zeros((nbtwa,nbtws,nb))
    for i in range(nb) :
        voile.append( data2[bateau]['polar']['sail'][i]['name'])
        toutespolaires[:,:,i]= data2[bateau]['polar']['sail'][i]['speed']
    speedRatio=data2[bateau]['polar']['foil']['speedRatio']
    twaMin=data2[bateau]['polar']['foil']['twaMin']
    twaMax=data2[bateau]['polar']['foil']['twaMax']
    twaMerge=data2[bateau]['polar']['foil']['twaMerge']
    twsMin=data2[bateau]['polar']['foil']['twsMin']
    twsMax=data2[bateau]['polar']['foil']['twsMax']
    twsMerge=data2[bateau]['polar']['foil']['twsMerge']
    hull=data2[bateau]['polar']['hull']['speedRatio']
    toutespolaires=np.zeros((nbtwa,nbtws,nb)) # initialisation d'un numpy array
    voile=[]
    for i in range(nb) :                     # constitution du fichier global de polaires brutes
        voile.append( data2[bateau]['polar']['sail'][i]['name'])
        toutespolaires[:,:,i]= data2[bateau]['polar']['sail'][i]['speed']
    polairesmax=np.amax(toutespolaires,axis=2) 
    polairesnp=np.copy(polairesmax) # initialisation d'un tableau pour les polaires avec le coef foils
    #print ('shape de polaires',polairesnp.shape)
    #print ('shape de nbtws',nbtws)


    for i in range (nbtwa):
        for j in range (nbtws):    
            #     polaire[i,j]=np.around(polairesmax[i,j])
            polairesnp[i,j]=np.around(polairesmax[i,j]*foil(tabtwa[i],tabtws[j],speedRatio,twaMin,twaMax,twaMerge,twsMin,twsMax,twsMerge)*hull,decimals=3)
    
    #print ('polairesnp',polairesnp)
    # transformation au format js 
    polairesjs2= [arr.tolist() for arr in polairesnp]
    #print ('Polaires Fullpack js2 ',polairesjs2)  


    return polairesnp,polairesjs2,polairesjson,l1,l2

def ccw(A,B,C):
    ''' exemple A=[45,-2] B=[45,-5] C=[44,-4] 3 points'''
    '''la fonction renvoie true si rotation anti horaire '''
    '''pente de AC est comparee a pente de AB '''
    return (C[1]-A[1])*(B[0]-A[0]) > (B[1]-A[1])*(C[0]-A[0])
    

def intersect (A,B,C,D): 
    ''' verifie si  AB et CD sont sequents en comparant les sens de rotation  dans les triangles '''    
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)


