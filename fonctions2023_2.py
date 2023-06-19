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
import zlib
import requests
import shapely
import tarfile 
from shapely.geometry import Point,LineString,Polygon,MultiLineString,MultiPoint,MultiPolygon
from shapely.ops import unary_union
from shapely import speedups

basedir=os.path.dirname(os.path.abspath("__file__")) 


if basedir=='/home/jp':                                  # cas ou le programme est declenche a partir d'une tache cron 
    basedir='/home/jp/vrouteur'
# print('Repertoire de travail pour fonctions : ',basedir)
# def impression2(tableau):                                        '''impression tableau 2 colonnes'''
# def impression3(tableau):                                        '''impression tableau 3 colonnes'''
# def impression3s(tableau):                                       '''impression tableau 32 colonnes'''
# def impression4(tableau):                                        '''impression tableau 4 colonnes'''
# def impression4s(tableau):                                       '''impression tableau 4s colonnes'''
# def impression5(tableau):                                        '''impression tableau 5 colonnes'''
# def impression8(tableau):                                        '''impression tableau 8 colonnes'''
# def impression8isoglobal(tableau):                               '''impression tableau 9 colonnes'''
# def impression9(tableau):                                        '''impression tableau 9 colonnes'''
# def impression10(tableau):                                       '''impression tableau 10 colonnes'''
# def impression11(tableau):                                       '''impression tableau 11 colonnes'''
# def impression12(tableau):                                       '''impression tableau 12 colonnes'''
# def ftabvmg(tab_tws,tab_twa,polaires):                          '''constitue un tableau des vmg max et min en fonction du vent '''
# def vmgmaxspeed(tws,tab_twa , tab_tws  ,polaires):              '''donne les valeurs de vmgmax et speedmax ainsi que les angles pour une force de vent'''
# def opti3(twa, tws,tab_twa , tab_tws  ,polaires):               ''' Optimise la twa lorsqu elle est autour des valeurs de vmgmax'''
# def opti_twa(tabtws,tabtwa,tab_twa,tab_tws,polaires)  :         ''' on fournit en entree   le tableau des tws et des twa  pour calcul  '''
# def petit_lissage(tabtwa):
# def moyen_lissage(tabtwa):                                      ''' on lisse en retirant les variations ponctuelles''' 
# def moyennage(tabtwa):                                          ''' on lisse en moyennant'''
# def charge_carto(y0,x0):                                        ''' charge la carto de la tuile'''
# def extrait_terres(lat,lng,pas,mask):'                           '' extrait les terres a partir du masque'''
# def securite(polygon,marge):                                     ''' definit un polygone avec une marge de securite sur lepolygone de base'''
# def securite2(multipolyline,marge):                             ''' definit des marges de securité sur une multipolyline''''''retourne des multipolylines incluant la marge de securite''' 
# def fleche2(y,x,cap,l,couleur,m):                               ''' Dessine une fleche se terminant au point y,x suivant un cap avec une longueur l dans la carte m '''
# def point_terre(listept,carte):                                 ''' listept est une liste de points sous forme de np.array'''
# def point_terre2(y,x,cartevr):                                  ''' y x est un point '''
# def sailpenalite(tws):                                          ''' retourne la penalite en secondes ou la vitesse est reduite interpolation spline VR'''  
# def tackpenalite(tws):                                          ''' retourne la penalite en secondes ou la vitesse est reduite interpolation spline VR'''  
# def gybepenalite(tws):                                          ''' retourne la penalite en secondes ou la vitesse est reduite interpolation spline VR'''  
# def sailpenalite0(tws):                                         ''' retourne la penalite en secondes ou la vitesse est reduite interpolation lineaire'''
# def peno_stamina(manoeuvre,coefboat,tws):                       ''' donne la perte de stamina en fonction de manoeuvre et de la vitesse du vent'''
# def recup_stamina(T,tws):                                        ''' donne la recuperation de la stamina en fonction de T en secondes et de la vitesse du vent '''
# def voile_utilisee (twa,tws,voileant):                           ''' retourne la voile utilisee et la vitesse polaire atteinte en tenant compte du coefficient de tolerance de 1.014'''   
    




###########################################################################################################
# Fonctions d impression
##########################################################################################################   
def impression2(tableau):
    '''impression tableau 2 colonnes'''
    ''' pour tableau final  N temps TWA'''
    for i in range (len(tableau)):
        print('{:4.0f}   \t{} \t {:6.0f}   '\
              .format(tableau[i,0],time.strftime(" %d %b %H:%M ",time.localtime(tableau[i,1])), tableau[i,2]) )

def impression3(tableau):
    '''impression tableau 3 colonnes'''
    ''' pour tableau final  N temps TWA'''
    for i in range (len(tableau)):
        print('{:4.0f}   \t{} \t {:6.0f}   '\
              .format(tableau[i,0],time.strftime(" %d %b %H:%M ",time.localtime(tableau[i,1])), tableau[i,2]) )

        
def impression3s(tableau):
    '''impression tableau 3 colonnes'''
    ''' pour tableau final  N temps TWA'''
    for i in range (len(tableau)):
        print('{:4.2f}   \t{:4.2f} \t {:4.2f}   '\
              .format(tableau[i,0],tableau[i,1], tableau[i,2]) )        
        
        
        
        
def impression4(tableau):
    '''impression tableau 4 colonnes'''
    ''' pour tableau final  N temps TWA'''
    for i in range (len(tableau)):
        print('{:4.0f}   \t{} \t {:6.0f}  \t {:6.0f} '\
              .format(tableau[i,0],time.strftime(" %d %b %H:%M ",time.localtime(tableau[i,1])), tableau[i,2], tableau[i,3]) )       
        
