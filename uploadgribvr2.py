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




import math
import sys
import time
import os
import urllib.request
import requests
import numpy as np
import xarray as xr
from datetime import datetime
from datetime import timezone
from urllib.request import urlretrieve
from urllib.error import HTTPError


from fonctions2023   import *
from fonctions2023_2 import *



# gestion des repertoires
basedir = os.path.abspath(os.path.dirname(__file__))

if basedir=='/home/jp':  
    #basedir='/home/jp/vrouteur'                                    # cas ou le programme est declenche a partir d'une tache cron 
    filename=basedir+"/gribsvr/derniergrib.npy"
    if os.path.exists(filename)==False:                            # on teste si on est dans vrouteur sinon on est dans notebooks
        basedir='/home/jp/vrouteur_2023_5'
        filename='/home/jp/gribs/gribsgfs/derniergrib.npy'

else:
    basedir='/home/jp/gribs'


t0=time.time()
print()
print()
print('***************************************************************************************************************')
print ('Mise a jour du  {}'.format(time.strftime(" %d %b %Y %H:%M:%S ", time.localtime(time.time())))) 
print('***************************************************************************************************************')




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



url='https://static.virtualregatta.com/winds/live/references.json'
filelocal1= basedir+'/gribsvr/ventsvr.txt'
urlretrieve(url, filelocal1)  # recuperation des fichiers
# print('{}  ventsvr.txt chargé!\n'.format(filelocal1)) 
# ouverture du fichier en local 

with open(filelocal1, "r") as fichier:                                           #fichier general definissant les fichiers a charger
    textevent=fichier.read()
listegribs=eval(textevent)    
references=listegribs['references']  
# print(len(references))
# print()
# print(references)
# for i in range (len(references)):
#     print(references[i][0]['reference'],references[i][0]['valid_time'] )

# constitution de la liste des gribs avec leur tig
listegribs2=[]
for i in range (len(references)):
    tig=references[i][0]['reference_ts']
    grib=['gfsvr_'+time.strftime("%Y%m%d_%H", time.gmtime(tig))+'.npy',tig]
    if grib not in listegribs2 :        
        listegribs2.append(grib)

print ('listegribs2 ',listegribs2)        
#remplissage des gribs
for k in range (len(listegribs2)):

    # print('\n Grib   a peupler {} \n*************************************************************' .format(  'gribsvr/'+str(listegribs2[k][0])))
    tig=listegribs2[k][1]
    # print('live/'+time.strftime("%Y%m%d/%H", time.gmtime(tig))+'/006.wnd')
    GR = np.zeros((129, 181, 360), dtype=complex)    # initialise le np array de complexes qui va recevoir les donnees 
    indices=[]

