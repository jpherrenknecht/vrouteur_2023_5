import csv
import json
import math
import os
import sys
import time
import urllib.parse  # pour decoder url
import uuid
import webbrowser
from datetime import datetime
from pathlib import Path

import folium
#import h5py
import numpy as np
import requests
import xarray as xr
from flask import (Flask, flash, jsonify, redirect, render_template, request,
                   session, url_for)
from global_land_mask import globe
from shapely.geometry import (LineString, MultiLineString, MultiPoint, Point,
                              Polygon)
from websocket import create_connection

from fonctions2023 import *
from fonctions2023_2 import *

app = Flask(__name__)

tic = time.time()
ticstruct = time.localtime()
utc = time.gmtime()
decalage = ticstruct[3] - utc[3]
basedir = os.path.dirname(os.path.abspath("__file__"))


# dt1 = np.ones(72) * 600
# dt2 = np.ones(370) * 3600
# # temps pour les isochrones tcumul_array[0] temps au depart tcumul_array[1] instant pour calcul isochrone 1
# tcumul_array = np.cumsum(np.concatenate(([0], dt1, dt2)))
cap_ar, m_ar, df1f2, numero_point, tmin, duree, requestidnum, numiso = 0, 0, 0, 0, 0, 0, 0, 0
tmin2=10000

carte_vr='inactif'
n2=180                                                               # nombre de caps a etudier autour de la direction de l arrivee
n3=500                                                               # nombre de points sur l isochrone
verbose=5
type_routage='normal'
lignes_exclusions='actif'

# on va chercher toutes les courses actives et les sauver dans un tableau    
polairesunit10=np.float32(np.zeros((701,1801)))
listecourses=[]
tabcourses=[]
tabcoursescomplet=[]
#polairesunit10=np.float32(np.zeros((701,1801)))
with open('static/js/courses2.json', 'r') as fichier1:
    data1 = json.load(fichier1)
    
with open('static/js/polars2.json', 'r') as fichier2:
        data2 = json.load(fichier2)    
    
for key,value in data1.items() :
    if value['active']=='oui':
        tabcourses.append(key)
        marques=[]
        coords=[]
        for k,val in value['marques'].items():
            marques.append(k)
            coords.append([val['lat'],val['lon']])
        listecourses.append(  [value['numero'],value['nom'],value['leg'],value['bateau'],value['moyenne'],marques,coords])      
        caracteristiques= (data1[key])      # on sauvera caracteristiques dans un tableau 
        bateau=data1[key]['bateau']
        if "exclusions" in data1[key]:
            fichierexclusions=(data1[key]["exclusions"])
            nom_fichier=basedir+'/static/txt'+fichierexclusions
            try:
                with open(nom_fichier, "r") as fichier:
                    exclusions=fichier.read()                                           
                    exclusions = eval (exclusions)
            except:
                pass
        else    :
            exclusions='non'
        tabmarques=[]                                             # on va transformer la liste des marques en un tableau
        for nom,marque  in caracteristiques['marques'].items():        # les noms sont les cles et les marques les valeurs du dictionnaire data2['4705']['marques']
            yn,xn=(marque['lat'],marque['lon'])
            tabmarques.append([nom,yn,xn])
            
        polairesjson   = data2[bateau]                          # ca c'est le fichier json pour le bateau uniquement
        tabtws        = np.asarray(data2[bateau]['polar']['tws'])                                            
        tabtwa        = np.asarray(data2[bateau]['polar']['twa'])
        nbtws          = len(tabtws)
        nbtwa          = len(tabtwa)
        bateau         = (data2[bateau]['polar']['label'])
        nbvoiles       = len(data2[bateau]['polar']['sail'])
        typevoile          = []
        toutespolaires = np.zeros((nbtwa,nbtws,nbvoiles))
        for i in range(nbvoiles) :
            typevoile.append( data2[bateau]['polar']['sail'][i]['name'])
            toutespolaires[:,:,i]= data2[bateau]['polar']['sail'][i]['speed']
            polairesmax=np.amax(toutespolaires,axis=2) 
        speedRatio         = data2[bateau]['polar']['foil']['speedRatio']
        twaMin             = data2[bateau]['polar']['foil']['twaMin']
        twaMax             = data2[bateau]['polar']['foil']['twaMax']
        twaMerge           = data2[bateau]['polar']['foil']['twaMerge']
        twsMin             = data2[bateau]['polar']['foil']['twsMin']
        twsMax             = data2[bateau]['polar']['foil']['twsMax']
        twsMerge           = data2[bateau]['polar']['foil']['twsMerge']
        hull               = data2[bateau]['polar']['hull']['speedRatio']
        lws                = data2[bateau]['polar']['winch']['lws']
        hws                = data2[bateau]['polar']['winch']['hws']
        lwtimer            = data2[bateau]['polar']['winch']['sailChange']['pro']['lw']['timer']
        hwtimer            = data2[bateau]['polar']['winch']['sailChange']['pro']['hw']['timer']
        lwratio            = data2[bateau]['polar']['winch']['sailChange']['pro']['lw']['ratio']
        hwratio            = data2[bateau]['polar']['winch']['sailChange']['pro']['hw']['ratio']
        tackprolwtimer     = data2[bateau]['polar']['winch']['tack']['pro']['lw']['timer']
        tackprolwratio     = data2[bateau]['polar']['winch']['tack']['pro']['lw']['ratio']
        tackprohwtimer     = data2[bateau]['polar']['winch']['tack']['pro']['hw']['timer']
        tackprohwratio     = data2[bateau]['polar']['winch']['tack']['pro']['hw']['ratio']
        gybeprolwtimer     = data2[bateau]['polar']['winch']['gybe']['pro']['lw']['timer']
        gybeprolwratio     = data2[bateau]['polar']['winch']['gybe']['pro']['lw']['ratio']
        gybeprohwtimer     = data2[bateau]['polar']['winch']['gybe']['pro']['hw']['timer']
        gybeprohwratio     = data2[bateau]['polar']['winch']['gybe']['pro']['hw']['ratio']
        polairesnp=np.copy(polairesmax) # initialisation d'un tableau pour les polaires avec le coef foils
        for i in range (nbtwa):
            for j in range (nbtws):    
                #     polaire[i,j]=np.around(polairesmax[i,j])
                polairesnp[i,j]=np.around(polairesmax[i,j]*foil(tabtwa[i],tabtws[j],speedRatio,twaMin,twaMax,twaMerge,twsMin,twsMax,twsMerge)*hull,decimals=3)
        polairesjs=[arr.tolist() for arr in polairesnp]          
        polairesunit=np.float32(np.zeros((72,181)))
        for i in range (71):                           # creation de polaireunit a laide de polairevecttwa
            polairesunit[i]=polaire_vect_twa(polairesnp,tabtwa,tabtws,np.ones(181)*i,np.arange(0,181).reshape(-1,1))
        polairesunit[71]=polairesunit[70]    
        tabvmg             = ftabvmg(tabtws,tabtwa,polairesnp)
             
        tabcoursescomplet.append([key,caracteristiques,tabmarques,polairesjson,polairesnp,polairesjs,tabtws,tabtwa,tabvmg,polairesunit,exclusions])      
        
        


def recherchecourse(course,tabcoursescomplet):
    for i in range (len(tabcourses)):
        if tabcoursescomplet[i][0]== course:
            break
    course           = tabcoursescomplet[i][0]
    caracteristiques = tabcoursescomplet[i][1] 
    tabmarques       = tabcoursescomplet[i][2] 
    polairesjson     = tabcoursescomplet[i][3]  
    polairesnp       = tabcoursescomplet[i][4]   # polaires numpy fullpack et foils
    polairesjs       = tabcoursescomplet[i][5]
    tabtws           = tabcoursescomplet[i][6] 
    tabtwa           = tabcoursescomplet[i][7] 
    tabvmg           = tabcoursescomplet[i][8]
    polairesunit     = tabcoursescomplet[i][9]
    exclusions       = tabcoursescomplet[i][10]
    return course,caracteristiques,tabmarques,polairesjson,polairesnp,polairesjs,tabtws,tabtwa,tabvmg,polairesunit,exclusions