def impression4s(tableau):
    '''impression tableau 4 colonnes'''
    
    for i in range (len(tableau)):
        print('{:6.2f}   \t{:6.2f} \t {:6.2f}  \t {:6.2f} '\
              .format(tableau[i,0],tableau[i,1], tableau[i,2], tableau[i,3]) )             


            
def impression20tabmarchetitre(titre,tableau):
    '''impression tableau de marche 13 colonnes'''
    ''' pour tableau de marche   '''
    print('\n{}\n********************************************************\n     N \t\t Y \t   X  \t\tdate   \t  tws    \ttwd  \tcap   \ttwa    \tspeed \tvoile \tchgt \tpeno solde_a    amort   stam \tMer   t_ordre \tvaleur \tv_auto  cible   '.format(titre))
  
    for i in range (len(tableau)):
        if tableau[i,0]==1:
            print()
            print('{:4.0f}\t{:10.4f}\t{:10.4f}\t{}\t{:6.1f}\t{:6.1f}\t{:6.1f}\t{:6.1f}\t{:6.2f}\t{:4.0f}\t{:4.0f}\t{:4.0f}\t{:3.0f} \t{:3.1f} \t{:3.1f}   \t{:3.0f}  \t{:3.0f}  \t{:7.2f}  {:3.0f}  \t{:3.0f}'\
                  .format(tableau[i,0],tableau[i,1], tableau[i,2],time.strftime(" %d %b %H:%M ",time.localtime(tableau[i,3])),    
                          tableau[i,4], tableau[i,5], tableau[i,6], tableau[i,7], tableau[i,8], tableau[i,9], tableau[i,10], tableau[i,11], tableau[i,12], tableau[i,13], tableau[i,14], tableau[i,15], tableau[i,16], tableau[i,17], tableau[i,18], tableau[i,19]) )   
        else:
            print('{:4.0f}\t{:10.4f}\t{:10.4f}\t{}\t{:6.1f}\t{:6.1f}\t{:6.1f}\t{:6.1f}\t{:6.2f}\t{:4.0f}\t{:4.0f}\t{:4.0f}\t{:3.0f} \t{:3.1f} \t{:3.1f}   \t{:3.0f}  \t{:3.0f}  \t{:7.2f}  {:3.0f}   \t{:3.0f}'\
            .format(tableau[i,0],tableau[i,1], tableau[i,2],time.strftime(" %d %b %H:%M ",time.localtime(tableau[i,3])),    
             tableau[i,4], tableau[i,5], tableau[i,6], tableau[i,7], tableau[i,8], tableau[i,9], tableau[i,10], tableau[i,11], tableau[i,12], tableau[i,13], tableau[i,14], tableau[i,15], tableau[i,16], tableau[i,17], tableau[i,18], tableau[i,19]) )        
            
            
            
            
            
            
            
def impression8(tableau):
    '''impressiontableau 8 colonnes'''
    ''' pour chemincomplet'''
    for i in range (len(tableau)):
        print('{:6.4f} \t{:6.4f} \t {:6.0f}  \t{:6.0f}  \t{:6.0f} \t {:6.0f} \t {:7.2f}  \t{:7.2f}   '\
              .format(tableau[i,0],tableau[i,1], tableau[i,2],
                      
                      
                      tableau[i,3],tableau[i,4], tableau[i,5],tableau[i,6],tableau[i,7])) 


def impression8isoglobal(tableau):
    '''impressiontableau 8 colonnes'''
    ''' pour chemincomplet'''
    print(' X \t\t Y \t\t  nsiso \t nptsm \t\t npoint  \t npt-ds_iso  \t ordoar  \t twaor') 
    for i in range (len(tableau)):
        print('{:6.4f} \t{:6.4f} \t {:6.0f}  \t{:6.0f}  \t{:6.0f} \t\t {:6.2f} \t {:6.2f}  \t{:6.2f}   '\
              .format(tableau[i,0],tableau[i,1], tableau[i,2], tableau[i,3],tableau[i,4], tableau[i,5],tableau[i,6],tableau[i,7]))         
        
def impression9(tableau):
    '''impressiontableau 9 colonnes'''
    ''' pour chemin complet avec temps de calcul'''
    for i in range (len(tableau)):
        print('{:6.0f} \t{:6.4f} \t {:6.4f}   \t{} \t{:6.4f} \t {:6.4f} \t {:6.2f}  \t{:6.2f}  \t{:6.2f}  '\
              .format(tableau[i,0],tableau[i,1], tableau[i,2], time.strftime(" %d%b %H:%M ",time.localtime(tableau[i,3])), tableau[i,4], tableau[i,5],tableau[i,6],tableau[i,7], tableau[i,8])) 

def impression9cc(tableau):
    '''impressiontableau 9 colonnes'''
    ''' pour chemin complet avec temps de calcul'''
    print('Chemin complet\n***********************')
    print ('N pt \tY \t\t  X \t\t\tT \ttws   \t  twd \t\t tabcap\t \ttwaos \t\ttwaopti \tvitesses')
    for i in range (len(tableau)):
        print('{:6.0f} \t{:6.4f} \t {:6.4f}   \t{} \t{:6.2f} \t {:6.2f} \t {:6.2f}  \t{:6.2f}  \t{:6.2f}  '\
              .format(tableau[i,0],tableau[i,1], tableau[i,2], time.strftime(" %d%b %H:%M ",time.localtime(tableau[i,3])), tableau[i,4], tableau[i,5],tableau[i,6],tableau[i,7], tableau[i,8])) 
        
        
        
