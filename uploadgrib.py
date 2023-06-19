# uploadgrib3
# coding: utf-8

#le debut de chargement des gribs intervient en heure UTC à
# 9h30(gfs06) - 15h30(gfs12) -  21h30(gfs18) - 03h30 (gfs00)
# en heure d'hiver
# 10h30(gfs06) - 16h30(gfs12) -  22h30(gfs18) - 04h30 (gfs00)

# les gribs complets sont disponibles en heure UTC à
# 11h(gfs06) - 17(gfs12) -  23(gfs18) - 05 h (gfs00)

# les gribs complets sont disponibles en heure d'hiver à
# 12h(gfs06) - 18(gfs12) -  00(gfs18) - 06 h (gfs00)
# les gribs complets sont disponibles en heure d'ete à
# 13h(gfs06) - 19(gfs12) -  01(gfs18) - 07 h (gfs00)


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
import numpy as np
import requests
import xarray as xr
from fonctions2023 import *



tic=time.time()
ticstruct = time.localtime()
utc = time.gmtime()
decalage = ticstruct[3] - utc[3]


# gestion des repertoires
basedir = os.path.abspath(os.path.dirname(__file__))

if basedir=='/home/jp':  
    #basedir='/home/jp/vrouteur'                                    # cas ou le programme est declenche a partir d'une tache cron 
    filename=basedir+"/gribsgfs/derniergrib.npy"
    if os.path.exists(filename)==False:                            # on teste si on est dans vrouteur sinon on est dans notebooks
        basedir='/home/jp/vrouteur_2023_5'
        filename='/home/jp/gribs/gribsgfs/derniergrib.npy'

else:
    basedir='/home/jp/gribs'




iprev = []                 
for a in range(0, 387, 3):                              # Construit le tuple des indexs des fichiers maxi 387
    iprev += (str(int(a / 100)) + str(int((a % 100) / 10)) + str(a % 10),)


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






# recherche du dernier grib disponible
# # *************************************************************************************
# avec tic 
# date_tuple           = time.gmtime(tic)             # transformation en tuple utc
# date_formatcourt     = time.strftime("%Y%m%d", time.gmtime(tic))
# dateveille_tuple     = time.gmtime(tic-86400) 
# dateveille_formatcourt=time.strftime("%Y%m%d", time.gmtime(tic-86400))











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
        filename384=basedir+"/gribsgfs/gfs_"+dateveille_formatcourt+"-18.npy"
        tig384=time.mktime(datetime(dateveille_tuple[0],dateveille_tuple[1],dateveille_tuple[2],18,0,0).timetuple())+decalage*3600
    elif (mn_jour_utc<700):   
        filename384=basedir+"/gribsgfs/gfs_"+date_formatcourt+"-00.npy"
        tig384=time.mktime(datetime(date_tuple[0],date_tuple[1],date_tuple[2],0,0,0).timetuple())+decalage*3600
    elif (mn_jour_utc<1060): 
        filename384=basedir+"/gribsgfs/gfs_"+date_formatcourt+"-06.npy"
        tig384=time.mktime(datetime(date_tuple[0],date_tuple[1],date_tuple[2],6,0,0).timetuple())+decalage*3600
    elif (mn_jour_utc<1420):   
        filename384=basedir+"/gribsgfs/gfs_"+date_formatcourt+"-12.npy"
        tig384=time.mktime(datetime(date_tuple[0],date_tuple[1],date_tuple[2],12,0,0).timetuple())+decalage*3600
    else:    
        filename384=basedir+"/gribsgfs/gfs_"+date_formatcourt+"-18.npy"
        tig384=time.mktime(datetime(date_tuple[0],date_tuple[1],date_tuple[2],18,0,0).timetuple())+decalage*3600

    # nom du fichier suivant le 384
    date     = time.strftime("%Y%m%d", time.gmtime(tig384 +21600))
    heure    = time.strftime("%H", time.gmtime(tig384+21600))
    filename = basedir+"/gribsgfs/gfs_"+date+"-"+heure+".npy"
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