#################################################################################################################
# Chargement des gribs
#################################################################################################################



##############################################################################################################################    
#          Fonctions detaillees  de routage     
##############################################################################################################################   


def routag(chemincomplet,t0 ,polaires,typegrib):
    '''Transforme le chemincomplet en routage'''
  
    
    # on arrondit les twaos"
    chemincomplet[:,7]=np.round(chemincomplet[:,7])
    routage=np.zeros((len(chemincomplet),10) )   # Initialisation : n,y,x,t,tws,twd,cap,twa,vitesse 
    y0,x0,t0_decale=chemincomplet[0,1],chemincomplet[0,2],chemincomplet[0,3]   # recalcul du chemincomplet de base avec les twas arrondies
    t_c  =  chemincomplet[:,3]
    #optimisation des twas    (facultatif)
    # for i in range (len(twaopti)):
    #     chemincomplet[i,7]=np.round(opti(chemincomplet[i,7],chemincomplet[i,4]))  #optimisation avec les polaires 
    # elimination des petites variations    
    for i in range (len (chemincomplet)-2):        #on evite les variations x - x   sur la twa ne sert a rien si pas arrondi
        if chemincomplet[i+2][7]==chemincomplet[i][7]:
            if chemincomplet[i+1][7]!=chemincomplet[i][7]:
                chemincomplet[i+1][7]=chemincomplet[i][7]    
    twas =  chemincomplet[:,7]
  
    twa0=chemincomplet[0,7]
    tws0=chemincomplet[0,4]
    twaopti=np.round(opti2(twa0,tws0,tabtwa , tabtws  ,polaires),1) 
    speedini=vit_polaires(polairesunit,tws0,twa0)
    routage[0]=chemincomplet[0,0:10]
    routage[0,8]=speedini
    routage[0,9]=twaopti
    y,x=y0,x0
    for i in range (len(chemincomplet)-1):
            t=t_c[i] 
            if typegrib=='gfs':
                tws,twd= prevision5(tig, GR, t, y, x)
            if typegrib=='gefs':
                tws,twd= previsiongefs(tigGEFS, GRGEFS, t, y, x)
            if tws<2:
                tws=2
            twao=twas[i]
            cap=fcap(twao,twd)         
            dt=t_c[i+1]-t_c[i]  
            vit=polaire_simple2(abs(twao),  tws, polairesunit)
            yp=y+vit*dt/3600/60*math.cos(cap*math.pi/180)
            xp=x+vit*dt/3600/60*math.sin(cap*math.pi/180)/math.cos(y*math.pi/180)
            twaopti=np.round(opti2(twao,tws,tabtwa , tabtws  ,polaires),1)  #optimisation avec les polaires          
            routage[i+1]=[i+1,yp,xp,t,tws,twd,cap,twao,vit,twaopti]
            y,x=yp,xp
    routage[:,4]=np.round(routage[:,4],1)
    routage[:,5]=np.round(routage[:,5],0)
    routage[:,6]=np.round(routage[:,6],0)
    routage[:,8]=np.round(routage[:,8],1)

    # on rassemble les occurences
    routage=routage[np.where( np.insert(np.diff(routage[:,7]),0,1,axis=0) !=0)]          
    
    return routage



def f_route (y0,x0,y1,x1,isoglobal,numero_point):
    ''' calcule la route a partir du tableau general des points et du dernier point le plus pres '''
    ''' utilise un dictionnaire pour remonter le chemin'''
    ''' retourne un tableau des points '''
    
    tabpoints= isoglobal[:,3:5]    
    tabpoints=(tabpoints[np.where(tabpoints[:,1]!=0)]).astype (int)
    dico= dict(zip(tabpoints[:,1],tabpoints[:,0]))  # creation du  dictionnaire de tous les points meres 
   
    #utilisation du dictionnaire
    a=numero_point                                   # numero dernier point
    route2 = [a]                                     # initialisation avec l'indice du point le plus pres dans le dernier isochrone
    while a!=0:
        a = int(dico[a])
        route2.append(a)  # route contient les indices successifs des points a emprunter a l'envers
    route2.reverse()  
  
    chemin=np.zeros((len(route2)+1,2))               # on initialise
    i=0
    for n in route2:                                 # on reconstitue le tableau des points a partir 
        chemin[i]=isoglobal[n,0],isoglobal[n,1]
        i+=1
    chemin[i] =[y1,x1]                              # on rajoute l'arrivee -- chemin est le tableau des points de l itineraire a suivre 
   
    return chemin


def detail(chemin,y1,x1,t0,typegrib):
    ''' Reconstitue le detail du chemin en partant des coordonnees X et Y des differents points donnés par chemin '''
    #print('ligne 254 duree',duree)  
    global tcumul_array
    tcumul_array.append(duree)
    imax=len(chemin)
    numero= np.arange(imax).reshape(-1,1)
    #T=(t_c[:imax]+t0).reshape(-1,1)
    tcumul_array=np.array(tcumul_array)
    #print('tcumul_array',tcumul_array)

    T=(tcumul_array+t0)       #tableau de tous les temps cumules 
    #print ('T.shape',T.shape)
    #print('T',T)

   
    if typegrib=='gfs':
        tws,twd       = previsiontab    (tig    ,GR     ,T,chemin[:,0],chemin[:,1])
    if typegrib=='gefs':
        tws,twd       = previsiontabgefs(tigGEFS, GRGEFS,T,chemin[:,0],chemin[:,1])
    
    tabcap        = np.mod(360+np.arctan2( np.diff(chemin[:,1]) , np.diff(chemin[:,0])/ np.cos(chemin[0:-1,0] *math.pi/180)) *180/math.pi,360)
    tabcap        = np.append(tabcap,0)
    twaos         = ftwao( tabcap,twd)                           # calcul des twa orientes sur tous les chemins 
    
    vitesses      = vit_polaires(polairesunit,tws,twaos)

    tabcap        = tabcap.reshape(-1,1)
    tws           = tws.reshape(-1,1)
    twd           = twd.reshape(-1,1)
    twaos         = twaos.reshape(-1,1)
    vitesses      = vitesses.reshape(-1,1)
    arrivee       = np.array([y1,x1])
    a             = chemin[:,0:2]-arrivee                                    # Elimination par cercle de coordonnees np.array (centre )
    D             = np.sqrt(np.einsum('ij,ij->i', a, a))                    # distance de tous les points a l arrivee en degres de latitude 
    D             = D.reshape(-1,1)  
    chemincomplet = np.concatenate((numero,chemin,T.reshape(-1,1),tws,twd,tabcap,twaos,vitesses,D),axis=1)
    tabtwslocal   = chemincomplet[:,4]
    tabtwalocal   = chemincomplet[:,7]
  
    tabtwalocal   = opti_twa(tabtwslocal,tabtwalocal,tabtwa,tabtws,polaires)     
    chemincomplet = np.concatenate((chemincomplet[:,:8],tabtwalocal.reshape(-1,1), chemincomplet[:,8:]),axis=1)
    chemincomplet[-1][7:9]=0                     #derniere vitesse  et distance ? egale a 0

    return chemincomplet  

   