# tableau de toutes les references de vent
    avail_ts=[]
    for i in range(len(references)): 
        
        if(references[i][0]['reference_ts'])==tig   :                        # on ne s occupe que des fichiers de meme valeur de tig
            
            tig_formate=time.strftime("%m-%d-%H ", time.gmtime(tig))
            avail_tsi=references[i][0]['avail_ts'] 
            avail_ts.append(avail_tsi)
            path=references[i][0]['rel_path']                                            # c est pour laller chercher le fichier VR
            heure_prev=references[i][0]['valid_ts']
            ecart=(heure_prev-tig)/3600
            indice=int(ecart//3) 
            indices.append(indice)                                                          # c est l indice de temps dans mon grib GR
            heure_prev_formate=time.strftime(" %d %b %Y %H:%M:%S ", time.gmtime(heure_prev))
            # impression des caracteristiques du grib qui va etre créé
            # print( 'Enregistrement Grib : {},avail_ts= {}  heure_prev :{}, ecart :{:4.0f}h, indice :{}, path :{} '.format (tig_formate,avail_tsi,heure_prev_formate,ecart,indice,path))
            furl=f'https://static.virtualregatta.com/winds/'+path
            r = requests.get(furl)
            buf=r.content
            open("wind.bin", "wb").write(buf)
            uv=np.frombuffer(buf, dtype=np.int8).reshape((181,360,2))
            uv=uv.astype(float)
            uv=np.sign(uv)*(uv/8)**2
            uv=np.concatenate((uv[:,180:],uv[:,:180],),axis=1)    # maintenant on est dans le meme schema que NOAA origine en 0 +90 
            GR[indice]=(uv[:,:,0]+uv[:,:,1]*1j )/3.6              # on remplit GR et on transforme en m/s pour etre homogene avec NOAA 
    # on charge le 06        
    # print('live/'+time.strftime("%Y%m%d/%H", time.gmtime(tig))+'/006.wnd')  
    
    path='live/'+time.strftime("%Y%m%d/%H", time.gmtime(tig))+'/006.wnd'
    # print(path)
    heure_prev=tig+6*3600
    ecart=6
    indice=int(ecart//3) 
    indices.append(indice)                                                          # c est l indice de temps dans mon grib GR
    heure_prev_formate=time.strftime(" %d %b %Y %H:%M:%S ", time.gmtime(heure_prev))
    # impression des caracteristiques du grib qui va etre créé
    # print( 'Enregistrement Grib : {},avail_ts= {}  heure_prev :{}, ecart :{:4.0f}h, indice :{}, path :{} '.format (tig_formate,avail_ts[0],heure_prev_formate,ecart,indice,path))
    
    furl=f'https://static.virtualregatta.com/winds/'+path
    r = requests.get(furl)
    buf=r.content
    open("wind.bin", "wb").write(buf)
    uv=np.frombuffer(buf, dtype=np.int8).reshape((181,360,2))
    uv=uv.astype(float)
    uv=np.sign(uv)*(uv/8)**2
    uv=np.concatenate((uv[:,180:],uv[:,:180],),axis=1)    # maintenant on est dans le meme schema que NOAA origine en 0 +90 
   
    GR[indice]=(uv[:,:,0]+uv[:,:,1]*1j )/3.6              # on remplit GR et on transforme en m/s pour etre homogene avec NOAA 

    # on sauvegarde dans un fichier filename   
    filename=basedir+'/gribsvr/'+str(listegribs2[k][0])
    sauvegardeGrib(filename,GR,tig,indices,avail_ts[0])    
    
    
    
print()    
print('Liste des gribs chargés avec leurs tig ',listegribs2)  

# reconstitution du grib global


# Chargement et ouverture du premier npy 
#****************************************
i=0
filename =basedir+'/gribsvr/'+str(listegribs2[i][0])
GR0,tig0,indices0,avail_ts =recupereGrib (filename)
GRDER  = np.copy(GR0)        # initialise le np array de complexes qui va recevoir les donnees 
indicemax=max(indices0)

# print('ligne 190 indices0',indices0)
# print('ligne 190 indicemax',indicemax)
# Chargement et ouverture du deuxieme npy s'il y a 
#*************************************************


if len(listegribs2)>1:                                                     # si deux gribs
    i=1

    filename =basedir+'/gribsvr/'+str(listegribs2[i][0])                            # on ouvre le fichier 
    GR1,tig1,indices1,avail_ts1 =recupereGrib (filename)
    max0=max(indices0)
    min1=min(indices1)
    max1=max(indices1)

    # print('ligne 205 indices0',indices0)
    # print('ligne 206 indices1',indices1)
    
    
    if tig1>tig0:
    
        decalage=listegribs2[1][1]-listegribs2[0][1]                   # decalage entre les deux tigs en secondes 
        decalageindice=int(decalage/3600/3)                            # decalage entre les indices des 2 gribs 
        indices1_decale=list(np.array(indices1)+decalageindice)        # mise en concordance des indices du deuxieme grib avec ceux du premier 
        # print ('indices1_decale ',indices1_decale)
        for j in range (len(indices1_decale)):
            GRDER[indices1_decale[j],:,:]=GR1[indices1[j],:,:]         # si il y a de nouvelles valeurs on remplace dans l ancien  
        
        delta=tig0+(12*3600)-avail_ts1
        coeff2=(t0 - avail_ts1)/(tig0+12*3600 -avail_ts1)
        coeff1= 1-coeff2
      
    # Maintenant on interpole  entre l indice 4 de l ancien et l'indice 5 qui est du nouveaugrib
        #GRDER est sur la base de l ancien grib pour garder les premieres valeurs
        # ( l'indice 4 est l'indice 4 de l'ancien)
        GRDER[4,:,:]=GR0[4,:,:]*coeff1 +  GR1[2,:,:]*coeff2
        indicemax=max(indices1_decale)
        # print ('indicemax l229',indicemax)
       



###################################################################################
#### Recuperation du grib NOAA pour completer au dela de l indice max et sauvegarde
###################################################################################
filename=basedir+"/gribsgfs/derniergrib.npy"
GRNOAA,tigNOAA,indice,avail_ts  = recupereGrib (filename)   

# print('tig Vr',time.strftime(" %d %b %Y %H:%M:%S ", time.gmtime(tig0)))
# print('tig noaa ',time.strftime(" %d %b %Y %H:%M:%S ", time.gmtime(tigNOAA)))
# print ('difference dindice',(tig0-tigNOAA)/3600/3)

deltaindice=int((tig0-tigNOAA)/3600/3)
print ('indicemax l 233',indicemax ) 
print ('GRDER',GRDER.shape)
print ('GRNOAA',GRNOAA.shape)

nouvelindice=int(indicemax+1-deltaindice)

if deltaindice==0 :
    GRDER[indicemax+1 :,:,:] = GRNOAA[indicemax+1  : ,:,:]        #normalement on remplace a partir de indicemax+1 mais par securite indice max        
else:
    GRDER[indicemax+1 :,:,:] = GRNOAA[indicemax+1+deltaindice: deltaindice,:,:]           

# print('GRDER',GRDER[62,15,22])
# print('GRNOAA',GRNOAA[62,15,22])


filename                 =basedir+'/gribsvr/derniergrib.npy'        # on sauvegarde dans un fichier  en l appelant dernier grib  
sauvegardeGrib(filename,GRDER,tig0,indices0,avail_ts)








def nettoyage():
    '''efface les fichiers plusvieux que le delta de temps '''
    delta=3600*24
    dir=basedir+'/gribsvr'   #repertoire des gribs
    for fichier in os.listdir(dir):
        mtime=os.path.getmtime(dir+'/'+fichier)
        # print(fichier)
        # print(mtime)
        # print(time.time()-mtime)
        if time.time()-mtime >delta :
            os.unlink(dir+'/'+fichier)
    print('Effacement des fichiers de plus de 24h')        
    return None 



if __name__ == '__main__':

    nettoyage()

    ###################################################################################
    #### Test de valeurs
    ###################################################################################




    ###########################################################################
    #### Recuperation des  gribs
    ############################################################################
   
    filename=basedir+"/gribsgfs/derniergrib.npy"
    GRNOAA,tigNOAA,indice,avail_ts = recupereGrib (filename)
  
    filename                      =basedir+'/gribsvr/derniergrib.npy' 
    GRVR,tigvr,indices,avail_ts =recupereGrib (filename)

    #tigvr,GRVR,filename,indices   = chargement_dernier_vr()
    # print('ligne 185', tigvr) 

    tigvr_formate_utc               = time.strftime(" %d %b %Y %H:%M:%S ", time.gmtime(tigvr))
    tig_formate_utc                 = time.strftime(" %d %b %Y %H:%M:%S ", time.gmtime(tig))

    

    y0=45
    x0=-3
    tsLastCalc=time.time()
    twscalc,twdcalc  =     prevision5 (tigvr,GRVR,tsLastCalc,y0,x0)        
    twsNOAA,twdNOAA  =     prevision5 (tigNOAA  ,GRNOAA  ,tsLastCalc,y0,x0)

    #########################################################################
    # Impressions de controle
    #########################################################################
    print ('\nVerification upload3 a t0 pour y0 = {:6.4f}  x0 = {:6.4f}'.format(y0,x0 ))   
    print ('Source                  twd       tws                \
        \n************************************* ')
    # print ('Jeu                   {:6.2f}   {:6.2f}            '.format(twdvr,twsvr))
    print ('Calculvr              {:6.2f}   {:6.2f}            '.format(twdcalc,twscalc))
    print ('CalculNOAA            {:6.2f}   {:6.2f}            '.format(twdNOAA,twsNOAA))
    print()

    tsLastCalc=time.time()+3600*24*12 
    twscalc,twdcalc  =     prevision5 (tigvr,GRVR,tsLastCalc,y0,x0)        
    twsNOAA,twdNOAA  =     prevision5 (tigNOAA  ,GRNOAA  ,tsLastCalc,y0,x0)

    #########################################################################
    # Impressions de controle
    #########################################################################
    print ('\nVerification upload3 a t0 +12j  pour y0 = {:6.4f}  x0 = {:6.4f}'.format(y0,x0 ))   
    print ('Source                  twd       tws                \
        \n************************************* ')
    # print ('Jeu                   {:6.2f}   {:6.2f}            '.format(twdvr,twsvr))
    print ('Calculvr              {:6.2f}   {:6.2f}            '.format(twdcalc,twscalc))
    print ('CalculNOAA            {:6.2f}   {:6.2f}            '.format(twdNOAA,twsNOAA))
    print()
