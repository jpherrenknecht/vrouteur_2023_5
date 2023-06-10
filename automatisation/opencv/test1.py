import sys
import cv2 as cv
print(cv.__version__)

#img = cv.imread(cv.samples.findFile("starry_night.jpg"))

dir='/home/jp/vrouteur_2023_5/automatisation/images/'
img='A227.png'
image=dir+img
img = cv.imread(cv.samples.findFile(image))
## [imread]
## [empty]
if img is None:
    sys.exit("Could not read the image.")
## [empty]
## [imshow]
cv.imshow("Display window", img)
k = cv.waitKey(0)
## [imshow]
## [imsave]
if k == ord("s"):
    cv.imwrite("starry_night.png", img)
## [imsave]