def exploitation_routage(y0,x0,t0,y1,x1,isoglobal,tmin,numero_point,typegrib):
    ''' a partir de isoglobal et du numero du dernier point '''
    ''' retourne la route suivie et decoupe les isochrones ''' 
    # print('on est dans l exploitation du routage')
    chemin  = f_route(y0,x0,y1,x1,isoglobal,numero_point) 
   
    chemincomplet   = detail(chemin,y1,x1,t0,typegrib)
    
    noir            = isoglobal[np.where(isoglobal[:,2]%6!=0) ]                                      # on garde que les isochrones non modulo6 
    coupuresnoir1   = np.where(np.diff(noir[:,2],1) >0)                              # coupure suivant les numeros d iso 
    coupuresnoir2   = np.where(np.diff(noir[:,5],1) >1)                              # coupure suivant la numerotation dans les isos
    coupuresnoir    = np.asarray(sorted(list(set(coupuresnoir1[0])|set(coupuresnoir2[0]))))  # on combine les 2 sets on transforme en liste, on trie et on transforme en np
    noir            = np.split(noir[:,0:2],coupuresnoir+1)                                           # coupure suivant le numero d'isochrone nparray
    noir            = [arr.tolist() for arr in noir] 
    
    blanc           = isoglobal[np.where(isoglobal[:,2]%6==0) ]                                        # on garde que les isochrones modulo6 
    coupuresblanc1  = np.where(np.diff(blanc[:,2],1) >0)
    coupuresblanc2  = np.where(np.diff(blanc[:,5],1) >1)                               # c donne la position des coupures sur les isochrones
    coupuresblanc   = np.asarray(sorted(list(set(coupuresblanc1[0])|set(coupuresblanc2[0]))))  # on combine les 2 sets on transforme en liste, on trie et on transforme en np
    blanc           = np.split(blanc[:,0:2],coupuresblanc+1)                                           # coupure suivant le numero d'isochrone nparray
    blanc           = [arr.tolist() for arr in blanc] 
    

  # determination des isochrones de mise a jour

    tic=round(time.time())
    ticstruct = time.localtime()
    utc = time.gmtime()
    decalage = ticstruct[3] - utc[3]  #en h
    sec_utc=tic-decalage*3600
    h00 = time.mktime(datetime(utc[0], utc[1], utc[2], 0, 0, 0).timetuple())        #heure 0 du jour en UTC
    heuresmaj = [h00+14400, h00+36000, h00 + 57600, h00+79200, h00+86400, h00+100800]  #mises a jour grib 4, 10,16,22h UTC
    indiceh = recherche(sec_utc, heuresmaj)   #indiceh donne la prochaine mise a jour 
    majprochaine=heuresmaj [indiceh]
    try:
        n1_maj=recherche(majprochaine-sec_utc, tcumul_array     )-1# indice de l isochrone concerne par la future mise a jour 
    except:
        n1_maj=0
    try:    
        n2_maj=recherche(majprochaine-sec_utc+21600,tcumul_array)# indice de l isochrone concerne par la future mise a jour +1
    except:
        n2_maj=0
    rouge            = isoglobal[np.where(isoglobal[:,2]==n1_maj) ] 
    # coupuresrouge    = np.where(np.diff(rouge[:,5],1) >1)
    # rouge            = np.split(rouge[:,0:2],coupuresrouge+1) 
    rouge            = rouge[:,0:2]
    rouge            = [arr.tolist() for arr in rouge] 

    rouge2            = isoglobal[np.where(isoglobal[:,2]==n2_maj) ] 
    # coupuresrouge    = np.where(np.diff(rouge[:,5],1) >1)
    # rouge            = np.split(rouge[:,0:2],coupuresrouge+1) 
    rouge2            = rouge2[:,0:2]
    rouge2            = [arr.tolist() for arr in rouge2] 
    return chemincomplet,noir,blanc,rouge,rouge2



 
    
def plus_pres(isocreme,y1,x1,t0):
    ''' Determine le N° du point le plus pres de l'arrivee et le temps vers l'arrivee y1 x1 '''
    latsfinales   = isocreme[: ,0]            # latitudes des points apres ecremages 
    lngsfinales   = isocreme[: ,1]
    nptsfinales   = isocreme[: ,4]            # numero de ces points servira pour determiner le point le plus pres 
   # distarfinales = isocreme[: ,5]
    twsfinales    = isocreme[: ,8]            # latitudes et longitudes des ~300 points d'arrivee apres nettoyage des terres 
    twdfinales    = isocreme[: ,9]
    twsfinales[twsfinales>70]   =70
  
    caparfinales=(450-np.arctan2(y1-latsfinales,x1-lngsfinales)*180/math.pi)%360  # cap  vers arrivee du point
    twaos=ftwao( caparfinales,twdfinales)
    vitessesfinales      = vit_polaires(polairesunit,twsfinales,twaos)
    dy=latsfinales-y1
    T=np.abs(dy*3600*60/np.cos(caparfinales*math.pi/180)/vitessesfinales)
    tmin=np.min(T)
    numero_ordre=np.argmin(T,axis=0)
    numero_point=int(nptsfinales[numero_ordre])     # numero du point le plus proche de l arrivee 
    numero_dernier_isochrone=int(isocreme[-1 ,2])
    temps_dernier_isochrone= t_c[numero_dernier_isochrone]+t0   
    return tmin,numero_point