def impression10cc(tableau):
    '''impression tableau 10 colonnes pour chemin complet avec twaopti'''
    print ('N pt \tY \t\t  X \t\t\tT \ttws   \t  twd \t\t tabcap\t \ttwaos \t\ttwaopti \tvitesses')
    for i in range (len(tableau)):
        print('{:6.0f} \t{:6.4f} \t {:6.4f}   \t{} \t{:6.2f} \t {:6.2f} \t {:6.2f}  \t{:6.2f}  \t{:6.2f}  \t{:6.2f} '\
              .format(tableau[i,0],tableau[i,1], tableau[i,2], time.strftime(" %d%b %H:%M ",time.localtime(tableau[i,3])), tableau[i,4], tableau[i,5],tableau[i,6],tableau[i,7], tableau[i,8],tableau[i,9])) 
        
def impression11cc(tableau):
    '''impression tableau 11 colonnes pour chemin complet avec twaopti et distance'''
    print ('N pt \tY \t\t  X \t\t\tT \ttws   \t  twd \t\t tabcap\t \ttwaos \t\ttwaopti \tvitesses \tdist')
    for i in range (len(tableau)):
        print('{:6.0f} \t{:6.4f} \t {:6.4f}   \t{} \t{:6.2f} \t {:6.2f} \t {:6.2f}  \t{:6.2f}  \t{:6.2f}  \t{:6.2f} \t\t{:6.4f}'\
              .format(tableau[i,0],tableau[i,1], tableau[i,2], time.strftime(" %d %b %H:%M ",time.localtime(tableau[i,3])), tableau[i,4], tableau[i,5],tableau[i,6],tableau[i,7], tableau[i,8],tableau[i,9],tableau[i,10])) 
                
        
        
        
def impression10(tableau):
    '''impressiontableau 10 colonnes'''
    for i in range (len(tableau)):
        print('{:4.0f} \t{:4.0f} \t {:6.4f} \t {:6.4f} \t{:6.0f}  \t {:6.2f} \t {:6.2f}  \t{:6.2f}  \t{:6.2f}  \t{:6.2f}'\
              .format(tableau[i,0],tableau[i,1], tableau[i,2], tableau[i,3],tableau[i,4] , tableau[i,5],tableau[i,6],tableau[i,7], tableau[i,8], tableau[i,9])) 

def impression10isocreme(tableau):
    '''impressionisocreme 10 colonnes'''
    for i in range (len(tableau)):
        print('{:6.4f} \t{:6.4f} \t {:4.0f} \t {:4.0f} \t{:4.0f}  \t {:6.2f} \t {:6.2f}  \t{:6.2f}  \t{:6.2f}  \t{:6.2f}'\
              .format(tableau[i,0],tableau[i,1], tableau[i,2], tableau[i,3], tableau[i,4], tableau[i,5],tableau[i,6],tableau[i,7], tableau[i,8], tableau[i,9])) 

        
def impression11isocreme(tableau):
    '''impressionisocreme 11 colonnes'''
    for i in range (len(tableau)):
        print('{:6.4f} \t{:6.4f} \t {:4.0f} \t {:4.0f} \t{:4.0f}  \t {:6.2f} \t {:6.2f}  \t{:6.2f}  \t{:6.2f}  \t{:6.2f} \t{:6.2f}'\
              .format(tableau[i,0],tableau[i,1], tableau[i,2], tableau[i,3], tableau[i,4], tableau[i,5],tableau[i,6],tableau[i,7], tableau[i,8], tableau[i,9], tableau[i,10])) 
       
        
        
        
def impression11(tableau):
    '''impression tableau 11 colonnes'''
    for i in range (len(tableau)):
        print('{:4.0f} \t{:4.0f} \t{:6.4f}  \t{:6.4f}  \t{}  \t {:6.2f} \t {:6.2f}  \t{:6.2f}  \t{:6.2f}  \t{:6.2f}  \t{:6.2f} '\
              .format(tableau[i,0],tableau[i,1], tableau[i,2], tableau[i,3], time.strftime(" %d %b %H:%M ",time.localtime(tableau[i,4])), tableau[i,5],tableau[i,6],tableau[i,7], tableau[i,8],tableau[i,9],tableau[i,10])) 

def impression12(tableau):
    '''impression tableau 12 colonnes'''
    for i in range (len(tableau)):
        print('{:4.0f} \t{:6.4f} \t{:6.4f} \t{} \t{:6.4f}  \t{:6.2f} \t{:7.2f} \t{:7.2f}  \t{:7.2f}  \t{:7.2f}  \t{:7.2f}  \t{:7.2f}'\
              .format(tableau[i,0],tableau[i,1], tableau[i,2],  time.strftime(" %d %b  %H:%M ",time.localtime(tableau[i,3])),\
                      tableau[i,4],tableau[i,5],tableau[i,6],tableau[i,7], tableau[i,8], tableau[i,9], tableau[i,10], tableau[i,11])) 


def impression_tabtwas(tableau) :

    '''impression tableau 6 colonnes tabtwas avec 2 colonnes supplementaires  '''
    '''numero  T tws twd twaos  res1 res2'''
    print ('N \t T  \t\t\ttws  \ttwd  \ttwaos  \t\t res1 \t\t res2')
    for i in range (len(tableau)):
        print('{:4.0f} \t{} \t{:4.2f} \t{:5.2f} \t{:7.2f} \t{:7.2f} \t{:7.2f}'\
              .format(tableau[i,0],time.strftime(" %d %b %Y %H:%M:%S ",time.localtime(tableau[i,1])),\
              tableau[i,2],tableau[i,3],tableau[i,4], tableau[i,5], tableau[i,6])) 
        
        
