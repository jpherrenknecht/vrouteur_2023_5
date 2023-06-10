from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

# Instancier le navigateur (dans cet exemple, on utilise Firefox)
driver = webdriver.Chrome()

# Ouvrir la page web
driver.get("https://www.google.com")

# Localiser l'objet à déplacer (par exemple, un élément avec l'ID "objet")
# objet = driver.find_element_by_id("objet")

# # Récupérer les coordonnées de départ de l'objet
# depart_x = objet.location['x']
# depart_y = objet.location['y']

# # Simuler l'événement "mousedown" sur l'objet
# action_chains = ActionChains(driver)
# action_chains.move_to_element_with_offset(objet, 0, 0).click_and_hold().perform()

# # Simuler l'événement "mousemove" pour déplacer l'objet
# nouvelle_position_x = depart_x + 100  # Déplacer de 100 pixels à droite
# nouvelle_position_y = depart_y + 100  # Déplacer de 100 pixels vers le bas
# action_chains.move_by_offset(nouvelle_position_x, nouvelle_position_y).perform()

# # Simuler l'événement "mouseup" pour relâcher l'objet
# action_chains.release().perform()

# # Fermer le navigateur
# driver.quit()