def f_isochrone(num_iso_ini,numiso,dt,cumuldt,tmin,x0,y0,t0,y1,x1,range_caps,n2,m_ar,centre,rayon,isocreme,typegrib):
    global isobrut
    ''' isobrut est utilise comme  reservoir pour les calculs de points provisoires '''
    ''' isocreme est l'isochrone des point precedents avec tws et twd '''
    #print('numiso, num_iso_ini',numiso ,num_iso_ini)
    if numiso==num_iso_ini:                                         # je garde l integralite de l isochrone
        tmin=10000
        numero_point=90     
        T2=np.ones(1)                                        # numero de point sert a conserver le numero de point du tmin
        print('Calcul des isochrones en cours avec grib', typegrib)
       # dt         = tcumul_array[1]-tcumul_array[0]
        tws,twd    = isocreme[0,  8:10]

        #tws,twd  = prevision5    (tig    ,GR     ,t0,x0,y0)     # meteo sur le point de depart
        caps       = np.tile(range_caps,1)                           # on repete la sequence autant que de fois le nombre de points en entree
        twds       = np.ones(n2)*twd                                 # on repete la sequence autant que de fois le nombre de caps
        twss       = np.ones(n2)*tws                                 # on repete la sequence autant que de fois le nombre de caps
        latss      = np.ones(n2)*y0                                  # on repete la sequence autant que de fois le nombre de caps
        lngss      = np.ones(n2)*x0                                  # on repete la sequence autant que de fois le nombre de caps
        nptsm      = np.ones(n2)*num_iso_ini   
        #on repete la sequence autant que de fois le nombre de caps
        # twats      = np.ones(n2)*twa_ant                             # on repete la sequence autant que de fois le nombre de caps
        twaos      = ftwao( caps,twds).reshape(-1,1)                 # calcul des twa orientees sur tous les chemins  
        # print(twaos)
        # print(twss)
        vitesses      =vit_polaires(polairesunit,twss,twaos)
      
        kpeno=0
        # penalite   = np.ravel((twaos*twa_ant<0)*dt*kpeno)            # tableau des penalites pour virement de bord ou empannage (150s) volontairement limite a 120 pour la premiere afin de ne pas avoir de marchae arriere        
        penalite=0
        dT         = (np.ones(n2))*dt  - penalite
       
        
                                                          # calcul des vitesses
        latsf      = (latss+vitesses*dT/3600/60*np.cos(caps*math.pi/180) ).reshape(-1,1)                                           # latitude après deplacement
        lngsf      = (lngss+vitesses*dT/3600/60*np.sin(caps*math.pi/180)/np.cos(latss*math.pi/180)  ).reshape(-1,1)                # longitude après deplacement 
        distar     = ((latsf-y1)**2 +(lngsf-x1)**2)**.5                                                                            # inutile ppour le premier iso    
        ordoar     = latsf-m_ar*lngsf 
        nsiso      = np.ones(n2).reshape(-1,1)                            # numero isochrone
        npoint     = np.arange(1,n2+1).reshape(-1,1)                      # numero de point   
        nptsm      = num_iso_ini*np.ones(n2).reshape(-1,1)   
        numdsiso   = (np.arange(n2)+1).reshape(-1,1) 

        t_iso2      =t0
        #t_iso2     =  float( tcumul_array[numiso+1]+t0 )  
        
        
        # temps pour le calcul de la meteo  sur les points fina  
        if typegrib=='gfs': 
            twsf,twdf  = previsiontab    (tig    ,GR     ,t_iso2,latsf,lngsf)     # meteo sur les points d arrivee
        if typegrib=='gefs':            
            twsf,twdf  = previsiontabgefs(tigGEFS, GRGEFS,t_iso2,latsf,lngsf)
        twsf       = twsf.reshape(-1,1)
        twdf       = twdf.reshape(-1,1)
        isocreme   = np.concatenate((latsf,lngsf,nsiso,nptsm,npoint,numdsiso,ordoar,twaos,twsf,twdf),axis=1)        # 8 elements directement isocreme
        cumuldt    = 0
        
        ######################################################################################
        # Elimination des points terre dans l'ordre globe, exclusions, carte avec securite )
        ######################################################################################
        
        isocreme      = isocreme[np.where( ~globe.is_land(isocreme[:,0],((isocreme[:,1]+180)%360)-180  ))]     # Elimination des points terre les points longitude >180 deviennent -180   
        if lignes_exclusions=='actif':
                isocreme=isocreme[np.where( point_terre(isocreme[:,0:2],exclusions)==0)]         
        if carte_vr=='actif':
            if numiso<25  :                                                                          # on ne teste que sur les 2 premieres heures dans le cas du deuxieme routage 30 fois 2 mn +6 fois 10 mn
                isocreme=isocreme[np.where( point_terre(isocreme[:,0:2],cartevr)==0)]  
        isocreme[:,4]= np.arange(1,len(isocreme)+1)                                        # on renumerote en utilisant la colonne 4 distar
     
    
    else:  
        
        #isochrones suivants
       # print('isochrones suivants sollicites')
       # dt            = tcumul_array[numiso+1]-tcumul_array[numiso]                          # temps sur lequel est calcule l isochrone
        numiso        = int( isocreme[-1,2])                               # numero de lisochrone precedent
        premier       = int( isocreme[-1,4]+1)                             # numero du premier point du nouvel isochrone
        n1            = len(isocreme)                                      # nombre de points de l isochrone precedent
        lats          = isocreme[:,0]                                      # latitudes  de tous les points au depart   
        lngs          = isocreme[:,1]                                      # longitudes de tous les points au depart 
        npoints       = isocreme[:,4]                                      # numero des points  initiaux va alimenter les points mere 
        twaas         = isocreme[:,7]                                      # twa sur les points de l'isochrone precedent
        tws           = isocreme[:,8]
        
        
        
        twd           = isocreme[:,9]
        caps          = np.tile(range_caps,n1)                         # on repete la sequence autant que de fois le nombre de points en entree
        twds          = np.ravel(np.tile(twd.reshape(-1,1),n2))        # on repete la sequence autant que de fois le nombre de caps
        twss          = np.ravel(np.tile(tws.reshape(-1,1),n2))        # on repete la sequence autant que de fois le nombre de caps
        latss         = np.ravel(np.tile(lats.reshape(-1,1),n2))       # on repete la sequence autant que de fois le nombre de caps
        lngss         = np.ravel(np.tile(lngs.reshape(-1,1),n2))       # on repete la sequence autant que de fois le nombre de caps
        nptsm         = np.ravel(np.tile(npoints.reshape(-1,1),n2))    # on repete la sequence autant que de fois le nombre de caps
        twats         = np.ravel(np.tile(twaas.reshape(-1,1),n2))      # on repete la sequence autant que de fois le nombre de caps      (twas anterieures 
      
        twaos         = ftwao( caps,twds)               # calcul des nouvelles twa orientees sur tous les chemins     pourra etre remplace par signetwa pour accelerer
        twaos         = twaos.reshape(-1,1)
        twats         = twats.reshape(-1,1)
        kpeno         = 0
        penalite      = np.ravel((np.sign(twaos)*np.sign(twats))<0*dt*kpeno)   
       # print('dt ligne 475 ',dt)                                # tableau des penalites pour virement de bord ou empannage (150s) volontairement limite a 120 pour la premiere afin de ne pas avoir de marchae arriere
        dT            = (np.ones(len(latss))*dt)-penalite                                                 # les penalites ne servent pas a grand chose
      
        # TWS10 =np.around(twss*10,0).astype(int)
        # TWA10 =np.around(np.abs(np.ravel(twaos)*10),0).astype(int)
        # vitesses=polairesunit10[TWS10,TWA10]


        #vitesses      = vit_polaires(polairesunit,twss,np.ravel(twaos))     // ancien calcul

        vitesses      = vit_polaires10(polairesunit10,twss,np.ravel(twaos))

                                     #calcul des vitesses
       
        dv=vitesses*dT/3600/60
        latsf         = latss+dv*np.cos(caps*math.pi/180)                                # latitude après deplacement
        lngsf         = lngss+dv*np.sin(caps*math.pi/180)/np.cos(latss*math.pi/180)      # longitude après deplacement 
        distar        = ((latsf-y1)**2 +(lngsf-x1)**2)**.5                                                # inutile ppour le premier iso    
        ordoar        = latsf-m_ar*lngsf 
        latsf         = latsf.reshape(-1,1)
        lngsf         = lngsf.reshape(-1,1)
        nptsm         = nptsm.reshape(-1,1)
        distar        = distar.reshape(-1,1)
        ordoar        = ordoar.reshape(-1,1)        
        isobrut       = np.concatenate((latsf,lngsf,nptsm,distar,ordoar,twaos),axis=1)                            # on constitue un tableau de tous les resultats
        
        ordomaxi      = (isobrut[np.argmax(isobrut,0)[4],4]) 
        ordomini      = (isobrut[np.argmin(isobrut,0)[4],4]) 
        coeff         = (n3-1)/ (ordomaxi-ordomini)                                                             # coefficient pour ecremer et garder n3 points
        isobrut[:,4]  = np.around(isobrut[:,4]*coeff,0)                           # La colonne 4 est multipliee par le coeff et arrondie  
      
        isobrut       = isobrut[isobrut[:,3].argsort(kind='stable')]           # On trie sur les distances 
        isobrut       = isobrut[isobrut[:,4].argsort(kind='stable')]           # On trie sur les ordonnees mais l'ordre des distances est respecté
       
       
        test          = (np.roll(np.diff(isobrut[:,4]),1))                        # ??????? il faudra que je comprenne ce que j ai fait              
        test[0]       = 1 
        isocreme      = isobrut[np.where(test !=0)]       
        a             = isocreme[:,0:2]-centre                                    # Elimination par cercle de coordonnees np.array (centre )
        D             = np.sqrt(np.einsum('ij,ij->i', a, a))
        isocreme      = isocreme[np.where(D<rayon )]  
        # if tmin>25000 :
        #     arrivee        = np.array([y1,x1])
        #     b             = isocreme[:,0:2]-arrivee   
        #     D2            = np.sqrt(np.einsum('ij,ij->i', b, b))
        #     isocreme      = isocreme[np.where(D2<2 )]  
        
        
        isocreme[:,4] = np.arange(1,len(isocreme)+1)                              # on numerote les points dans isocreme    en reutilisant la colonne 4     
        
        ######################################################################################
        # Elimination des points terre dans l'ordre globe, exclusions, carte avec securite )
        ######################################################################################
        
        isocreme      = isocreme[np.where( ~globe.is_land(isocreme[:,0],((isocreme[:,1]+180)%360)-180  ))]     # Elimination des points terre les points longitude >180 deviennent -180  


        if lignes_exclusions=='actif':
                 isocreme=isocreme[np.where( point_terre(isocreme[:,0:2],exclusions)==0)] 
                #  if (numiso<50)  :      
                #     print (point_terre(isocreme[:,0:2],exclusions))
        
       

        if (type_routage=='fin') and numiso<24  :                                                                          # on ne teste que sur les 2 premieres heures dans le cas du deuxieme routage 30 fois 2 mn +6 fois 10 mn
            isocreme=isocreme[np.where( point_terre(isocreme[:,0:2],cartevr)==0)]  
        
        ######################################################################################
        # Ajout du numero d iso du n de point et de  la meteo a l isochrone 
        ######################################################################################
        l_isocreme    = len(isocreme)    
        nsiso         = (np.ones(l_isocreme)*numiso+1).reshape(-1,1)                            # numero isochrone
        npoint        = np.arange(premier,premier+l_isocreme).reshape(-1,1)               # numerotation des points dans l isochrone en indice 5    
        t_iso2        = cumuldt+t0                                                        # temps pour l isochrone  qui vient d etre calcule numiso etant le numero de l iso precedent
        latsf         = isocreme[:,0]                                                     # latitudes des points apres ecremages 
        lngsf         = isocreme[:,1]

        if typegrib=='gfs':
            twsf,twdf     = previsiontab(tig,GR,t_iso2,latsf,lngsf) 

        t8=time.time()
        
            
            # t_iso2f =time.strftime(" %d %b %H:%M ", time.localtime(t_iso2))
        if typegrib=='gefs':
            twsf,twdf     = previsiontabgefs(tigGEFS, GRGEFS,t_iso2,latsf,lngsf)
        twsf          = twsf.reshape(-1,1)
        twdf          = twdf.reshape(-1,1)    
            
        # on constitue isocreme complet     
        isocreme      = np.concatenate((isocreme[:,:2],nsiso,isocreme[:,2].reshape(-1,1)\
                        ,npoint,isocreme[:,4].reshape(-1,1),isocreme[:,3].reshape(-1,1),isocreme[:,5].reshape(-1,1),twsf,twdf),axis=1)
        #####################################################################################
        # Calcul du temps minimum vers arrivee 
        #####################################################################################        
       
        # if tmin>25000  and cumuldt<1300000 :                                              # si tmin2 est superieur a 20000 on va extraire  5 points 
        #     ecart=int(l_isocreme/4)
        #     tab=np.arange(0,l_isocreme,ecart)
        #     selection=isocreme[tab]
        # else:
        #     selection=isocreme   
        #selection=isocreme
        latsfinales      = isocreme[: ,0]            # latitudes des points apres ecremages 
        lngsfinales      = isocreme[: ,1]
        nptsfinales      = isocreme[: ,4]            # numero de ces points servira pour determiner le point le plus pres 
        twsfinales       = isocreme[: ,8]            # latitudes et longitudes des ~300 points d'arrivee apres nettoyage des terres 
        twdfinales       = isocreme[: ,9] 
        caparfinales     = (450-np.arctan2(y1-latsfinales,x1-lngsfinales)*180/math.pi)%360  # cap  vers arrivee du point

        twaos            = ftwao( caparfinales,twdfinales)
        vitessesfinales  = vit_polaires10(polairesunit10,twsfinales,np.ravel(twaos))+0.01      # 18 06 +0.01 pour eviter une division par zero
        dy               = latsfinales-y1
        T2               = np.abs(dy*3600*60/np.cos(caparfinales*math.pi/180)/vitessesfinales)
       
        tmin             = round(np.min(T2),0)
        numero_point     = np.argmin(T2,axis=0)+premier
        t9=time.time()
        # if numiso==50:
        #     print ('t9-t8',t9-t8)
        # on va retourner un dt en fonction de numiso et de tmin  
    
        if numiso<=36     or tmin<10000:             # les 36 premiers isochrones soit 6h sont a 600 s ainsi que ceux a l arrivee 
            dt=600
        elif numiso<=108 or tmin<7200:    
            dt=1800
        else :
            dt=3600
        cumuldt += dt
        tcumul_array.append(cumuldt)
        
        # si tmin <10000 on va eliminer les points pour lesquels le test superieur a disons 3tmin
        
        if tmin<10000:
            T2=T2.reshape(-1,1)
            isocreme=np.concatenate((isocreme,T2),axis=1)
            isocreme  =isocreme[np.where(isocreme[:,10]<3*tmin)]
            npoint        = np.arange(premier,premier+len(isocreme))           # numerotation des points dans l isochrone en indice 5   
            isocreme[:,4] = npoint
            numero_point=np.argmin(isocreme[:,10],axis=0)+premier  # on cherche le nouveau numero du point le plus pres
        
        # t10=time.time()
        # if numiso==50:
        #     print ('t10-t9',t10-t9)
    
    return isocreme,tmin,numero_point,dt,cumuldt,tcumul_array






