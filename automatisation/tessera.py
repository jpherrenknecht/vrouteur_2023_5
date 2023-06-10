import cv2
import pytesseract

adresse='/home/jp/vrouteur_2023_5/automatisation/images/un.png'
image = cv2.imread(adresse)
gray  = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
custom_config = r'--oem 3 --psm 6'  # Configuration personnalisée pour Tesseract
text = pytesseract.image_to_string(thresh, config=custom_config)
print("Chiffre détecté :", text)


#/home/jp/vrouteur_2023_5/automatisation/images/A227.png