##########################################################################################################
# Fonctions de tracage
##########################################################################################################        
        
        
def fleche3(y,x,cap,l,couleur,m):
    '''Dessine une fleche se terminant au point y,x suivant un cap avec une longueur l dans la carte m '''
    yfin=y-l*math.cos(cap*math.pi/180)
    xfin=x-l*math.sin(cap*math.pi/180)/math.cos(y*math.pi/180)
    yfin2=yfin-l*0.1*math.cos((cap+30)*math.pi/180)
    xfin2=xfin-l*0.1*math.sin((cap+30)*math.pi/180)/math.cos(yfin*math.pi/180)  
    yfin3=yfin-l*0.1*math.cos((cap-30)*math.pi/180)
    xfin3=xfin-l*0.1*math.sin((cap-30)*math.pi/180) /math.cos(yfin*math.pi/180)
    yfine=y-l*1.1*math.cos(cap*math.pi/180)
    xfine=x-l*1.1*math.sin(cap*math.pi/180)/math.cos(y*math.pi/180)
    yfine2=yfine-l*0.1*math.cos((cap+30)*math.pi/180)
    xfine2=xfine-l*0.1*math.sin((cap+30)*math.pi/180)/math.cos(yfine*math.pi/180)
    yfine3=yfine-l*0.1*math.cos((cap-30)*math.pi/180)
    xfine3=xfine-l*0.1*math.sin((cap-30)*math.pi/180) /math.cos(yfine*math.pi/180)
    fleche=[[[y,x],[yfin,xfin],[yfin2,xfin2],[yfin,xfin],[yfin3,xfin3],[yfin,xfin],[yfine,xfine],[yfine2,xfine2],[yfine,xfine],[yfine3,xfine3]]]
    folium.PolyLine (fleche,color=couleur,weight=2 ).add_to(m)
    return None         
        
        
##########################################################################################################
# Fonctions d optimisation
##########################################################################################################
def ftabvmg(tab_tws,tab_twa,polaires):
    '''constitue un tableau des vmg max et min en fonction du vent '''
    ''' tabvmg comprend tws tous les 0.1 twamin et twamax '''
    vmax=max(tab_tws)
    tabvmg=np.zeros((  (vmax-2)*10,3))
    tabvmg[:,0]=np.arange(2,vmax,0.1) 
    for i in range (len(tabvmg)):
        tabvmg[i,1]=vmgmaxspeed(tabvmg[i,0],tab_twa , tab_tws  ,polaires)[0]
        tabvmg[i,2]=vmgmaxspeed(tabvmg[i,0],tab_twa , tab_tws  ,polaires)[2]   # retourne twamax,vmgmax,twamin,vmgmin,twaspeedmax,speedmax
    return tabvmg    



def vmgmaxspeed(tws,tab_twa , tab_tws  ,polaires):
    '''donne les valeurs de vmgmax et speedmax ainsi que les angles pour une force de vent'''
    '''Attention ici tab twa tabtws polaires sont des valeurs globales'''
    ''' calcule un tableau de valeur tous les 0.1 de twa '''
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


def opti3(twa, tws,tab_twa , tab_tws  ,polaires):
    ''' Optimise la twa lorsqu elle est autour des valeurs de vmgmax'''
    ''' en entree une twa et une tws'''
    ''' sortie la twa optimisee si la twa est a moins de 2 ° de l'optimum   ---'''
    # retourne les valeurs caracteristiques pour un vent donné 
    # donne les valeurs caracteristiques pour une  vitesse de vent donné
    twamax,vmgmax,twamin,vmgmin,twaspeedmax,speedmax=vmgmaxspeed(tws,tab_twa , tab_tws  ,polaires)
    signe=twa/(abs(twa)+0.0001)
    if abs(twa)-twamax<2:                  # 
        twar=round((twamax*signe),0)
    elif abs(abs(twa)-twamin)<2:
        twar=round((twamin*signe),0)
   
    elif   abs(abs(twa)-twaspeedmax)<2: 
        twar=round((twaspeedmax*signe),1)
    #bannissement des valeurs hors laylines   
    elif abs(twa)<twamax:
        twar=twamax*signe
    elif abs(twa)>twamin:
        twar=round((twamin*signe),1)
    else:
        twar=twa  
    twar=round(twar,0)    
    return twar    


    
def opti_twa(tabtws,tabtwa,tab_twa,tab_tws,polaires)  : 
    ''' on fournit en entree   le tableau des tws et des twa  pour calcul  '''
    ''' en sortie on obtient les twa optimisee et arrondies au degre pour les valeus proches des optimums au pres au portant et au vent arriere'''
    twaopti=np.zeros(len (tabtwa))
    for i in range (len (tabtwa)):
        tws=tabtws[i]
        twa=tabtwa[i]
        twaopti[i]=opti3(tabtwa[i],tabtws[i],tab_twa,tab_tws,polaires)
    twaopti=twaopti.reshape(-1,1)
    return twaopti


def petit_lissage(tabtwa):
    ''' on lisse en retirant les variations ponctuelles''' 
    twalisse=np.zeros(len (tabtwa))
    twalisse[0]=tabtwa[0]
    for i in range (len (tabtwa)-2):
        if (tabtwa[i]==tabtwa[i+2]):
            twalisse[i+1]=tabtwa[i]
        else :    
            twalisse[i+1]=tabtwa[i+1]
    twalisse[-1]=tabtwa[-1] 
    twalisse=twalisse.reshape(-1,1)
    return twalisse