def routagexxl(y0,x0,t0,y1,x1,ari,course,typegrib):
    '''retourne les isochrones le chemin '''
    '''ainsi qu un tableau de marche a partir des donnees '''
    '''Si ari<0 c'est y1 x1 qui sont pris en compte '''
    # print(' ligne 911 Dans routage globalxx', t0 )
    global cartevr,polaires,tabtwa,tabtws,tabvmg,polairesunit,tcumul_array,duree,tmin

   
    cartevr=[]
    tcumul_array=[0]
    tmin=10000
    # tmin2=tmin
    course,caracteristiques,tabmarques,polairesjson,polairesnp,polairesjs,tabtws,tabtwa,tabvmg,polairesunit,exclusions=recherchecourse(course,tabcoursescomplet)
    if ari>0:
        noma,y1,x1=tabmarques[ari][0],tabmarques[ari][1],tabmarques[ari][2]
        
    chemincomplet,noir,blanc,rouge,rouge2,tf=routage_xl (0,t0,y0,x0,y1,x1,typegrib)
  
    # duree=tf-t0
    # j = duree // (3600 * 24)
    # h = (duree-(j*3600*24))//3600
    # mn = (duree - (j * 3600 * 24)-(h*3600))//60 
    # s=duree-(j*3600*24+h*3600+mn*60)
    # print ('\n*******************************************************************')
    # print ('\n Duree du trajet tf-t0  {:8.0f}s soit    {:2.0f}j {:2.0f}h {:2.0f}mn {:2.0f}s' .format(duree,j,h,mn,s))
    
    # try:
    #     #indexes=np.concatenate([np.arange(0,50),np.arange(-50,0)],axis=0)
    #     cartevr=chargecarte_points(chemincomplet[:,1:2])   # on charge la carte pour les 25 premiers points 
    # except: 
    #     try:
    #         indexes=np.concatenate([np.arange(0,10),np.arange(-10,0)],axis=0)
    #         cartevr=chargecarte_points(chemin[indexes])   # on charge la carte pour les 10 premiers points    
    #     except:
    #         pass
    
    duree=(tf-t0)         # duree du trajet vers l arrivee
  
    return chemincomplet,noir,blanc,rouge,rouge2,tf,duree




