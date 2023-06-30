
var intl=new Intl.DateTimeFormat("fr-EU",{month:"2-digit",day:"2-digit", year:"2-digit",hour12: false,hour:"2-digit", minute:"2-digit" });
var intlhmn=new Intl.DateTimeFormat("fr-FR",{day:"2-digit",month:"2-digit", hour12: false,hour:"2-digit", minute:"2-digit" });
var intlhmn2=new Intl.DateTimeFormat("fr-FR",{ hour12: false,hour:"2-digit", minute:"2-digit" });

// fonction servant a relancer le calcul avec nouveau departs et arrivee
function itineraire(latdep,lngdep,ts,latar,lngar,dep,ari){
	console.log ('TEST4')
	url="vroutage?dep="+dep
	+"&ari="+ari+"&username="+username+"&teamname="+teamname+"&userid="+userid+"&urlbeta="+urlbeta
	+"&race="+race+"&y0="+latdep+"&x0="+lngdep+"&y1="+latar+"&x1="+lngar+"&ts="+ts+"&tws="+twsvr+"&twd="+twdvr+"&twa="+twa+"&rank="+rank+"&source=context" 
	console.log ('url'+url)
	document.location.href=url
}






function ajoutmarqueur(y0,x0)
        
        {   
            var texte= 'Nouveau marqueur';
            L.marker([y0,x0 ],    {icon: redIcon}).bindTooltip(texte).addTo(map); 
        }