def chargement_384():
    '''Charge le fichier  complet 384 existant qui servira de base '''
   
   # filename384,tig384,filename,tig,status=fileNames()
    date  = time.strftime("%Y%m%d", time.gmtime(tig384 ))
    heure = time.strftime("%H", time.gmtime(tig384))
    GR = np.zeros((len(iprev), 181, 360), dtype=complex)    # initialise le np array de complexes qui recoit les donnees  
   
    if os.path.exists(filename384) == False:                # si ce fichier n'existe pas deja
        print('Chargement du fichier 384 {}'.format (filename384))
             
        for indexprev in range(len(iprev)):  # recuperation des fichiers de 0 a 384 h
            prev = iprev[indexprev]
            url = "https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_1p00.pl?file=gfs.t" + heure + "z.pgrb2.1p00.f" + \
                prev + "&lev_10_m_above_ground=on&all_var=on&leftlon=" \
                + str(leftlon) + "&rightlon=" + str(rightlon) + "&toplat=" + str(toplat) + "&bottomlat=" + str(
                bottomlat) + "&dir=%2Fgfs." + date + "%2F" + heure+"%2Fatmos"

            nom_fichier = "grib_" + date + "_" + heure + "_" + prev   # nom sous lequel le  fichier est sauvegarde provisoirement
            try:       
                urlretrieve(url, nom_fichier)   
               
                ds = xr.open_dataset(nom_fichier, engine='cfgrib')    # exploitation du fichier et mise en memoire dans GR
                GR[indexprev] = ds.variables['u10'].data + ds.variables['v10'].data * 1j
                os.remove(nom_fichier)                  # On efface le fichier pour ne pas encombrer
                residuel=nom_fichier + '.90c91.idx'
                if os.path.exists(residuel) == True: 
                    os.remove(residuel)   # On efface le fichier residuel
                residuel=nom_fichier + '.4cc40.idx'
                if os.path.exists(residuel) == True: 
                    os.remove(residuel)   # On efface le fichier residuel
                residuel=nom_fichier + '.923a8.idx'
                if os.path.exists(residuel) == True: 
                    os.remove(residuel)   # On efface le fichier residuel 
                date_p_s=time.strftime("%d %b %Hh", time.gmtime(tig384+indexprev*3*3600))
                print(' Enregistrement  384  {}-{} + {} heures soit {} '.format(date,heure,prev,date_p_s))  # destine a suivre le chargement des previsions
            except HTTPError :
                print ('La Prévision {} est non disponible '.format(prev) )
        indice384=indexprev 
        # GR=np.concatenate((GR,GR[:,:,0:1]), axis=2)   #mise en place de la prevision longitude 360 =0
        
        sauvegardeGrib(filename384,GR,tig384,indice384,tig384+13200)   # on sauvegarde sous forme d'un fichier npy et json 

    else :  
        print('Le fichier {} existe deja '.format(filename384))
    return None