def routage_xl (num_iso_ini,t0,y0,x0,y1,x1,typegrib):
    ''' Effectue un routage de base suivi d une exploitation du routage'''
    ''' retourne le chemin  le chemin complet et les isochrones'''
    global numiso
    precision_arrivee=4000
    isoglobal,tmin,numiso,numero_point,dernier = routage_x(num_iso_ini,t0,y0,x0,y1,x1,precision_arrivee,typegrib)  
    chemincomplet,noir,blanc,rouge,rouge2     = exploitation_routage(y0,x0,t0,y1,x1,isoglobal,tmin,numero_point,typegrib)
  
    duree= cumuldt+tmin                        # duree totale du trajet
    tf=t0+duree
    
    if verbose>4 :
        j = duree // (3600 * 24)
        h = (duree-(j*3600*24))//3600
        mn = (duree - (j * 3600 * 24)-(h*3600))//60 
        s=duree-(j*3600*24+h*3600+mn*60)
        print ('\n*******************************************************************')
        print ('Dernier isochrone avant arrivee     \t{:6.0f}\
                \nDernier point du dernier isochrone  \t{:6.0f}\
                \nPoint le plus proche de l arrivee   \t{:6.0f}\
                \nTemps mini dernier iso vers arrivee \t{:6.0f}s\
                \nTemps cumule du trajet              \t{:6.0f}s\
                \nsoit                            {:2.0f}j {:2.0f}h {:2.0f}mn {:2.0f}s\
                \nArrivee prévue le              {}'\
               .format(numiso,dernier,numero_point,tmin,duree,j,h,mn,s,time.strftime(" %d %b %Y %H:%M:%S ", time.localtime(tf)) ))
        print ('*******************************************************************\n')
  
    return chemincomplet,noir,blanc,rouge,rouge2,tf



def routage_x(num_iso_ini,t0,y0,x0,y1,x1,precision_arrivee,typegrib):
    global points,carte_sec,cartevr,cumuldt,tcumul_array,T2
    ''' points c'est pour le tracage de l'isochrone1 cartesec pour le tracage de la carte'''
    ''' retourne isoglobal temps vers arrivee numero dernier isochrone, numero dernier point plus proche , dernier point '''
    if typegrib=='gfs':
        tws_dep,twd_dep =prevision5(tig, GR, time.time(), y0, x0)
    if typegrib=='gefs':
        tws_dep,twd_dep =previsiongefs(tigGEFS, GRGEFS, time.time(), y0, x0)
    
    print ('Au Depart t0 {} tws_dep= {:6.4f} twd_dep= {:6.4f}\n'.format(time.strftime(" %d %b %Y %H:%M:%S ", time.localtime(t0)),tws_dep,twd_dep))


    isoglobal     = np.zeros((400000,8),dtype='float32')              # tableau general des points pour 400 isochrones de 300pts =120000   contient       lat,lng,N°iso N°ptmere npt distar,ordoar twa_ant  suffisant pour 450 *300
    isocreme      = np.zeros((500,10),dtype='float32')                # tableau general des points apres ecremage 500 points max           contient       lat lng N°iso N°ptmere npt distar ordoar twa_ant tws twd)
    isoglobal[:,2]= -1 
    isoglobal[0]  = [y0,x0,0,0,0,0,0,0]  
    isocreme [0]  = [y0,x0,0,0,0,0,0,0,tws_dep,twd_dep]              # on initialise le premier isochrone 
    num_iso_ini,numiso=0,0 
    cumuldt       = 0
    tcumul_array  = [0] 
    cap_ar        = round((450-math.atan2(y1-y0,x1-x0)*180/math.pi)%360)                                             
    range_caps    = np.float32(np.mod(np.arange(cap_ar-90,cap_ar+90, 1),360))                 # range des caps a etudier sur chaque point en nombre n2 180/n2 doit etre ent
    n2            = len(range_caps)
    m_ar          = (y1-y0)/ (x1-x0)                                                                   # pente de la droite entre le depart et l'arrivee  
    centre        = np.array([(y0+y1)/2,(x0+x1)/2])
    rayon         = (((y1-y0)**2 +(x1-x0)**2)**.5 )/2*1.05
    
    tmin          = 10000    
    # i=num_iso_ini
    
 
    #######################################################################################################
    # Lancement du moteur de routage
    #######################################################################################################
    numiso=0
    t_isofutur=0
    dt=600
    precision_arrivee=dt
   
    while (tmin>precision_arrivee and t_isofutur< tgribmax):          
        tic=time.time()
        isocreme,tmin,numero_point,dt,cumuldt,tcumul_array = f_isochrone(num_iso_ini,numiso,dt,cumuldt,tmin,x0,y0,t0,y1,x1,range_caps,n2,m_ar,centre,rayon,isocreme,typegrib)
        premier                        = int( isocreme[0,4])                             # numero du premier point du nouvel isochrone
        dernier                        = int( isocreme[-1,4])                            # numero du dernier point du nouvel isochrone
        isoglobal[premier:dernier+1,:] = isocreme[:,:8]                                  # on copie dans isoglobal
     
        t_iso2 =cumuldt+t0
        t_isofutur        = cumuldt+t0+(3600*3)     # le grib est calcule avec l indice +1     
        temps_calcul      = time.time()-tic

        # print('tcumul_array',tcumul_array)
        # print('cumuldt',cumuldt)
        
        
        # t_isofuturf =time.strftime(" %d %b %H:%M ", time.localtime(t_isofutur))
        # tgribmaxf =time.strftime(" %d %b %H:%M ", time.localtime(tgribmax))
        # print ( '\n ligne 726 t_isofutur,tgribmax ' ,t_isofuturf,tgribmaxf )
        
        if verbose>4 : 
            t_iso2_formate    = time.strftime(" %d %b %H:%M ", time.localtime(t_iso2))
            print ('isochrone {:6.0f} de {:6.0f} \t a {:6.0f} \t soit {:6.0f} points,le {} dt {:6.0f} cumuldt {:6.0f} tmin {:6.0f}  tcalc {:6.3f}'\
                 .format (numiso+1,premier,dernier,len(isocreme),t_iso2_formate,dt,cumuldt,tmin,temps_calcul ) )
        else :
            print( numiso+1,end='-')
        numiso+=1   
    tcumul_array.append(cumuldt+tmin)
    isoglobal=isoglobal[np.where(isoglobal[:,2]>=0)]                    # on ne garde que la partie utile de isoglobal (on vire tous les elements 0 )
    return isoglobal,tmin,numiso,numero_point,dernier










def vents_encode(tig, GR, latini, latfin, longini, longfin):
    ''' extrait du grib GR les donnees entre ini et fin sur 24 h et l'exporte en json'''
    # les latitudes et longitudes sont en coordonnees leaflet positives au nord la latitude initiale est la plus petite (plus au sud )
    # on les transforme en indices grib
    # ilatini est l'indice de grib dans GR ( ex pour latini= 60 N   ilatini=30)
    ilatini = 90 - latini
    ilatfin = 90 - latfin
    # pour les longitudes longini est la plus a l'ouest
    if (longini < longfin):
        U10 = GR[0:12, ilatini:ilatfin, longini:longfin].real
        V10 = GR[0:12, ilatini:ilatfin, longini:longfin].imag
    else:
        fin = 360-longini         # sert a determiner la coupe a la fin
        debut = longfin+1
        U10 = np.concatenate((GR[0:12, ilatini:ilatfin, longini:360].real,
                             GR[0:12, ilatini:ilatfin, 0:longfin].real), axis=2)
        V10 = np.concatenate((GR[0:12, ilatini:ilatfin, longini:360].imag,
                             GR[0:12, ilatini:ilatfin, 0:longfin].imag), axis=2)

    u10 = [arr.tolist() for arr in U10]
    v10 = [arr.tolist() for arr in V10]
    return u10, v10






# partie serveur web

##########################################################################################################################
##########################################################################################################################

@app.route("/", methods=["GET", "POST"])
def index():
    # le but de cette page est juste de recuperer localstorage et de le renvoyer vers l'application 
     # on va juste lui passer la liste complete des courses 

    #print(listecourses)
    t0=round(time.time(),0)
   #print(t0)
    return render_template("index.html",listecourses=listecourses,t0=t0)