var LeafletIcon=L.Icon.extend({
    options:{
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    shadowSize: [41, 41],
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34] 
            }
    });

    var greenIcon = new LeafletIcon({ iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png'});
    var blackIcon = new LeafletIcon({ iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-black.png'});    
    var redIcon   = new LeafletIcon({ iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png'});   
	var greyIcon   = new LeafletIcon({ iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-grey.png'});
	var predIcon   = new LeafletIcon({ iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png'}); 
	var pgreenIcon   = new LeafletIcon({ iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png'}); 

function popupbasique(page) {
	window.open(page,'Polaires','top=10,left=1000 ,width=1000, height=1000');
  }
  


function arrondi(a,n)
            {return(Math.round(a*10**n)/10**n);}


            function h_mn(sec)
			{   sec=sec
				h=Math.floor(sec/3600)	
				mn=Math.ceil((sec-3600*h)/60)
				s=sec-3600*h-60*mn 
				res=h+'h '+mn+'mn'
				return res
			}

			function h_mn2(sec)
			{   sec=sec
				h=Math.floor(sec/3600)	
				mn=Math.ceil((sec-3600*h)/60)
				s=sec-3600*h-60*mn 
				res=h+'h '+mn+'mn'
				return res
			}
			

            function deg_mn_(sec)
			{   sec=sec+15
				h=Math.floor(sec/3600)	
				mn=Math.ceil((sec-3600*h)/60)
				s=sec-3600*h-60*mn 
				res=h+'h '+mn+'mn'
				return res
			}

            function pos_dec_mn(pos)
			{  // transforme les degres decimaux en mn sec
			 	abs=Math.abs(pos)
				deg=Math.floor(abs)
				min=Math.floor((abs-deg)*60)
				sec=Math.round(((abs-deg)*60-min)*60)
				return deg+'°'+min+'mn'+sec+'s'
            }  
            
            function numero_point(sec)
            {
				//nombre isochrone a 10mn
				var nbiso_dixmn=72;
                if (sec<nbiso_dixmn*600)
                    {npt=Math.floor (sec/600)}
                else
                    {npt=Math.floor(sec/3600)+60}
                return npt+1;
            }


            function cap(x0,y0,x1,y1)
                {capi=90-(Math.atan((y1-y0)/(x1-x0+0.0000001))*180/3.1416);
                    if ((x1-x0)>0)
                        {capi=capi+180}
                return capi }   
                function pos_dec_mn(pos)
                    {   abs=Math.abs(pos)
                        deg=Math.floor(abs)
                        min=Math.floor((abs-deg)*60)
                        sec=Math.round(((abs-deg)*60-min)*60)
                        return deg+'°'+min+'mn'+sec+'s'
                    }    


			function recherche(tws,TWS)
			{
				var indice;
				for ( var i=0 ;i< TWS.length ;i++)
				{if (TWS[i]<=tws) {indice=i} }
				return indice
			}		

			function coeff_foil(twa,tws)
        
			{ var coeff1,coeff2,coeff3,coeff4
			  if ((twa>twaMin-twaMerge) && (twa<twaMax+twaMerge) && (tws>twsMin-twsMerge) && (tws<twsMax+twsMerge))
				{ if ((twa>twaMin-twaMerge) && (twa<twaMin))  {  coeff1=(twa-twaMin+twaMerge)/twaMerge   }  else coeff1=1
				  if ((twa>twaMax) && (twa<twaMax+twaMerge))  {  coeff2=(twa-twaMax)/twaMerge  }    else coeff2=1
				  if ((tws>twsMin-twsMerge) && (tws<twsMin))  {  coeff3=(tws-twsMin+twsMerge)/twsMerge  }     else coeff3=1
				  if ((tws>twsMax) && (tws<twsMax+twsMerge))  {  coeff4=(tws-twsMax)/twsMerge   }  else coeff4=1
				  coeff =1+(speedRatio-1)*coeff1*coeff2*coeff3*coeff4
				}
			  else {coeff=1}
			  return coeff  
			}
	 
			function vitessepolaire (twa,tws,foil=1,hull=1.003)
				{  var i=recherche(twa,TWA)
				   var j=recherche(tws,TWS)        // donne la valeur inferieure ou egale
				   dtws=TWS[j+1]-TWS[j]
				   dtwa=TWA[i+1]-TWA[i]
				   deltatwa= (twa-TWA[i])/dtwa
				   deltatws= (tws-TWS[j])/dtws
				   var vxx = new Array 
				   for (var k=0;k<voiles.length;k++)
					  {
						v00=voiles[k][i][j]
						v10=voiles[k][i+1][j]
						v01=voiles[k][i][j+1]
						v11=voiles[k][i+1][j+1]
						vx0=v00+(v10-v00)*deltatwa
						vx1=v01+(v11-v01)*deltatwa
						vxx[k]= vx0+(vx1-vx0)*deltatws
					  }
				   var coeff=(foil==1?coeff_foil(twa,tws):1)   
				   var vmax=Math.max(...vxx)*coeff*hull
				   
				   var indice = vxx.indexOf(Math.max(...vxx));
				   var res=[vmax,indice] 
				   //console.log ('vmax' +vmax)
				 return res
				}    
			


            function polinterpol2d(bateau,twa,tws)                            // ancienne fonction 
			{	// parametres : polaires du bateau twa et tws
			    var i_sup=l2.findIndex(element => element > twa);
				var j_sup=l1.findIndex(element => element > tws);				
				var twa_inf=l2[i_sup-1]
				var twa_sup=l2[i_sup]
				var tws_inf=l1[j_sup-1]
				var tws_sup=l1[j_sup]
				dx = twa-twa_inf 				// Ecart avec la valeur d'indice mini
				dy = tws-tws_inf
				deltax=twa_sup-twa_inf
				deltay=tws_sup-tws_inf
				fx1y1   = bateau[i_sup-1][j_sup-1]
				fx2y1   = bateau[i_sup][j_sup-1]			
				fx1y2   = bateau[i_sup-1][j_sup]			
				fx2y2   = bateau[i_sup][j_sup]			
				dfx     = fx2y1-fx1y1			
				dfy     = fx1y2-fx1y1			
				dfxy    = fx1y1+fx2y2-fx2y1-fx1y2				
				fxy     = dfx*dx/deltax  + dfy*dy/deltay + dfxy*dx*dy/deltax/deltay + fx1y1
				return fxy
			}




            function cvent(u,v) //retourne la vitesse du vent et sa force a partir de u et v
			{
				vit = Math.sqrt(u*u + v*v)
				angle= Math.acos(v/vit)*180/Math.PI+180;
				if (u<0)
				{angle=360-angle}
				vit*= 1.94384     // Vitesse en noeuds
				return [vit,angle]				
			} 

			function interpol2d(XX,t0,i_lat,i_lng)
			{			
				lat0    = Math.floor(i_lat)       // partie entiere
				lng0    = Math.floor(i_lng)
				//t0    = Math.floor(i_t)       // t0 est censé être un indice entier
				dec_lat = i_lat%1    				// partie decimale
				dec_lng = i_lng%1
                //console.log( 'lat0 '+ lat0 +' Lng0 '+lng0 +' t0 ' + t0)  
				fx1y1   = XX[t0][lat0][lng0]
				fx2y1   = XX[t0][lat0+1][lng0]
				fx1y2   = XX[t0][lat0][lng0+1]
				fx2y2   = XX[t0][lat0+1][lng0+1]
				dfx     = fx2y1-fx1y1
				dfy     = fx1y2-fx1y1
				dfxy    = fx1y1+fx2y2-fx2y1-fx1y2
				fxy     = dfx*dec_lat  + dfy*dec_lng + dfxy*dec_lat*dec_lng + fx1y1
				return fxy
			}

			function interpol3d(XX,i_t,i_lat,i_lng)
			{
				lat0    = Math.floor(i_lat)       // partie entiere
				lng0    = Math.floor(i_lng)
				t0      = Math.floor(i_t)
				dec_t   = i_t%1						// partie decimale				
				dec_lat = i_lat%1
				dec_lng = i_lng%1
				console.log ('Valeurs dans interpolation 3d lat0 '+lat0+' lng0 '+lng0+' dec_t '+dec_t+' dec_lat '+dec_lat+' dec_lng '+dec_lng)
				r1      = interpol2d(XX,t0,i_lat,i_lng)
				r2      = interpol2d(XX,t0+1,i_lat,i_lng)
				r       = r1+(r2-r1)*dec_t
				return r
			}

            function gvent (lat,lng ,t)
			{
			i_lat=lat-latini       // ecart avec la latitude du grib chargé
			i_lng=lng-lngini
			console.log(' ')	
			console.log ('************* Latitude  '+lat+' i_lat : '+i_lat)
			console.log ('************* Longitude ' +lng+' i_lng : '+i_lng)
			console.log(' ')
			i_t=(t-tig)/3600/3     // Ecart en heures avec le tig  modulo 3h
			u10=interpol3d(U10,i_t,i_lat,i_lng)	
			v10=interpol3d(V10,i_t,i_lat,i_lng)	
			res=cvent(u10,v10) 		// vitesse=res[0], angle=res[1] 
			console.log('resultat'+ res)
			return res	

			}

            function ftwa(cap,dvent)
			{//twa en valeur absolue
			return 180-Math.abs(((cap-dvent+360)%360)-180)
			}

			function ftwao(cap,dvent)
			{ // twa orientée
			twa1=(cap-dvent+360)%360
			if (twa1<180)
			{twao=twa1}
			else{twao=twa1-360}
			return twao	
			}

			function pos_dec_mn(pos)
			{  // transforme les degres decimaux en mn sec
			 	abs=Math.abs(pos)
				deg=Math.floor(abs)
				min=Math.floor((abs-deg)*60)
				sec=Math.round(((abs-deg)*60-min)*60)
				return deg+'°'+min+'mn'+sec+'s'
			}  

			function pos_dec_mn_lat(pos)
			{  // transforme les degres decimaux en mn sec
			 	abs=Math.abs(pos)
				deg=Math.floor(abs)
				min=Math.floor((abs-deg)*60)
				sec=Math.round(((abs-deg)*60-min)*60)
				if (pos>0) {var hem='N' }
				else {var hem='S'}
				return deg+'°'+min+"'"+sec+"''"+hem+"  "
			}  

			function pos_dec_mn_lng(pos)
			{  // transforme les degres decimaux en mn sec
			 	abs=Math.abs(pos)
				deg=Math.floor(abs)
				min=Math.floor((abs-deg)*60)
				sec=Math.round(((abs-deg)*60-min)*60)
				if (pos>0) {var hem='E'}
				else{var hem='W'}
				return deg+'°'+min+"'"+sec+"''"+hem+"  "
			}  


			function dec_to_mn_lat(pos)
			{  // transforme les degres decimaux en mn sec
				var tab=new Array;
			 	var abs=Math.abs(pos)
				var  deg=Math.floor(abs)
				var  min=Math.floor((abs-deg)*60)
				var  sec=Math.round(((abs-deg)*60-min)*60)
				if (pos>0) {hem='N' }
				else {hem='S'}
				tab=[deg,min,sec,hem]
				return tab
			}  

			function dec_to_mn_lng(pos)
			{  // transforme les degres decimaux en mn sec
				var tab=new Array;
			 	var abs=Math.abs(pos)
				var  deg=Math.floor(abs)
				var  min=Math.floor((abs-deg)*60)
				var  sec=Math.round(((abs-deg)*60-min)*60)
				if (pos>0) {hem='E' }
				else {hem='W'}
				tab=[deg,min,sec,hem]
				return tab
			}  




			function dec_to_mn_lat_n(pos)
			{  // transforme les degres decimaux en mn sec
				var tab=new Array;
			 	var abs=Math.abs(pos)
				var  deg=Math.floor(abs)
				var  min=Math.floor((abs-deg)*60)
				var  sec=Math.round(((abs-deg)*60-min)*60)
				if (pos>0) {hem=+1 }
				else {hem=-1}
				tab=[deg,min,sec,hem]
				return tab
			}  

			function dec_to_mn_lng_n(pos)
			{  // transforme les degres decimaux en mn sec
				var tab=new Array;
			 	var abs=Math.abs(pos)
				var  deg=Math.floor(abs)
				var  min=Math.floor((abs-deg)*60)
				var  sec=Math.round(((abs-deg)*60-min)*60)
				if (pos>0) {hem=1 }
				else {hem=-1}
				tab=[deg,min,sec,hem]
				return tab
			}  









			function h_mn(sec)
			{
				h=Math.floor(sec/3600)	
				mn=Math.floor((sec-3600*h)/60)
				s=sec-3600*h-60*mn
				res=h+'h '+mn+'mn '+s+'s'
				return res
			}

			function hmn(t)
			{ h =Math.floor(t/3600)
			 mn= Math.floor( (t%3600)/60)
			 res= h+':'+mn
			  return res
			}

			function recherche (tws,TWS)
			{
				var indice
				for (var i=0;i<TWS.length ;i++)
				{if (TWS[i]<=tws) {indice=i}}
				return indice
			}




			function polinterpol2d(bateau,twa,tws)                                          // ancienne fonction 
			{	// parametres : polaires du bateau twa et tws
				twa=Math.abs(twa)
				if (twa==180){twa=179.99}
			    var i_sup=l2.findIndex(element => element > twa);

				var j_sup=l1.findIndex(element => element > tws);				
				var twa_inf=l2[i_sup-1]
				var twa_sup=l2[i_sup]
				var tws_inf=l1[j_sup-1]
				var tws_sup=l1[j_sup]
				//console.log('isup : '+ i_sup)
                dx = twa-twa_inf 				// Ecart avec la valeur d'indice mini
				dy = tws-tws_inf

				deltax=twa_sup-twa_inf
				deltay=tws_sup-tws_inf
				fx1y1   = bateau[i_sup-1][j_sup-1]
				fx2y1   = bateau[i_sup][j_sup-1]			
				fx1y2   = bateau[i_sup-1][j_sup]			
				fx2y2   = bateau[i_sup][j_sup]			
				dfx     = fx2y1-fx1y1			
				dfy     = fx1y2-fx1y1			
				dfxy    = fx1y1+fx2y2-fx2y1-fx1y2				
				fxy     = dfx*dx/deltax  + dfy*dy/deltay + dfxy*dx*dy/deltax/deltay + fx1y1
				return fxy
			}


//*******************************************************************
// fonction importante permettant de calculer la meteo en js
// il est important que cette fonction soit en phase avec la fonction python


function vit_angle_vent(lat,lng,t0)

{   //Nouvelle version
	
	// console.log (' y0 : '+y0+' x0 : '+x0+' t0 : '+t0+' tig : '+tig)
	// console.log('heure du grib  : '+intlhmn.format(tig*1000))
	// console.log('heure prevision  : '+intlhmn.format(t0*1000))
	
	try{
	itemp=(t0-tig)/3600/3     // Ecart en heures avec le tig  modulo 3h
	ilati=-(lat-latini)       // ecart avec la latitude du grib chargé
	ilong=(360+lng-lngini)%360
	iitemp    = Math.floor(itemp)       // partie entiere
	iilati    = Math.floor(ilati)
	iilong    = Math.floor(ilong)
	ditemp    = itemp%1						// partie decimale				
	dilati    = ilati%1
	dilong    = ilong%1
	// console.log(' ')
	// console.log ('Indices : '+itemp.toFixed(4)+' '+ilati.toFixed(4)+' '+ilong.toFixed(4))	
	
	// a l'indice de temps t 
	u000=U10[iitemp][iilati][iilong]
	u010=U10[iitemp][iilati+1][iilong]
	u001=U10[iitemp][iilati][iilong+1]
	u011=U10[iitemp][iilati+1][iilong+1]
	v000=V10[iitemp][iilati][iilong]
	v010=V10[iitemp][iilati+1][iilong]
	v001=V10[iitemp][iilati][iilong+1]
	v011=V10[iitemp][iilati+1][iilong+1]

	// a l'indice de temps t+1 
	u100=U10[iitemp+1][iilati][iilong]
	u110=U10[iitemp+1][iilati+1][iilong]
	u101=U10[iitemp+1][iilati][iilong+1]
	u111=U10[iitemp+1][iilati+1][iilong+1]
	v100=V10[iitemp+1][iilati][iilong]
	v110=V10[iitemp+1][iilati+1][iilong]
	v101=V10[iitemp+1][iilati][iilong+1]
	v111=V10[iitemp+1][iilati+1][iilong+1]

	// interpolation vectorielle    
	// on demarre les interpolations sur le temps 
	fraction = Math.floor(ditemp*18)/18
	
	ux00=u000+fraction*(u100-u000)
	ux10=u010+fraction*(u110-u010)
	ux01=u001+fraction*(u101-u001)
	ux11=u011+fraction*(u111-u011)
	vx00=v000+fraction*(v100-v000)
	vx10=v010+fraction*(v110-v010)
	vx01=v001+fraction*(v101-v001)
	vx11=v011+fraction*(v111-v011)

	// maintenant on est reduit a une interpolation a 2 dimensions
	//on fait ensuite une interpolation bilineaire sur les latitudes

	uxx0=ux00+ dilati*(ux10-ux00)
	uxx1=ux01+ dilati*(ux11-ux01)
	vxx0=vx00+ dilati*(vx10-vx00)
	vxx1=vx01+ dilati*(vx11-vx01)
	// puis sur la longitude
	uxxx=uxx0+dilong*(uxx1-uxx0)
	vxxx=vxx0+dilong*(vxx1-vxx0)
	// le calcul du module donne la vitesse
	speed_uv = Math.sqrt(uxxx**2+vxxx**2)

	// interpolation sur les modules 
	m000=Math.sqrt(u000**2+v000**2)
	m010=Math.sqrt(u010**2+v010**2)
	m001=Math.sqrt(u001**2+v001**2)
	m011=Math.sqrt(u011**2+v011**2)
	m100=Math.sqrt(u100**2+v100**2)
	m110=Math.sqrt(u110**2+v110**2)
	m101=Math.sqrt(u101**2+v101**2)
	m111=Math.sqrt(u111**2+v111**2)

	// interpolation des modules sur le temps
	mx00=m000+fraction*(m100-m000)
	mx10=m010+fraction*(m110-m010)
	mx01=m001+fraction*(m101-m001)
	mx11=m011+fraction*(m111-m011)
	//interpolation des modules sur la latitude
	mxx0=mx00+ dilati*(mx10-mx00)
	mxx1=mx01+ dilati*(mx11-mx01)
	//puis sur la longitude
	mxxx=mxx0+dilong*(mxx1-mxx0)
	speed_s=mxxx*1.94384


	angle= Math.acos(vxxx/speed_uv)*180/Math.PI+180;
	if (uxxx<0) {angle=360-angle}

	//console.log (''+u000+' '+v000+ '   '+u010+' ' +v010+ '  '+u001+' ' +v001+'   '+u011+' ' +v011 )

	speed_uv *=1.94384
	vitesse=(speed_uv+speed_s)/2
	//console.log ('fraction '+fraction)
	// console.log (''+uxxx+' '+vxxx )
	// console.log (' speed_uv : '+speed_uv)
	// console.log (' speed_s  : '+speed_s)
	// console.log (' angle  : '+angle)
	}

	catch{
		vitesse=0
		angle=0
	}


	return[vitesse,angle]

}







			function cvent(u,v) //retourne la vitesse du vent et sa force a partir de u et v
			{
				vit = Math.sqrt(u*u + v*v)
				angle= Math.acos(v/vit)*180/Math.PI+180;
				if (u<0)
				{angle=360-angle}
				vit*= 1.94384     // Vitesse en noeuds
				return [vit,angle]				
			} 

			

            
			function dist_cap_ortho(lati,lngi,latfi,lngfi)
			{// latitude origine equateur positive vers le nord
			//longitude greenwich positive vers l'est 
			latirad = lati*Math.PI/180
			latfrad = latfi*Math.PI/180
			lb_m_la=(lngfi-lngi)*Math.PI/180
			cosfia=Math.cos(latirad)
			sinfia=Math.sin(latirad)
			sinfib=Math.sin(latfrad)
			cosfib=Math.cos(latfrad)
			cos_lb_m_la=Math.cos(lb_m_la)
			sin_lb_m_la=Math.sin(lb_m_la)
			capo= Math.atan(cosfib*sin_lb_m_la/((cosfia*sinfib-sinfia*cosfib*cos_lb_m_la)+0.0000001))*180/Math.PI

			if( (latfi-lati)<=0)
			{capo=180+capo}
			else {capo=(capo+360)%360}
			dist= Math.acos(sinfia*sinfib+cosfia*cosfib*cos_lb_m_la)/Math.PI*180*60
			return [dist,capo]
			}


			function dist_cap_ortho2(lati,lngi,latfi,lngfi)
			{// latitude origine equateur positive vers le nord
			//longitude greenwich positive vers l'est 
			latirad = lati*Math.PI/180
			latfrad = latfi*Math.PI/180
			lb_m_la=(lngfi-lngi)*Math.PI/180
			cosfia=Math.cos(latirad)
			sinfia=Math.sin(latirad)
			sinfib=Math.sin(latfrad)
			cosfib=Math.cos(latfrad)
			cos_lb_m_la=Math.cos(lb_m_la)
			sin_lb_m_la=Math.sin(lb_m_la)
			capo= Math.atan2(cosfib*sin_lb_m_la,((cosfia*sinfib-sinfia*cosfib*cos_lb_m_la)+0.0000001))*180/Math.PI

			// if( (latfi-lati)<=0)
			// {capo=180+capo}
			// else {}

			capo=(capo+360)%360
			dist= Math.acos(sinfia*sinfib+cosfia*cosfib*cos_lb_m_la)/Math.PI*180*60
			return [dist,capo]
			}







			function deplacement(latinit,lnginit,dt,vitesse,cap)
			{		
				cap_r=cap*Math.PI/180
				latfdep=latinit+vitesse*dt/3600/60*Math.cos(cap_r)
				lngfdep=lnginit+vitesse*dt/3600/60*Math.sin(cap_r)/Math.cos(latinit*Math.PI/180)
				arrivee=[latfdep,lngfdep]
				return arrivee 

			}

			function penalite (tws)
			{ 
				//console.log ('dans fonction penalite tws +'+tws+ ' lwtimer '+lwtimer)
				//temps de neutralisation de l avancement du bateau pour fullpack  
				
				pt=Math.min( Math.max(lwtimer +(tws-lws)/(hws-lws)*(hwtimer-lwtimer),lwtimer),hwtimer)*(1-lwratio)

				//console.log ('dans fonction penalite lws +'+lws+ ' t '+pt)

			  //t= 
			  return pt
			}


			function tackpenalite (tws)
			{ 
				
				//temps de neutralisation de l avancement du bateau pour fullpack en tack  
				
				pt=Math.min( Math.max(tackprolwtimer +(tws-lws)/(hws-lws)*(tackprohwtimer-tackprolwtimer),tackprolwtimer),tackprohwtimer)*(1-tackprolwratio)

				//console.log ('dans fonction penalite lws +'+lws+ ' t '+pt)

			  //t= 
			  return pt
			}

			function gybepenalite (tws)
			{ 
				//console.log ('dans fonction penalite tws +'+tws+ ' lwtimer '+lwtimer)
				//temps de neutralisation de l avancement du bateau pour fullpack   en gybe

				pt=Math.min( Math.max(gybeprolwtimer +(tws-lws)/(hws-lws)*(gybeprohwtimer-gybeprolwtimer),gybeprolwtimer),gybeprohwtimer)*(1-gybeprolwratio)

				//console.log ('dans fonction penalite lws +'+lws+ ' t '+pt)

			  //t= 
			  return pt
			}






			function polyline_cap(y0,x0,cap0,t0)
			{  
			    // Fonction de calcul de la ligne cap constant avec changements de voiles
				var meteo_t0=vit_angle_vent (y0,x0,t0);tws_t0=meteo_t0[0];twd_t0=meteo_t0[1];			
				var twa_t0=Math.abs(ftwao(cap0,meteo_t0[1]))
				polyline=  [[y0,x0]] ; polyvoilecap= [[]] ;//initialisation des polylines
				var yt = y0 ; var xt = x0 ; var tt=t0 
								
				for (var i=0;i<=72;i++)
					{tt = tt+600
					meteo=vit_angle_vent (yt,xt,tt)
				    twa=ftwa(cap0,meteo[1])
					res=vitessepolaire (twa_t0,meteo[0]) ;vit_polaire=res[0]; nvoile1 =res[1];	     // utilisation de la nouvelle fonction pour le calcul des polaires avec les voiles
					                 	
					if (nvoile1 != nvoile0) {	polyvoilecap.push(point) ;nvoile0=nvoile1	;pt=penalite (meteo[0]);}
					else {pt=0}
					point=deplacement(yt,xt,600-pt,vit_polaire,cap0)     //calcul du nouveau point }					
                    polyline.push(point)													    	
					yt=point[0];xt=point[1];pt=0;
					}
			
			return [polyline,polyvoilecap,cap0]  
			}
                



			function polyline_twa(y0,x0,twa0,t0)
			{  // fonction de calcul de la ligne twa_ini constante avec changements de voiles
			  	var meteo_t0=vit_angle_vent (y0,x0,t0)     // meteo au point de depart permet de calculer la twa par rapport au cap suivi
				var twa_ini_abs=Math.abs(twa0)
				res=vitessepolaire (twa_ini_abs,meteo_t0[0]) ;vit_polaire=res[0]  ; nvoile0 =res[1];   // utilisation de la nouvelle fonction pour le calcul des polaires avec les voiles
				polyline = [[y0,x0]]  						//initialisation de la polyline
				polyvoile= [[]]  						// initialisation pour changement de voile
				var yt = y0 ; var xt = x0 ; var tt=t0; var pt=0 				// initialisation des latitudes et longitudes dans la boucle	
				for (var i=0;i<=72;i++)                                                // avant modif provisoire 72   
					{tt = tt+600
					var meteo=vit_angle_vent (yt,xt,tt)	// on calcule la meteo au nouveau point 
					res_t=vitessepolaire (twa_ini_abs,meteo[0]) ; vit_polaire=res_t[0]   ; nvoile1 =res_t[1];//utilisation de la fonction avec detection changement de voile 
					
					
					var capa=(+360+twa0+meteo[1])%360	
					if (nvoile1 != nvoile0) {	polyvoile.push(point);nvoile0=nvoile1;pt=penalite (meteo[0])}
					else {pt=0}
					point=deplacement(yt,xt,600-pt,vit_polaire,capa)         	// on calcule le nouveau point }
					polyline.push(point)											// on ajoute les nouveaux points dans la serie de points 
					yt=point[0];xt=point[1];pt=0;	
					}
			return [polyline,polyvoile,twa0]  
			}


		
	
	
			






























    // Fonction zezo                
        function crsdist(lat1, lon1, lat2, lon2)
         {
            var a = crsdist_num(lat1, lon1, lat2, lon2);
            var dist = Math.round(a[1] * 34377.4)/10;
            if (dist.toString().indexOf('.') < 0)
             {
                    dist += '.0';
             }
            var dir = Math.round(a[0] * (180/Math.PI) * 10)/10;
            if (dir.toString().indexOf('.') < 0) 
            {
                dir += '.0';
            }
            dir = dir.toString();
            dist = dist.toString();
                while (dir.length < 5) 
            {
                dir = " " + dir;
            }
            while (dist.length < 6) {
                dist = " " + dist;
            }
            //var res = dist + 'nm ' + dir + '°';
            var res = 'Cap :'+dir +'° Distance :'+dist+'M';
        return res;
        }
        


            function crsdist_num(lat1, lon1, lat2, lon2)
        {
            lat1 = lat1 * Math.PI/180;
            lon1 = lon1 * Math.PI/180;
            lat2 = lat2 * Math.PI/180;
            lon2 = lon2 * Math.PI/180;
            var crs;        
            var d=Math.acos(Math.sin(lat1)*Math.sin(lat2)+Math.cos(lat1)*Math.cos(lat2)*Math.cos(lon1-lon2));
            var argacos=(Math.sin(lat2)-Math.sin(lat1)*Math.cos(d))/(Math.sin(d)*Math.cos(lat1));
            if (Math.sin(lon2-lon1) > 0){   
                    crs=Math.acos(argacos); 
            } else {
                    crs=2*Math.PI-Math.acos(argacos); 
            }
            return [crs,d];
        }

		// function testPolyline(t0)
		// {   console.log ('(js ligne 526)'+t0 )
		// 	twasimul1=-document.getElementById('twasimul1').value
		// 	twasimul2=-document.getElementById('twasimul2').value
		// 	twasimul3=-document.getElementById('twasimul3').value
		// 	twasimul4=-document.getElementById('twasimul4').value
		// 	twasimul5=-document.getElementById('twasimul5').value
			
		// 	capsimul1=+document.getElementById('capsimul1').value
		// 	capsimul2=+document.getElementById('capsimul2').value
		// 	capsimul3=+document.getElementById('capsimul3').value
		// 	capsimul4=+document.getElementById('capsimul4').value
		// 	capsimul5=+document.getElementById('capsimul5').value
			
		// 	tsimulation1=+document.getElementById('tsimul1').value
		// 	tsimulation2=+document.getElementById('tsimul2').value
		// 	tsimulation3=+document.getElementById('tsimul3').value
		// 	tsimulation4=+document.getElementById('tsimul4').value
		// 	tsimulation5=+document.getElementById('tsimul5').value

		// 	console.log ('*************************************************************')
		// 	console.log ('********************* SIMULATION ****************************')
		// 	console.log ('*************************************************************')



			
		// 	if(	document.getElementById('twa1').checked)
		// 	{choix1='twa';valeur1= twasimul1}
		// 	else if(	document.getElementById('cap1').checked)
		// 	{choix1='cap';valeur1= capsimul1}
		// 	else {choix1='rien';valeur1=0}

		// 	if(	document.getElementById('twa2').checked)
		// 	{choix2='twa';valeur2= twasimul2}
		// 	else if(	document.getElementById('cap2').checked)
		// 	{choix2='cap';valeur2= capsimul2}
		// 	else {choix2='rien';valeur2=0}

		// 	if(	document.getElementById('twa3').checked)
		// 	{choix3='twa';valeur3= twasimul3}
		// 	else if(	document.getElementById('cap3').checked)
		// 	{choix3='cap';valeur3= capsimul3}
		// 	else {choix3='rien';valeur3=0}

		// 	if(	document.getElementById('twa4').checked)
		// 	{choix4='twa';valeur4= twasimul4}
		// 	else if(	document.getElementById('cap4').checked)
		// 	{choix4='cap';valeur4= capsimul4}
		// 	else {choix4='rien';valeur4=0}

		// 	if(	document.getElementById('twa5').checked)
		// 	{choix5='twa';valeur5= twasimul5}
		// 	else if(	document.getElementById('cap5').checked)
		// 	{choix5='cap';valeur5= capsimul5}
		// 	else {choix5='rien';valeur5=0}




			

		// 	//calcul des points 
		// 	//polyline= [[latdep,lngdep]]  //initialisation de la polyline
		// 	polyline= [[y0,x0]]  //initialisation de la polyline
		// 	t100 =t0

			

		// 	// conditions au depart
		// 	meteo=vit_angle_vent (latdep,lngdep,t0)
		// 	tws_ini=meteo[0]
		// 	twd_ini=meteo[1]
		// 	lat8=+latdep
		// 	lng8=+lngdep
		// 	dt=600   //intervalle entre deux points 10mn
			
		// 	t1=tsimulation1/10 // recalcul toutes les 10mn 
		// 	t2=tsimulation2/10 
		// 	t3=tsimulation3/10 
		// 	t4=tsimulation4/10 
		// 	t5=tsimulation5/10 
			
		// 	// 1er tronçon
		// 	console.log('choix1 '+choix1+' : '+valeur1 )
		// 	for (var i=0;i<(tsimulation1/10);i++)
		// 	{tsimul1 = t100+(i*600)         // intervalles de 600s soit 10mn
		// 		console.log ('tsimul1  '+tsimul1)
				
		// 		if (choix1=='twa')
		// 		{	meteo=vit_angle_vent (lat8,lng8,tsimul1)
		// 			twa =twasimul1
		// 			console.log('twasimul1 : '+twasimul1)
		// 			vit_polaire=polinterpol2d(polairesjs,twa,meteo[0])
		// 			console.log('vit_polaire : '+vit_polaire)
		// 			capa=+twa+meteo[1]
		// 			console.log('capa : '+capa)
		// 			point=deplacement(lat8,lng8,dt,vit_polaire,capa) 
		// 			console.log('nouveau point : '+point) 
		// 			lat8=point[0];lng8=point[1];
		// 			polyline.push(point)	
		// 			}
		// 		if (choix1=='cap')
		// 		{	meteo=vit_angle_vent (lat8,lng8,tsimul1)
		// 			cap1 =capsimul1
		// 			console.log('twasimul1 : '+twasimul1)
		// 			twa=ftwa(cap1,meteo[1])
		// 			vit_polaire=polinterpol2d(polairesjs,twa,meteo[0])
		// 			console.log('vit_polaire : '+vit_polaire)
		// 			console.log('capa : '+capa)
		// 			point=deplacement(lat8,lng8,dt,vit_polaire,cap1) 
		// 			console.log('nouveau point : '+point) 
		// 			lat8=point[0];lng8=point[1];
		// 			polyline.push(point)	
		// 			}
		// 	}

		// 		// 2eme troncon
		// 	console.log('choix2 '+choix2+' : '+valeur2 )
		// 	for (var i=0;i<(tsimulation2/10);i++)
		// 	{tsimul2 = t100+(tsimulation1*60)+i*600
		// 		console.log ('****************************************tsimul2  '+tsimul2)
		// 		console.log ( 'pour test'+lat8 +' '+ lng8+' '+tsimul2)
		// 		if (choix2=='twa')
		// 		{	meteo=vit_angle_vent (lat8,lng8,tsimul2) //lat8 lng8 sont les latitudes issues de la sequence precedente
		// 			twa =twasimul2
		// 			console.log('twasimul2 : '+twasimul2)
		// 			vit_polaire=polinterpol2d(polairesjs,twa,meteo[0])
		// 			console.log('vit_polaire : '+vit_polaire)
		// 			capa=+twa+meteo[1]
		// 			console.log('capa : '+capa)
		// 			point=deplacement(lat8,lng8,dt,vit_polaire,capa) 
		// 			console.log('nouveau point : '+point) 
		// 			lat8=point[0];lng8=point[1];
		// 			polyline.push(point)	
		// 			}
		// 		if (choix2=='cap')
		// 		{	meteo=vit_angle_vent (lat8,lng8,tsimul2)
		// 			cap2 =capsimul2
		// 			console.log('capsimul2 : '+capsimul2)
		// 			twa=ftwa(cap2,meteo[1])
		// 			vit_polaire=polinterpol2d(polairesjs,twa,meteo[0])
		// 			console.log('vit_polaire : '+vit_polaire)
		// 			console.log('capa : '+capa)
		// 			point=deplacement(lat8,lng8,dt,vit_polaire,cap2) 
		// 			console.log('nouveau point : '+point) 
		// 			lat8=point[0];lng8=point[1];
		// 			polyline.push(point)	
		// 			}
		// 	}


		// 	// 3eme troncon
		// 	console.log('ZZZZZZZZZZZZZZZZZZ choix3 '+choix3+' : '+valeur3 )
		// 	for (var i=0;i<(tsimulation3/10);i++)
		

		// 	{tsimul3 = t100+(+tsimulation1+tsimulation2)*60+i*600
		// 		// console.log ('XXXXXXXXXXXXXXXXXtsimul3  '+tsimul3)
		// 		// console.log ( 'pour test'+lat8 +' '+ lng8+' '+tsimul3)
		// 		if (choix3=='twa')
		// 		{	meteo=vit_angle_vent (lat8,lng8,tsimul3) //lat8 lng8 sont les latitudes issues de la sequence precedente
		// 			twa =twasimul3
		// 			console.log('twasimul3 : '+twasimul3)
		// 			vit_polaire=polinterpol2d(polairesjs,twa,meteo[0])
		// 			console.log('vit_polaire : '+vit_polaire)
		// 			capa=+twa+meteo[1]
		// 			console.log('capa : '+capa)
		// 			point=deplacement(lat8,lng8,dt,vit_polaire,capa) 
		// 			console.log('nouveau point : '+point) 
		// 			lat8=point[0];lng8=point[1];
		// 			polyline.push(point)	
		// 			}
		// 		if (choix3=='cap')
		// 		{	meteo=vit_angle_vent (lat8,lng8,tsimul3)
		// 			cap3 =capsimul3
		// 			console.log('capsimul3 : '+capsimul3)
		// 			twa=ftwa(cap3,meteo[1])
		// 			vit_polaire=polinterpol2d(polairesjs,twa,meteo[0])
		// 			console.log('vit_polaire : '+vit_polaire)
		// 			console.log('capa : '+capa)
		// 			point=deplacement(lat8,lng8,dt,vit_polaire,cap3) 
		// 			console.log('nouveau point : '+point) 
		// 			lat8=point[0];lng8=point[1];
		// 			polyline.push(point)	
		// 			}
		// 	}


		// 	// 4eme troncon
		// 	console.log('choix4 '+choix4+' : '+valeur4 )

		// 	console.log('tsimulation 1 +2 + 3  : '+(tsimulation1+tsimulation2 +tsimulation3))
		// 	for (var i=0;i<tsimulation4/10;i++)
		// 	{tsimul4 = t100+(+tsimulation1+tsimulation2 +tsimulation3)*60+i*600
		// 		console.log ('********************************tsimul4  '+tsimul4)
		// 		console.log ( 'pour test'+lat8 +' '+ lng8+' '+tsimul4)
		// 		if (choix4=='twa')
		// 		{	meteo=vit_angle_vent (lat8,lng8,tsimul3) //lat8 lng8 sont les latitudes issues de la sequence precedente
		// 			twa =twasimul4
		// 			console.log('twasimul4 : '+twasimul4)
		// 			vit_polaire=polinterpol2d(polairesjs,twa,meteo[0])
		// 			console.log('vit_polaire : '+vit_polaire)
		// 			capa=+twa+meteo[1]
		// 			console.log('capa : '+capa)
		// 			point=deplacement(lat8,lng8,dt,vit_polaire,capa) 
		// 			console.log('nouveau point : '+point) 
		// 			lat8=point[0];lng8=point[1];
		// 			polyline.push(point)	
		// 			}
		// 		if (choix4=='cap')
		// 		{	meteo=vit_angle_vent (lat8,lng8,tsimul4)
		// 			cap4 =capsimul4
		// 			console.log('capsimul4 : '+capsimul4)
		// 			twa=ftwa(cap4,meteo[1])
		// 			vit_polaire=polinterpol2d(polairesjs,twa,meteo[0])
		// 			console.log('vit_polaire : '+vit_polaire)
		// 			console.log('capa : '+capa)
		// 			point=deplacement(lat8,lng8,dt,vit_polaire,cap4) 
		// 			console.log('nouveau point : '+point) 
		// 			lat8=point[0];lng8=point[1];
		// 			polyline.push(point)	
		// 			}
		// 	}

		// 	// 5eme troncon
		// 	console.log('choix5 '+choix5+' : '+valeur5 )

		// 	console.log('tsimulation 1 +2 + 3 +4 : '+(tsimulation1+tsimulation2 +tsimulation3+tsimulation4))
		// 	for (var i=0;i<tsimulation5/10;i++)
		// 	{tsimul5 = t100+(+tsimulation1+tsimulation2 +tsimulation3+tsimulation4)*60+i*600
		// 		//console.log ('********************************tsimul4  '+tsimul4)
		// 		//console.log ( 'pour test'+lat8 +' '+ lng8+' '+tsimul4)
		// 		if (choix5=='twa')
		// 		{	meteo=vit_angle_vent (lat8,lng8,tsimul4) //lat8 lng8 sont les latitudes issues de la sequence precedente
		// 			twa =twasimul5
		// 			console.log('twasimul5 : '+twasimul5)
		// 			vit_polaire=polinterpol2d(polairesjs,twa,meteo[0])
		// 			console.log('vit_polaire : '+vit_polaire)
		// 			capa=+twa+meteo[1]
		// 			console.log('capa : '+capa)
		// 			point=deplacement(lat8,lng8,dt,vit_polaire,capa) 
		// 			console.log('nouveau point : '+point) 
		// 			lat8=point[0];lng8=point[1];
		// 			polyline.push(point)	
		// 			}
		// 		if (choix5=='cap')
		// 		{	meteo=vit_angle_vent (lat8,lng8,tsimul5)
		// 			cap5 =capsimul5
		// 			console.log('capsimul5 : '+capsimul5)
		// 			twa=ftwa(cap5,meteo[1])
		// 			vit_polaire=polinterpol2d(polairesjs,twa,meteo[0])
		// 			console.log('vit_polaire : '+vit_polaire)
		// 			console.log('capa : '+capa)
		// 			point=deplacement(lat8,lng8,dt,vit_polaire,cap4) 
		// 			console.log('nouveau point : '+point) 
		// 			lat8=point[0];lng8=point[1];
		// 			polyline.push(point)	
		// 			}
		// 	}

		// return polyline
		
		// }

		function show(h)
		{console.log ('valeur de h '+h)
		var heureduvent=h
		return heureduvent
		}


		function show_wind(h)
			{
				wind_time=h
				console.log ('valeur de h '+h)
				
				document.getElementById("hours")[h].selected=true;
				// recuperation de la valeur souhaitee 	
				//document.getElementById('valeurtemps').innerHTML=wind_time
				tempsmeteo=+t0+(h*3600)
				console.log ('lat lng'+e.latlng.lat)
				try{meteocurseur=vit_angle_vent (e.latlng.lat,e.latlng.lng ,tempsmeteo) }
				catch(err){console.log ('erreur sur la meteo');meteocurseur=meteodepart  } //meteo au curseur 
						   
			   
				document.getElementById('tws3').value=meteocurseur[0].toFixed(2)
				document.getElementById('twd3').value=meteocurseur[1].toFixed(2)
				document.getElementById('dist3').value=direction[0].toFixed(0)
				// console.log ('wind_time : '+wind_time)
				// document.getElementById('dist3').value=wind_time

			}


			function next_wind()
			{
			var wind_time=document.getElementById('hours').selectedIndex;
			if (wind_time<24){
			show(+wind_time+1)
			console.log ('wind_time'+wind_time)
			}
			}

			function prev_wind()
			{
			var wind_time=document.getElementById('hours').selectedIndex;	
			if (wind_time>0)
			{
			show(+wind_time-1)
			}
			}



			function chaine_to_dec (lat,lng)
			{ // retourne les coordonnees string du json en tableau [lat,lng]
			
			var tablat=lat.split('-')
			var degre=parseInt( tablat[0])
			var minutes=parseInt(tablat[1])
			var secondes=parseInt(tablat[2])
			var orient= tablat[3]
			console.log('orientation ' +orient)
			var lati= degre + minutes / 60 + secondes / 3600
			if (orient=='S'){lati=-lati}

			//console.log ('latitude '+degre+' '+minutes+' '+secondes+' '+orient)
			//console.log ('lat decimale '+lat )
			var tablng=lng.split('-')
			degre=parseInt( tablng[0])
			minutes=parseInt(tablng[1])
			secondes=parseInt(tablng[2])
			orient= tablng[3]

			console.log('orientation E W : ' +orient)
			var lngi= degre + minutes / 60 + secondes / 3600
			if (orient=='W'){
			console.log ('orientation west confirmee')	
				lngi=-lngi}

			var coord=[lati,lngi]
			return coord	
			}