def chargementGrib():
    '''Procedure complete '''
    '''charge le 384 s'il n'est pas deja charge ''' 
    '''Cherche s'il existe un grib avec des previsions plus recentes que l on peut charger  '''   
    global filename384,tig384
    filename384,tig384,filename,tig,status=fileNames()
       
    if os.path.exists(filename384) == False:
        chargement_384() 

    date  = time.strftime("%Y%m%d", time.gmtime(tig ))
    strhour = time.strftime("%H", time.gmtime(tig))

    if status!='chargeable':  # on ne peut pas charger un nouveau fichier
        print('Le dernier grib disponible est le grib complet {}\n'.format(filename384))
        # on va copier vers
        filenamejson=filename384.split('.')[0]+'.json'
        filename2=basedir+"/gribsgfs/derniergrib.npy"
        
        filename3=basedir+"/gribsgfs/derniergrib.json"
        shutil.copy(filename384,filename2)
        shutil.copy(filenamejson,filename3)

    else:
        print('Il existe un grib partiellement disponible  ',filename)
        print()
        print('On charge de nouvelles previsions pour ',filename)
        # on commence par recuperer le 384 pour pouvoir le completer avec les dernieres previsions
        GR,tig,indice,avail_ts  =recupereGrib (filename384)



        if os.path.exists(filename) == True:            # si le nouveau fichier existe deja
            # on le charge pour recuperer l'indice de depart
           GR,tig,indice,avail_ts  =recupereGrib (filename)


        else :                                          # si le nouveau fichier n a pas encore ete cree
            GRN = np.zeros((len(iprev), 181, 360), dtype=complex)    # initialise le np array de complexes qui recevra les donnees  
            tign=tig+21600
            indice=-1
        # on peut commencer le chargement a l'indice suivant ou a l'indice 0 s il n'y avait rien de charge

            test='Debut'
            indexprev=indice+1                                       # On commence a tester le chargement au nouvel indice
            while test!='fin' and indexprev<len(iprev):
                prev = iprev[indexprev]
            
                url = "https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_1p00.pl?file=gfs.t" + strhour + "z.pgrb2.1p00.f" + \
                    prev + "&lev_10_m_above_ground=on&all_var=on&leftlon=" \
                    + str(leftlon) + "&rightlon=" + str(rightlon) + "&toplat=" + str(toplat) + "&bottomlat=" + str(
                    bottomlat) + "&dir=%2Fgfs." + date + "%2F" + strhour+"%2Fatmos"

                nom_fichier = "grib_" + date + "_" + strhour + "_" + prev   # nom de  fichier provisoire

                try:       
                    urlretrieve(url, nom_fichier)
                    ds = xr.open_dataset(nom_fichier, engine='cfgrib')
                    GRN[indexprev ] = ds.variables['u10'].data + ds.variables['v10'].data * 1j
                    os.remove(nom_fichier) 
                                    # On efface le fichier pour ne pas encombrer
                    residuel=nom_fichier + '.90c91.idx'
                    if os.path.exists(residuel) == True: 
                        os.remove(residuel)   # On efface le fichier residuel
                    residuel=nom_fichier + '.4cc40.idx'
                    if os.path.exists(residuel) == True: 
                        os.remove(residuel)   # On efface le fichier residuel
                    residuel=nom_fichier + '.923a8.idx'
                    if os.path.exists(residuel) == True: 
                        os.remove(residuel)   # On efface le fichier residuel

                    print ("\tEnregistrement nouveau  grib  prévision +{}h  {} ".format(prev,time.strftime("%Y%m%d %H", time.gmtime(tign )) ) )
                    #print ('243 dernier indice a jour',indexprev )
                    indice=indexprev
                except HTTPError :
                    test='fin'
                    if indexprev==0:     #  arrive seulement dans le cas d un probleme NOAA chargement impossible 
                        print("\tLe nouveau grib n'est pas encore  disponible")
                    else :    # on complete GRN avec les valeurs de GR entre indexprev et 126 (378 )
                    # print ('249 dernier indice a jour',indexprev )
                        GRN[(indexprev):127,:,:]=np.copy(GR[(indexprev+2):129,:,:])   # on fait une copie et non une vue nb le 127 n'est pas copié
                        GRN[-2:,:,:]=GRN[-3,:,:]       # comme il manque dans GR les valeurs des deux derniers on copie -3 dans -2 et -1 
                        indice=indexprev-1    # la derniere prevision indexprev a ete un echec
                        print ('\tPrevisions completees par les valeurs de lancien grib de +{}h à +{}h'.format(iprev[indexprev],126*3) )
                indexprev+=1         
       
            sauvegardeGrib(filename,GRN,tign,indice,tic)
            filename2=basedir+"/gribsgfs/derniergrib.npy"
            sauvegardeGrib(filename2,GRN,tign,indice,tic)          #sauvegardé egalement sous le nom de dernier grib   
    return None


def nettoyage():
    '''efface les fichiers plusvieux que le delta de temps '''
    delta=3600*24
    dir=basedir+'/gribsgfs'   #repertoire des gribs
    for fichier in os.listdir(dir):
        mtime=os.path.getmtime(dir+'/'+fichier)
        #print(fichier,time.time()- mtime)
        # print(mtime)
        #print(time.time()-mtime)
        if time.time()-mtime >delta :
            os.unlink(dir+'/'+fichier)
    print('Effacement des fichiers de plus de 24h')        
    return None 











if __name__ == '__main__':

    
    chargementGrib()
    nettoyage()
    
    # recuperation des dernieres valeurs pour test  
    filename=basedir+"/gribsgfs/derniergrib.npy"
    GR,tig,indice,avail_ts   = recupereGrib (filename)

    # calcul d'une prevision 
    latitude='045-00-00-N'
    longitude='003-00-00-W'
    d = chaine_to_dec(latitude, longitude)  
    tic=time.time()
    tic_formate=time.strftime(" %d %b %Y %H:%M:%S ", time.localtime(tic))
    dateprev_s=tic
    dateprev_formate_local = time.strftime(" %d %b %Y %H:%M:%S ", time.localtime(dateprev_s))
    vit_vent_n, angle_vent = prevision(tig, GR,dateprev_s, d[0], d[1])
    print('\tLe{} heure Locale Pour latitude {:6.2f} et longitude{:6.2f} '.format(dateprev_formate_local, d[0], d[1]))
    print('\t Calcul 1 Angle du vent   {:6.3f} ° Vitesse {:6.3f} Noeuds'.format(angle_vent,vit_vent_n))
    


   