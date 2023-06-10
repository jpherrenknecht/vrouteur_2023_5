import webbrowser
import pyautogui
import time

# ouvrir la fenetre VR 
# ouvrir la map du dash
# lancer le programme
# se positionner sur le Wp a modifier en moins de 3 s

time.sleep(3)          # 3 s le temps de se positionner sur le wp à deplacer 
pyautogui.moveRel(2,0,2)    # deplace de 2 pixels en x a droite et de 0 en y vers le bas  
pyautogui.mouseUp()

# il n'y a plus qu'à sauver la nouvelle position et à verifier 