@app.route("/testajax")
def testjson(): 

    text = request.args.get('valeur')            # recupere les donnees correspondant a valeur dans le site html
    print(' ')
    print(text)
    print(' ')

    if request.is_json:                           # renvoie une valeur au serveur 
        print ('request is json')
        seconds=time.time()
        return jsonify ({'seconds':seconds, 'valeurtest': 5500})

    
    return render_template("testajax.html")





@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/clear")
def clear():
    return render_template('clear.html')


@app.route("/windybase", methods=["GET", "POST"])
def windybase():
    return render_template("windybase.html")




@app.route("/windbase2", methods=["GET", "POST"])
def windbase2():



   # source=request.args['source']
    trajetini= (request.args['trajetini']) 
    print()
    # print('trajet initial : ', trajetini)
    print( ) 
    source = 'windbase2'

    msg = 'Source windbase2 avec trajetini'
    print(msg)
    #print('listecourses',listecourses)

    # La liste des courses (listecourses)  supportees a ete etablie au debut du programme
    return render_template("windbase2.html", source=source, msg=msg, listecourses=listecourses,trajetini=trajetini)





####################################################################################################################################################################
####################################################################################################################################################################
@app.route('/patience', methods=["GET", "POST"])
def patience():
    global tws
 #identification de la source
    try:
        source = request.args['source']
        msg = 'la source est ' + source
    except:
        source = 'provisoire'                                    # valeur par defaut
        msg    = ' La source n est pas definie '    

    lat       = float(request.args['lat'])  
    lon       = float(request.args['lon']) 
    userid    = (request.args['userid']) 
    username  = (request.args['username']) 
    teamname  = (request.args['teamname']) 
    type      = (request.args['type']) 
    clat      = float(request.args['clat']) 
    clon      = float(request.args['clon']) 
    ts        = float(request.args['ts']) 
    o         = float(request.args['o']) 
    auto      = (request.args['auto']) 
    twa       = float(request.args['twa']) 
    tws       = float(request.args['tws']) 
    twd       = float(request.args['twd'])
    race      = (request.args['race']) 
    rank      = float(request.args['rank'])
    voile     = float(request.args['voile'])
    depart    = float(request.args['depart'])
    source    = (request.args['source'])

    # on extrait les valeurs utiles pour la course
    # course='569.1'

    course,caracteristiques,tabmarques,polairesjson,polairesnp,polairesjs,tabtws,tabtwa,tabvmg,polairesunit,exclusions=recherchecourse(race,tabcoursescomplet)

  
    # valeurs de l arrivee par defaut
    ari=1
    y1=float(tabmarques[ari][1])
    x1=float(tabmarques[ari][2])

    return render_template ("patience.html",lat=lat,lon=lon,userid=userid,username=username,teamname=teamname\
           ,type=type,clat=clat,clon=clon,ts=ts,o=o,auto=auto,twa=twa,tws=tws,twd=twd,race=race,rank=rank,voile=voile,\
            depart=depart,source=source,tabmarques=tabmarques,y1=y1,x1=x1 )


@app.route('/api/donneesvr', methods=["GET", "POST"])
def donneesvr():
    dictionnaire={'tws':tws,'twd':45}
    return jsonify(dictionnaire) 



@app.route('/cartesvr', methods=["GET", "POST"])
def cartesvr():
    global chemin
    chemin=np.asarray(chemin)
    cartevr=chargecarte_points(chemin)   # on charge la carte pour les 25 premiers points 
    text = request.args.get('valeur')            # recupere les donnees correspondant a valeur dans le site html
    print ('Demande Ajax  faite par vrouteur.html',text)
    b=5000   
    return jsonify ({'retour1':cartevr, 'retour2': b})







@app.route('/routagegefs', methods=["GET", "POST"])
def routagegefs(): 
    global tigGEFS,GRGEFS,tgribmax

    text = request.args.get('valeur')            # recupere les donnees correspondant a valeur dans le site html
    y0   = float(request.args.get('y0') )
    x0   = float(request.args.get('x0') )
    y1   = float(request.args.get('y1') )
    x1   = float(request.args.get('x1') ) 
    ts   = float(request.args.get('ts') )
    ari  = int  (request.args.get('ari')) 
    course   = request.args.get('course') 
    print ('Demande Ajax  faite par vrouteur.html',text)
    print ('valeurs de  y0 , x0 ',y0, x0)
    print ('valeurs de  y1 , x1 ',y1, x1)
    print ('valeurs de  ts      ',ts)
    print ('valeurs de  ari     ',ari)
    print ('valeurs de  course  ',course)

    typegrib='gefs'
    filename                      = basedir+'/gribsgefs/derniergrib.npy' 
    GRGEFS,tigGEFS,indices,avail_ts       = recupereGrib (filename)
    tgribmax                      = tigGEFS+384*3600 

    chemincomplet,noir,blanc,rouge,rouge2,tf,dureegefs=routagexxl(y0,x0,ts,y1,x1,ari,course,typegrib)
    
    chemin=chemincomplet[:,1:3]

    b=5000   

    chemin        = [arr.tolist() for arr in chemin]
    return jsonify ({'retour1':chemin, 'retour2': dureegefs})







