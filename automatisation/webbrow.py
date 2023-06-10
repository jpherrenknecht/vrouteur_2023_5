
import webbrowser as wb
import subprocess
url="https://www.virtualregatta.com/fr/offshore-jeu/"
wb.open_new(url)   # pour l instant pas trouve plein ecran il faut donc regler la fenetre au max

xte_command = "xte 'mousemove 3655 50' 'sleep 5' 'mouseclick 2'  'mouseclick 1'"     # declenche dashmap
subprocess.call(xte_command, shell=True)

xte_command = "xte 'mousemove 3530 1050' 'sleep 5' 'mouseclick 2'  'mouseclick 1'"   # met en plein ecran 
subprocess.call(xte_command, shell=True)

xte_command = "xte 'mousemove 2500 700' 'sleep 10' 'mouseclick 2'  'mouseclick 1'"   # ouvre la course"
subprocess.call(xte_command, shell=True)



# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.by import By

# driver = webdriver.Chrome()
# url='https://www.virtualregatta.com/fr/offshore-jeu/'
# driver.get(url)
# # assert "Python" in driver.title
# # elem = driver.find_element(By.NAME, "q")
# # elem.clear()
# elem.send_keys("pycon")
# elem.send_keys(Keys.RETURN)
# assert "No results found." not in driver.page_source
#driver.close()

# # Effectuer un clic à un endroit de la page
# element = driver.find_element_by_xpath('//xpath_de_l_element')
# actions = ActionChains(driver)
# actions.move_to_element(element).click().perform()

# # Fermer le navigateur
# driver.quit()