def moyen_lissage(tabtwa):
    ''' on lisse en retirant les variations ponctuelles''' 
    twamlisse=np.zeros(len (tabtwa))
    twamlisse[0]=tabtwa[0]
    
    for i in range (len (tabtwa)-3):
        if (tabtwa[i]==tabtwa[i+3]):
            twamlisse[i+1]=tabtwa[i]
            twamlisse[i+2]=tabtwa[i]
        else :    
            twamlisse[i+1]=tabtwa[i]
            twamlisse[i+2]=tabtwa[i]
    twamlisse[-1]=tabtwa[-1] 
    twamlisse[-2]=tabtwa[-2] 
    twamlisse=twamlisse.reshape(-1,1)
    return twamlisse

def moyennage(tabtwa):
    twamoyenne=np.zeros(len (tabtwa))
    twamoyenne[0]=tabtwa[0]
    for i in range (len (tabtwa)-2):
        if (tabtwa[i]*tabtwa[i+1])>0:
            twamoyenne[i+1]=np.round((tabtwa[i]+tabtwa[i+2])/2)
        else:
            twamoyenne[i]=tabtwa[i]
            twamoyenne[i+1]=tabtwa[i+1]
    twamoyenne[-2]=tabtwa[-2]          
    twamoyenne[-1]=tabtwa[-1]        
    twamoyenne=twamoyenne.reshape(-1,1)        
    return twamoyenne



def charge_carto(y0,x0):
    resolution=1
    lat=math.ceil(y0)
    lng=math.floor(x0)
    pas=730
    resolution=1
    
    # on cherche si le fichier existe dans les txt
    file=str(resolution)+'_'+str(lng)+'_'+str(lat)+'.txt'
    # print(basedir)
    filename=basedir+'/carto/txt/'+file

    if os.path.exists(filename) == True:                                             # si le fichier existe on le charge
        with open(filename, "r") as fichier:
            cartetexte=fichier.read()
            # print('Le fichier carte existe deja en local')
        carte=eval(cartetexte)     
        # print(carte) 

    else:                                              # si le fichier n'existe pas on va le chercher chez vr
        lng_f=str(int(lng/10))
        lat_f=str(int(lat/10))
        folder='/'+str(resolution)+'/'+lng_f+'/'+lat_f+'/'
        file=str(resolution)+'_'+str(lng)+'_'+str(lat)+'.deg'
        folderlocal=basedir+'/carto/'
        filelocal=folderlocal+file

        url='https://static.virtualregatta.com/ressources/maps/dalles/vro2k16'+folder+file
        #url2='https://static.virtualregatta.com/ressources/maps/dalles/vro2k16/1/0/4/1_-2_46.deg'
        urlretrieve(url, filelocal)  # recuperation des fichiers
        # print('{} fichier chargé chez VR et sauvegardé en local  !\n'.format(file)) 

        #2) Ouverture du fichier VR et extraction du masque 
        with open(filelocal,'rb') as fid:
            header=fid.read(11)
            gzbuf=fid.read()
            databuf=zlib.decompress(gzbuf,-zlib.MAX_WBITS)
        data=np.frombuffer(databuf,dtype=np.int8)
        data.resize((730,730))
        mask=   ( data > -1) *1

        #3) Conversion du masque en polygone 
        carte=extrait_terres(lat,lng,pas,mask)

        #4 on le sauvegarde en txt et en js local
        # ecriture dans fichier 
        lng_f=str(int(lng/10))
        lat_f=str(int(lat/10))
        folder=str(resolution)+'/'+lng_f+'/'+lat_f+'/'
        file=str(resolution)+'_'+str(lng)+'_'+str(lat)+'.txt'
        filename=basedir+'/carto/txt/'+file
        # print(' sauvegarde du txt ',filename)
        textecarte=str(carte)
        with open(filename, "w+") as fichier:
            fichier.write(textecarte)
        #sauvegarde en js on met E et W pour eviter d'avoir des ennuis 
        if lng>0:
            oe='E'
        else:
            oe='W'
        if lat>0:
            on='N'
        else:
            on='S'
        # variablejs='map_'+str(abs(lat))+on+'_'+str(abs(lng))+oe     
        # namefichierjs1='/home/jphe/carto/js/'+variablejs+'.js'    
        # namefichierjs2='/home/jphe/dashmap/cartes/'+variablejs+'.js' 
        # textejs=variablejs+' = '+textecarte    
        # # on va sauver a la fois dans carto et dans dashmap
        # with open(namefichierjs1, "w+") as fichier:
        #     fichier.write(textejs)
        # with open(namefichierjs2, "w+") as fichier:
        #     fichier.write(textejs)
    return  carte   

def chargecarte_points(points):
    '''charge l ensemble des cartes existant sur un itineraire et les concatene'''
    b=np.ceil(points[:,0]).reshape(-1,1)
    c= np.floor(points[:,1]).reshape(-1,1)
    cartes=np.concatenate((b,c),axis=1)
    listecartes=np.unique(cartes, axis=0)
    # print(listecartes)
    cartevr=[]
    for i in range (len(listecartes)): 
        carteunique=charge_carto(listecartes[i][0],listecartes[i][1])
        if  carteunique:
            for j in range (len  (carteunique)):
                cartevr.append(carteunique[j])
    return cartevr   