@app.route('/vroutage', methods=["GET", "POST"])
def vroutage():

   
    global tig,GR,tgribmax,polaires,tabtwa,tabtws,tabvmg,chemin,polairesunit10,exclusions
    tic=time.time()
    #filename                      = basedir+'/gribs/derniergrib.npy' 
    filename                      = '/home/jp/gribsdistants/gribsgfs/derniergrib.npy'
    print ('\n Le grib utilise est le grib NOAA 1°\n')
    GR,tig,indices,avail_ts       = recupereGrib (filename)
    tgribmax                      = tig+384*3600 

    # print('indices',indices)
    # print('avail_ts ',avail_ts)
    availTsStr=time.strftime(" %d %b %H:%M ", time.localtime(avail_ts))
    # print('avail_ts ',availTsStr)

 #identification de la source
    try:
        source = request.args['source']
       # msg = 'la source est ' + source
    except:
        source = 'provisoire'                                    # valeur par defaut
       # msg    = ' La source n est pas definie '    
    if source=='patience':
        ycoord        = float(request.args['lat'])  
        xcoord        = float(request.args['lon']) 
        userid    = (request.args['userid']) 
        username  = (request.args['username']) 
        teamname  = (request.args['teamname']) 
        type      = (request.args['type']) 
        clat      = float(request.args['clat']) 
        clon      = float(request.args['clon']) 
        ts        = float(request.args['ts']) 
        o         = float(request.args['o']) 
        auto      = (request.args['auto']) 
        twa       = float(request.args['twa']) 
        tws       = float(request.args['tws']) 
        twd       = float(request.args['twd'])
        race      = (request.args['race']) 
        rank      = float(request.args['rank'])
        voile     = float(request.args['voile'])
  
        # ces elements ont ete rajoute par patience qui les a extrait du local storage
        y1       = float(request.args['y1'])  
        x1       = float(request.args['x1'])  
        ari      = int(request.args['ari']) 
        dep      = int(request.args['dep'])
        print('voile issue de dashmap par patience', voile)
        print('team issue de dashmap par patience', teamname)


    if source=='windbase2.html':    
        username  = (request.args['username'])  
        race      = (request.args['race']) 
        ycoord    = float(request.args['ycoord'])  
        xcoord    = float(request.args['xcoord']) 
        ts        = float(request.args['t0']) 
        ari       = int(request.args['ari']) 
        dep       = int(request.args['dep'])
        y1        = float(request.args['y1'])  
        x1        = float(request.args['x1'])  

        # elements rajoutes
        userid    = 'xxxxxxxxxxxxxxx'   
        teamname  = ' '
        type      = 258
        voile     = 17
        clat      = ycoord
        clon      = xcoord
        o         = 0
        auto      = 'auto'
        twa       = 0
        tws       = 0
        twd       = 0
        rank      = 9999



    if source=='vroutage.html':  
        username  = (request.args['username']) 
        race      = (request.args['race']) 
        ycoord    = float(request.args['lat'])  
        xcoord    = float(request.args['lon']) 
        dep       = int(request.args['dep'])
        ari       = int(request.args['ari']) 
        

        userid    = (request.args['userid']) 
        teamname  = (request.args['teamname']) 
        type      = (request.args['type']) 
        clat      = float(request.args['clat']) 
        clon      = float(request.args['clon']) 
        ts        = float(request.args['ts']) 
        o         = float(request.args['o']) 
        auto      = (request.args['auto']) 
        twa       = float(request.args['twa']) 
        tws       = float(request.args['tws']) 
        twd       = float(request.args['twd'])
        rank      = float(request.args['rank'])
        voile     = float(request.args['voile'])

        # ces elements ont ete rajoute par patience qui les a extrait du local storage

       
        
   
    if source=='context':  

        # elements strictement necessaires
        race      = (request.args['race']) 
        username  = (request.args['username']) 
        ycoord    = float(request.args['y0'])  
        xcoord    = float(request.args['x0']) 
        ts        = float(request.args['ts'])
        yari      = float(request.args['y1'])  
        xari      = float(request.args['x1'])  
        dep       = int(request.args['dep'])
        ari       = int(request.args['ari']) 



        print(' race ',race)

      # elements rajoutes
        userid    = 'xxxxxxxxxxxxxxx'   
        teamname  = '-'
        type      = 258
        voile     = 17
        clat      = ycoord
        clon      = xcoord
        o         = 0
        auto      = 'auto'
        twa       = 0
        tws       = 0
        twd       = 0
        rank      = 9999
        #Elements supplementaires
        # userid    = (request.args['userid']) 
        # teamname  = (request.args['teamname']) 
        # type      = (request.args['type']) 
        # clat      = float(request.args['clat']) 
        # clon      = float(request.args['clon']) 
        # o         = float(request.args['o']) 
        # auto      = (request.args['auto']) 
        # twa       = float(request.args['twa']) 
        # tws       = float(request.args['tws']) 
        # twd       = float(request.args['twd'])
        # rank      = float(request.args['rank'])
        # voile     = float(request.args['voile'])
  
      
      
       
       
     
  
    course,caracteristiques,tabmarques,polairesjson,polaires,polairesjs,tabtws,tabtwa,tabvmg,polairesunit,exclusions=recherchecourse(race,tabcoursescomplet)
    # print('tabmarques',tabmarques)
    # print()
    # print(' \n caracteristiques course',caracteristiques)
    # Recuperation de y0 et x0 en fontion de depart et arrivee
   


    twsunit=np.arange(701)/10
    for i in range (0,1801):
        twaunit=np.ones(701)*i/10
        twsunit[twsunit>69]=69
        polairesunit10[:,i]= vit_polaires(polairesunit,twsunit,twaunit)

    #print('polairesunit10.shape',polairesunit10.shape)    

    nomcourse= caracteristiques['nom']
    leg      = caracteristiques['leg']
    bateau   = caracteristiques['bateau'].split('/')[1]

    if dep>=0 :
        y0=tabmarques[dep][1]
        x0=tabmarques[dep][2]
        print('\nOn est dans le cas d\'un depart sur marque y0= {} x0= {}'.format(y0,x0))

    else :
        y0=ycoord
        x0=xcoord           
        print('on est dans le cas dun depart sur coordonnees') 
        print('y0,x0',y0,x0)
    

    if ari>=0 :
        y1=tabmarques[ari][1]
        x1=tabmarques[ari][2]

    else :  
        y1=yari
        x1=xari  
   

    t0=time.time()
    twsjp, twdjp = prevision5(tig, GR, t0, y0, x0)          # on va recuperer tws et twd par le grib pour t0 à voir si t0 est le bon temps pour Vr
   
    print('\nLa source est {} dep= {} ari= {}  Routage de {:6.4f}  {:6.4f}  vers {:6.4f}  {:6.4f} \n '.format(source,dep,ari,y0,x0,y1,x1 ))  
   
   
    
    # #####################################################################""
    # recuperation des vents sur zone pour transmission a  vroutage.html
    ydep = min(y0, y1)
    latini = (math.floor(y0)+10)    # latitude la plus au nord en premier
    latfin = (latini - 20)
    lngini = (math.floor(x0)-20) % 360
    lngfin = (lngini+40) % 360
    u10, v10 = vents_encode(tig, GR, latini, latfin, lngini, lngfin)
    # #####################################################################

     
    # if request.is_json:                           # renvoie une valeur au serveur 
    #     text = request.args.get('valeur')            # recupere les donnees correspondant a valeur dans le site html
    #     print ('Demande Ajax  pour les cartes',text)

    # if request.is_json:                           # renvoie une valeur au serveur 
    #    #text = request.args.get('valeur')            # recupere les donnees correspondant a valeur dans le site html
    #     print ('Demande de routage GEFS par Ajax json')
    #     ts=time.time()
    #     seconds=time.time()
    #     typegrib='gefs'
    #     chemingefs,chemincompletgefs,noirgefs,blancgefs,tfgefs,dureegefs=routagexxl(y0,x0,ts,y1,x1,ari,course,'gefs')
    #     chemingefs       =[arr.tolist() for arr in chemingefs]
    #     chemincompletgefs=[arr.tolist() for arr in chemincompletgefs]
    #     return jsonify ({'tfgefs':tfgefs, 'valeurtest': chemingefs, 'chemincompletgefs': chemincompletgefs,'dureegefs':dureegefs})



    # else:
    ts=time.time()
    typegrib='gfs'

    # print ('valeurs de base')
    # print ('valeurs de  y0 , x0 ',y0, x0)
    # print ('valeurs de  y1 , x1 ',y1, x1)
    # print ('valeurs de  ts      ',ts)
    # print ('valeurs de  ari     ',ari)
    # print ('valeurs de  course  ',course)

   
   
    chemincomplet,noir,blanc,rouge,rouge2,tf,duree=routagexxl(y0,x0,ts,y1,x1,ari,course,typegrib)
    tabmarche                               = routag(chemincomplet,ts,polaires,typegrib)

   
    chemin=chemincomplet[:,1:3]
    chemincomplet = [arr.tolist() for arr in chemincomplet]
    chemin        = [arr.tolist() for arr in chemin]
    tabmarche     = [arr.tolist() for arr in tabmarche]
    
    tac=time.time()
    print('Duree                {:6.2f}'.format(tac-tic))
    print ('Duree par isochrone {:6.3f}'.format((tac-tic )/numiso))
    return render_template ("vroutage.html",lat=y0,lon=x0,userid=userid,username=username,teamname=teamname,\
        type=type,clat=clat,clon=clon,ts=ts,o=o,auto=auto,twa=twa,tws=tws,twd=twd,twsjp=twsjp,twdjp=twdjp,\
        race=race,rank=rank,voile=voile, dep=dep,ari=ari,listecourses=listecourses,caracteristiques=caracteristiques,\
        nomcourse=nomcourse,leg=leg,bateau=bateau,polairesjson=polairesjson,source=source,tabmarques=tabmarques,\
        polairesjs=polairesjs, chemin=chemin,chec=chemincomplet,tabmarche=tabmarche,noir=noir,blanc=blanc,rouge=rouge,rouge2=rouge2,duree=duree,y1=y1,x1=x1,\
        tig=tig,availTsStr=availTsStr,u10=u10,v10=v10,nomgrib=typegrib,cartevr=cartevr,exclusions=exclusions)



if __name__ == "__main__":
    # db.create_all()                 #creation de la base de donnees
    app.debug = True
    app.run(host='0.0.0.0',port=5000,debug=True)
