import webbrowser
import pyautogui
import time
import cv2
# Ouvrir la page 

#ouverture de l url
url='https://www.virtualregatta.com/en/offshore-game/'
webbrowser.open(url)
#pyautogui.press("F11")
#time.sleep(2)
#print(pyautogui.position())    # donne la position du curseur  
#pyautogui.moveTo(3530,1010)
time.sleep(3)
dir='/home/jp/vrouteur_2023_5/automatisation/images/'
img='PleinEcran.png'
image=dir+img
PleinEcran=pyautogui.locateOnScreen(image)  #permet de rechercher une image sur l ecran
pyautogui.click(PleinEcran)


pyautogui.moveRel(-100,-100,1) # pour eviter l apparition des equipes
print('Position PleinEcran',PleinEcran)
time.sleep(3)
# pyautogui.locateAllOnScreen('num_9.png')  #permet de rechercher une image sur l ecran
# triangleGauche=pyautogui.locateOnScreen('triangleGauche.png') 
# pyautogui.click(triangleGauche)
print('position du curseur apres plein ecran',pyautogui.position())    # donne la position du curseur     
img0='Leg5.png'
image0=dir+img
img='triangleDroit.png'
image=dir+img
triangleDroit=pyautogui.locateOnScreen(image,confidence=0.9)  #permet de rechercher une image sur l ecran
while triangleDroit==None:
    print ('La position triangle droit n a pas ete detectee') 
    
    # pyautogui.moveTo(3758,571)    #deplace le curseur a la position en 1 s
    # time.sleep(1)
    pyautogui.mouseDown(3758,571,button="left")
    pyautogui.mouseUp(3758,571,button="left")
    time.sleep(2)
    Leg5=pyautogui.locateOnScreen(image)
    if Leg5!=None:
        print('Leg5 detecte Position',Leg5)
        pyautogui.click(Leg5)


    # pyautogui.mouseDown(3758,571,button="left")
    # pyautogui.mouseUp(3758,571,button="left")
    # time.sleep(1)

    # pyautogui.mouseDown(3758,571,button="left")
    # pyautogui.leftClick(3758,571) 
    # pyautogui.rightClick(3758,571) 
    # pyautogui.tripleClick()

# else :
#     print('TriangleDroit detecte Position',triangleDroit)
#     pyautogui.click(triangleDroit)



img='Leg5.png'
image=dir+img
Leg5=pyautogui.locateOnScreen(image)  #permet de rechercher une image sur l ecran
if Leg5==None:
    print ('la position Leg5 n a pas ete detectee')
    # time.sleep(2)
    # pyautogui.click(3758,625)      
    
    time.sleep(3)
    img='triangleDroit.png'
    image=dir+img
    triangleDroit=pyautogui.locateOnScreen(image,confidence=0.9)  #permet de rechercher une image sur l ecran
    if triangleDroit==None:
       print ('La position triangle droit n a pas ete detectee') 
    else :
        print('TriangleDroit detecte Position',triangleDroit)
        pyautogui.click(triangleDroit)

else:

    print('Leg5 detecte Position',Leg5)
    pyautogui.click(Leg5)




# cic=pyautogui.locateOnScreen('cic.png')  #permet de rechercher une image sur l ecran
# print('cic',cic)
# pyautogui.click(cic)



# print(pyautogui.position())    # donne la position du curseur  
# pyautogui.moveTo(3530,1010)

# pyautogui.leftClick()
# time.sleep(5)
# pyautogui.moveTo(1997,577)
# time.sleep(1)
# pyautogui.tripleClick()
# print('position fleche gauche',pyautogui.position())    # donne la position du curseur 
# time.sleep(1)
# print(pyautogui.position())    # donne la position du curseur  
# time.sleep(5)
# pyautogui.moveTo(2066,667)
# time.sleep(1)
# pyautogui.leftClick()



#*************************************************************************
# time.sleep(3)          #le temps de se positionner sur le wp
# pyautogui.mouseDown()
# pyautogui.moveRel(2,0,2)
# pyautogui.mouseUp()

#pyautogui.locateOnScreen('PleinEcran.png')  #permet de rechercher une image sur l ecran
# pyautogui.locateAllOnScreen('num_9.png')  #permet de rechercher une image sur l ecran

#pyautogui.click('PleinEcran.png')
pyautogui.screenshot('screenshot2.png',region=(500,500,600,1000))