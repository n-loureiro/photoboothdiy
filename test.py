#import picamera
import pygame
import time
import os
import PIL.Image
import cups
#import RPi.GPIO as GPIO
from random import randint

from threading import Thread
from pygame.locals import *
from time import sleep
from PIL import Image, ImageDraw


# initialise global variables
Numeral = ""  # Numeral is the number display
Message = ""  # Message is a fullscreen message
BackgroundColor = ""
CountDownPhoto = ""
CountPhotoOnCart = ""
SmallMessage = ""  # SmallMessage is a lower banner message
TotalImageCount = 0  # Counter for Display and to monitor paper usage
PhotosPerCart = 30  # Selphy takes 16 sheets per tray
imagecounter = 0
cwd = os.getcwd()
imagefolder =  os.path.join(cwd,'Photos')
templatePath = os.path.join(cwd,'Photos', 'Template', "template.png") #Path of template image
ImageShowed = False
Printing = False
BUTTON_PIN = 25
#IMAGE_WIDTH = 558
#IMAGE_HEIGHT = 374
IMAGE_WIDTH = 550
IMAGE_HEIGHT = 360

save_final_path = os.path.join(cwd,'final')

# Load the background template
bgimage = PIL.Image.open(templatePath)

#Setup GPIO
#GPIO.setmode(GPIO.BCM)
#GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# initialise pygame
pygame.init()  # Initialise pygame
pygame.mouse.set_visible(False) #hide the mouse cursor
infoObject = pygame.display.Info()
# screen = pygame.display.set_mode((infoObject.current_w,infoObject.current_h), pygame.FULLSCREEN)  # Full screen 
screen = pygame.display.set_mode((800,800), pygame.RESIZABLE)  # Full screen 
background = pygame.Surface(screen.get_size())  # Create the background object
background = background.convert()  # Convert it to a background

# screenPicture = pygame.display.set_mode((infoObject.current_w,infoObject.current_h), pygame.FULLSCREEN)  # Full screen
screenPicture = pygame.display.set_mode((infoObject.current_w,infoObject.current_h), pygame.RESIZABLE)  # Full screen
backgroundPicture = pygame.Surface(screenPicture.get_size())  # Create the background object
backgroundPicture = background.convert()  # Convert it to a background

transform_x = infoObject.current_w # how wide to scale the jpg when replaying
transfrom_y = infoObject.current_h # how high to scale the jpg when replaying

def InitFolder():
	global imagefolder
	global Message
 
	Message = 'Folder Check...'
	UpdateDisplay()
	Message = ''

	#check image folder existing, create if not exists
	if not os.path.isdir(imagefolder):	
		os.makedirs(imagefolder)	
			
	imagefolder2 = os.path.join(imagefolder, 'images')
	if not os.path.isdir(imagefolder2):
		os.makedirs(imagefolder2)


def main(threadName, *args):
	InitFolder()
	while True:
		show_image('images/start_camera.jpg')
		WaitForEvent()
		time.sleep(0.2)
		TakePictures()
	GPIO.cleanup()


# launch the main thread
Thread(target=main, args=('Main', 1)).start()




pygame.init()
width, height = (200,300)
screen = pygame.display.set_mode((width, height))


def loop():
	clock = pygame.time.Clock()
	while not False:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return(False)
			if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
				print("here")
		clock.tick(30)


loop()
pygame.quit()