def intersect (polyline,cartevr):
    '''teste lintersection d'une polyline avec la cartevr'''
    polyline_sh=LineString(polyline) 
    k=1
    for polygon in cartevr:
        polygon_sh=Polygon(polygon)
        
        if polyline_sh.intersects(polygon_sh):
            k*=0
    return k  

def f_merlibre(y0,x0,vitesse,temps,capdebut,capfin):
    ''' calcule les caps libres de terre entre capdebut et capfin '''
    ''' pour un vitesse donnee en noeuds et un temps en s '''
    ''' retourne un tableau des caps libres '''
    ''' une valeur merlibreglobale=1 si pas de terres dans le range des caps'''
    ''' la carte vr  des caps explores et les segments explores'''
    # cartevr=charge_carto(y0,x0)
    segment=np.zeros((360,2,2))
    segmentsfolium=[]
    points =np.zeros((360,2)) 
    capslibres=[]
    merlibreglobale=1
    capmini=min(capdebut,capfin)
    capmaxi=max(capdebut,capfin) 
    # on fait un premier passage pour pouvoir charger toutes les cartes
    for cap in range (capmini,capmaxi):
        points[ cap, 0] = y0+vitesse*temps/3600/60*math.cos(cap*math.pi/180)
        points[ cap, 1] = x0+vitesse*temps/3600/60*math.sin(cap*math.pi/180)/math.cos(y0*math.pi/180)
    cartevr=chargecarte_points(points)        # on charge la carte  globale  tenant compte de tous les points calcules
    
    for cap in range (0,360):        
        segment[cap]=[[y0,x0],[ points[ cap, 0], points[ cap, 1]]]
        res=intersect(segment[cap],cartevr)
        segmentsfolium.append(  [[[y0,x0],[ points[ cap, 0], points[ cap, 1]]],res ] )
        merlibreglobale*=res
        if res==1:
            capslibres.append(cap)
    return capslibres,merlibreglobale,cartevr,segmentsfolium





def f_merlibre_range(y0,x0,vitesse,temps,rangecaps):
    '''rangecaps est un np array'''
    ''' calcule les caps libres de terre pour le range de caps  '''
    ''' pour un vitesse donnee en noeuds et un temps en s '''
    ''' retourne un tableau des caps libres '''
    ''' une valeur merlibreglobale=1 si pas de terres dans le range des caps'''
    ''' la carte vr  des caps explores et les segments explores'''    
    pointsnp=np.zeros((len(rangecaps),2)) 
    segmentsfolium=[]
    capslibres=[]
    merlibreglobale=1 
    for i in range(len(rangecaps)) :
            cap=rangecaps[i]
            pointsnp[i]=[y0+vitesse*temps/3600/60*math.cos(cap*math.pi/180), x0+vitesse*temps/3600/60*math.sin(cap*math.pi/180)/math.cos(y0*math.pi/180)]
    cartevr=chargecarte_points(pointsnp)
    for i in range (len(pointsnp)): 
            trait=[[y0,x0],pointsnp[i]]
            res=intersect(trait,cartevr)
            segmentsfolium.append([trait,res])
            merlibreglobale*=res
            if res==1:
                capslibres.append(rangecaps[i])
           
    return capslibres,merlibreglobale,cartevr,segmentsfolium


    
def extrait_terres(lat,lng,pas,mask):
    # 1) on constitue la liste des carres
    # print(lat)
    terre=[]
    delta=1/pas
    for i in range(pas):
        for j in range(pas):
                if mask[j,i]==1:
                    terre.append([                        
                        [round(lat-j*delta,5),round(lng+(i*delta),5)]\
                       ,[round(lat-j*delta,5),round(lng+(i+1)*delta,5)]\
                        ,[round(lat-(j+1)*delta,5),round(lng+(i+1)*delta,5)]\
                        ,[round(lat-(j+1)*delta,5),round(lng+i*delta,5)]\
                        ,[round(lat-j*delta,5),round(lng+i*delta,5)]])
                    
    # print(len(terre))
    # print (terre[0:2])
    
    polygone_shp=[]
    for i in range (len(terre)):
        polygone_shp.append(Polygon(terre[i]))
    polygonglobal=unary_union(polygone_shp)     
    listeglobale=[]
    try:
     
        nbpoly=len(polygonglobal.geoms)
        for i in range(nbpoly):
            # a=np.array((polygonglobal[i].exterior.coords.xy))
            a=np.array((polygonglobal.geoms[i].exterior.coords.xy))
            Y=(a[0].reshape(-1,1))
            X=(a[1].reshape(-1,1))
            points=np.concatenate((Y,X),axis=1)
            listepoints=[arr.tolist() for arr in (points)]
            listeglobale.append(listepoints)
    except:
        # print ('un seul polygone')  
        #print(polygonglobal) 
        a=np.array(polygonglobal.exterior.coords.xy)
        Y=a[0].reshape(-1,1)
        X= a[1].reshape(-1,1)
        points=np.concatenate((Y,X),axis=1)
        #print(points)

        listepoints=[arr.tolist() for arr in (points)]
        listeglobale.append(listepoints)
    return listeglobale








def securite(polygon,marge):
    
    '''definit un polygone avec une marge de securite sur le polygone de base'''
    polygon_sh=Polygon(polygon).buffer(marge)
    a=np.array((polygon_sh.exterior.coords.xy))
    Y=(a[0].reshape(-1,1))
    X=(a[1].reshape(-1,1))
    polyline=np.concatenate((Y,X),axis=1)
    return polyline  


def securite2(multipolyline,marge):
    ''' definit des marges de securité sur une multipolyline'''
    '''retourne des multipolylines incluant la marge de securite'''
    
    polylines=[]
    for i in range (len (multipolyline)):
        polygon=multipolyline[i]
        polygon_sh=Polygon(polygon).buffer(marge)
        a=np.array((polygon_sh.exterior.coords.xy))
        Y=(a[0].reshape(-1,1))
        X=(a[1].reshape(-1,1))
        polyline=list(np.concatenate((Y,X),axis=1))
        polylines.append(polyline)
    return polylines   


def fleche2(y,x,cap,l,couleur,m):
    '''Dessine une fleche se terminant au point y,x suivant un cap avec une longueur l dans la carte m '''
    yfin=y+l*math.cos(cap*math.pi/180)
    xfin=x+l*math.sin(cap*math.pi/180)
    yfin2=yfin+l*0.1*math.cos((cap+30)*math.pi/180)
    xfin2=xfin+l*0.1*math.sin((cap+30)*math.pi/180)
    yfin3=yfin+l*0.1*math.cos((cap-30)*math.pi/180)
    xfin3=xfin+l*0.1*math.sin((cap-30)*math.pi/180)    
    fleche=[[[y,x],[yfin,xfin],[yfin2,xfin2],[yfin,xfin],[yfin3,xfin3]]]
    folium.PolyLine (fleche,color=couleur).add_to(m)
    return None


def point_terre(listept,carte):
    '''listept est une liste de points sous forme de np.array'''
    '''cartevr est une liste de polygone sous forme de liste de liste de points'''
    '''res est un np.array de points'''
    res=np.zeros(len(listept))
    i=0
    for pt in listept:
        point=Point(pt)
        for polygon in carte:
            polygon_sh=Polygon(polygon)
            if point.within(polygon_sh):
                res[i]=1
        i+=1 
    return res     
    
    
    
def point_terre2(y,x,cartevr):
    '''y x est un point '''
    '''cartevr est une liste de polygone sous forme de liste de liste de points'''
    '''res est un np.array de points le resultat est 0 si terre '''
    
    point=Point(y,x)
    k=1
    for polygon in cartevr:
        polygon_sh=Polygon(polygon)
        if point.within(polygon_sh):
                 k*=0
    return k  


def sailpenalite(tws):
    '''retourne la penalite en secondes ou la vitesse est reduite interpolation spline'''
    t = (tws-lws)/(hws-lws)
    if tws<lws:
        res=lwtimer
    if tws>hws:
        res=hwtimer
    else:                                                                                       
        res=(1-t)*((1-t)*lwtimer + t*((1-t)*lwtimer+t*hwtimer))+t*((1-t)*((1-t)*lwtimer+t*hwtimer)+t*(hwtimer))
    return res

def tackpenalite(tws):
    '''retourne la penalite en secondes ou la vitesse est reduite interpolation spline'''
    t = (tws-lws)/(hws-lws)
    if tws<lws:
        res=tackprolwtimer
    if tws>hws:
        res=tackprohwtimer
    else:                                                                                       
        res=(1-t)*((1-t)*tackprolwtimer + t*((1-t)*tackprolwtimer+t*tackprohwtimer))+t*((1-t)*((1-t)*tackprolwtimer+t*tackprohwtimer)+t*(tackprohwtimer))
    return res

def gybepenalite(tws):
    '''retourne la penalite en secondes ou la vitesse est reduite interpolation spline'''
    t = (tws-lws)/(hws-lws)
    if tws<lws:
        res=gybeprolwtimer
    if tws>hws:
        res=gybeprohwtimer
    else:                                                                                       
        res=(1-t)*((1-t)*gybeprolwtimer + t*((1-t)*gybeprolwtimer+t*gybeprohwtimer))+t*((1-t)*((1-t)*gybeprolwtimer+t*gybeprohwtimer)+t*(gybeprohwtimer))
    return res


# def sailpenalite0(tws):
#     '''retourne la penalite en secondes ou la vitesse est reduite interpolation lineaire'''
#     pt=min( max(lwtimer +(tws-lws)/(hws-lws)*(hwtimer-lwtimer),lwtimer),hwtimer)
#     # *(1-tackprolwratio)
#     return pt  

# def tackpenalite0(tws):
#     '''retourne la penalite en secondes ou la vitesse est reduite interpolation lineaire'''
#     pt=min( max(tackprolwtimer +(tws-lws)/(hws-lws)*(tackprohwtimer-tackprolwtimer),tackprolwtimer),tackprohwtimer)
#     # *(1-tackprolwratio)
#     return pt  


# def gybepenalite0(tws):
#     '''retourne la penalite en secondes ou la vitesse est reduite interpolation lineaire'''
#     pt=min( max(gybeprolwtimer +(tws-lws)/(hws-lws)*(gybeprohwtimer-gybeprolwtimer),gybeprolwtimer),gybeprohwtimer)
#     # *(1-tackprolwratio)
#     return pt  

def peno_stamina(manoeuvre,coefboat,tws):
    ''' donne la perte de stamina en fonction de manoeuvre et de la vitesse du vent'''
    if tws<10:
        coefwind=1+tws*0.02
    elif (tws>=10 and tws<=20):
        coefwind=1.2+(tws-10)*0.03
    elif (tws>20 and tws<30):
        coefwind=1.5+(tws-20)*0.05    
    else :
        coefwind = 2
    if (manoeuvre=='gybe' or manoeuvre=='tack'):
        coefmnvr=10
    else:
        coefmnvr=20
    return coefwind*coefmnvr*coefboat


def recup_stamina(T,tws): 
    ''' T en secondes '''
    ''' approximation lineaire en atttendant mieux'''
    points=T/(tws/3+5)/60
    return points

def recherche (twa,tab_twa):
    ''' recherche l'indice d'une twa ou tws dans le tableau '''
    k=0
    while (twa > tab_twa[k]):
        k+=1
    return k





def f_route (y0,x0,y1,x1,isoglobal,numero_point):
    ''' calcule la route a partir du tableau general des points et du dernier point le plus pres '''
    ''' utilise un dictionnaire pour remonter le chemin'''
    ''' retourne un tableau des points '''
    tabpoints= isoglobal[:,3:5]    
    tabpoints=(tabpoints[np.where(tabpoints[:,1]!=0)]).astype (int)
    dico= dict(zip(tabpoints[:,1],tabpoints[:,0]))  # creation du  dictionnaire de tous les points meres 
   
    #utilisation du dictionnaire
    a=numero_point                                   # numero dernier point
    route = [a]                                     # initialisation avec l'indice du point le plus pres dans le dernier isochrone
    while a!=0:
        a = int(dico[a])
        route.append(a)                             # route contient les indices successifs des points a emprunter a l'envers
    route.reverse()  
    chemin=np.zeros((len(route)+1,2))               # on initialise
    i=0
    for n in route:                                 # on reconstitue le tableau des points a partir 
        chemin[i]=isoglobal[n,0],isoglobal[n,1]
        i+=1
    chemin[i] =[y1,x1]                              # on rajoute l'arrivee -- chemin est le tableau des points de l itineraire a suivre 
    # print(route2)
    return chemin,route


def exploitation_routage(y0,x0,y1,x1,isoglobal,tmin,numero_point):
    ''' a partir de isoglobal et du numero du dernier point '''
    ''' retourne la route suivie et decoupe les isochrones dans les terres''' 
    # print('on est dans l exploitation du routage')
    chemin,route=f_route(y0,x0,y1,x1,isoglobal,numero_point) 
    chemincomplet=detail(chemin,y1,x1)
    
    noir=isoglobal[np.where(isoglobal[:,2]%6!=0) ]                                         # on garde que les isochrones non modulo6 
    coupuresnoir1       =np.where(np.diff(noir[:,2],1) >0)                                 # coupure suivant les numeros d iso 
    coupuresnoir2       =np.where(np.diff(noir[:,5],1) >1)                                 # coupure suivant la numerotation dans les isos
    coupuresnoir=np.asarray(sorted(list(set(coupuresnoir1[0])|set(coupuresnoir2[0]))))     # on combine les 2 sets on transforme en liste, on trie et on transforme en np
    noir=np.split(noir[:,0:2],coupuresnoir+1)                                              # coupure suivant le numero d'isochrone nparray
    noir=[arr.tolist() for arr in noir] 
    
    blanc=isoglobal[np.where(isoglobal[:,2]%6==0) ]                                        # on garde que les isochrones modulo6 
    coupuresblanc1       =np.where(np.diff(blanc[:,2],1) >0)
    coupuresblanc2       =np.where(np.diff(blanc[:,5],1) >1)                               # c donne la position des coupures sur les isochrones
    coupuresblanc=np.asarray(sorted(list(set(coupuresblanc1[0])|set(coupuresblanc2[0]))))  # on combine les 2 sets on transforme en liste, on trie et on transforme en np
    blanc=np.split(blanc[:,0:2],coupuresblanc+1)                                           # coupure suivant le numero d'isochrone nparray
    blanc=[arr.tolist() for arr in blanc] 
    
    return chemin,chemincomplet,route,noir,blanc 


def nb_virt(tab):
    '''retourne le nombre de virements dans un tableau constitue de 0 et de 1'''
    virt=0
    for i in range(len(tab)-1):
        if tab[i+1]!=tab[i]:
            virt+=1
    return virt        


def digits3(a):
    '''transforme un nombre inferieur a 999 en chaine sur 3 caracteres'''
    if a>100:
        res=str(a)
    if a>9 and a<100:
        res='0'+str(a)
    if a<10:
        res='00'+str(a)
    return res    
   
# def config_13virt(nbpos,nbvrt):
#     ''' cherche les differentes configurations de virement de bord pour nbpos positions postives et nbvrt nb de virements '''
#     tableau=[]
#     for i in range (2**13,2**14-1,1):
#         a=str( "{0:b}".format(i))
#         tab=np.array([int(a[1]),int(a[2]),int(a[3]),int(a[4]),int(a[5]),int(a[6]),int(a[7]),int(a[8]),int(a[9]),int(a[10]),int(a[11]),int(a[12]),int(a[13])])
#         if np.sum(tab)==nbpos and nb_virt(tab)<nbvrt+1:
#             tableau.append(list(tab))
#     for i in range (len(tableau)):
#         for j in range (len (tableau[i])): 
#             if tableau [i][j]==0:
#                 tableau [i][j]=-1
            
#     return tableau


def cherchevoile(polairesjson,n):
    if n>10:
        auto=' Auto'
    else:
        auto=' Man'
    n=n%10    
    typevoiles          = []
    nbvoiles       = len(polairesjson['polar']['sail'])
    for i in range(nbvoiles) :
        typevoiles.append( polairesjson['polar']['sail'][i]['name'])
    typevoiles.append('Na')    
    print(typevoiles)    
    typevoile =typevoiles[n-1]
    return typevoile,auto


if __name__ == '__main__':
    twao=112
    tws=8.4
    nbvoiles=7
    voile_utilisee (twao,tws,voileant,tab_twa,tab_tws,toutespolaires,nbvoiles)
        