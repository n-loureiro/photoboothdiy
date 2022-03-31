#import picamera
import pygame
import time
import os
import PIL.Image
import cups
import RPi.GPIO as GPIO
from random import randint
import random
import signal

from threading import Thread
from pygame.locals import *
from time import sleep
from PIL import Image, ImageDraw

import gphoto2 as gp

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
templatePath_print = os.path.join(cwd,'Photos', 'Template', "template2.png") #Path of template image
templatePath = os.path.join(cwd,'Photos', 'Template', "photo_strip.png")


ImageShowed = False
Printing = False
BUTTON_PIN = 25
#IMAGE_WIDTH = 558
#IMAGE_HEIGHT = 374
IMAGE_WIDTH = 550
IMAGE_HEIGHT = 360

debug = False

save_final_path = os.path.join(cwd,'final')

def kill_gphoto2():
	print("killling!!!!!!!!!!")
	try:
		for line in os.popen("ps aux | grep gphoto2 | grep -v grep"):
			fields = line.split()
			pid = fields[1]
			print("pid", pid)
			os.kill(int(pid), signal.SIGKILL)
	except Exception as e:
		print("Error killing gphoto2, {}".format(e))


# Load the background template
bgimage = PIL.Image.open(templatePath)
bgimage_print = PIL.Image.open(templatePath_print)


print_image = Image.new(mode="RGBA", size=(600,1800))

#Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# initialise pygame
pygame.init()  # Initialise pygame
pygame.mouse.set_visible(False) #hide the mouse cursor

if not debug:
	infoObject = pygame.display.Info()

	transform_x = infoObject.current_w # how wide to scale the jpg when replaying
	transfrom_y = infoObject.current_h # how high to scale the jpg when replaying

	screen = pygame.display.set_mode((infoObject.current_w,infoObject.current_h), pygame.FULLSCREEN)  # Full screen 
	background = pygame.Surface(screen.get_size())  # Create the background object
	background = background.convert()  # Convert it to a background

	screenPicture = pygame.display.set_mode((infoObject.current_w,infoObject.current_h), pygame.FULLSCREEN)  # Full screen
	backgroundPicture = pygame.Surface(screenPicture.get_size())  # Create the background object
	backgroundPicture = background.convert()  # Convert it to a background
else:
	debug_width = 960*2
	debug_height = 540*2

	screen = pygame.display.set_mode((debug_width,debug_height), pygame.FULLSCREEN)  # Full screen 
	background = pygame.Surface((debug_width,debug_height))  # Create the background object
	background = background.convert()  # Convert it to a background

	screenPicture = pygame.display.set_mode((debug_width,debug_height), pygame.FULLSCREEN)  # Full screen
	backgroundPicture = pygame.Surface((debug_width,debug_height))  # Create the background object
	backgroundPicture = background.convert()  # Convert it to a background

	transform_x = debug_width # how wide to scale the jpg when replaying
	transfrom_y = debug_height # how high to scale the jpg when replaying

if not debug:
	kill_gphoto2()
	camera = gp.Camera()
	camera.init()

# A function to handle keyboard/mouse/device input events
def input(events):
	for event in events:  # Hit the ESC key to quit the slideshow.
		print(event.type)
		if (event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE)):
			pygame.quit()
			
# set variables to properly display the image on screen at right ratio
def set_dimensions(img_w, img_h):
	# Note this only works when in booting in desktop mode. 
	# When running in terminal, the size is not correct (it displays small). Why?
	# connect to global vars
	global transform_y, transform_x, offset_y, offset_x

	# based on output screen resolution, calculate how to display
	ratio_h = (infoObject.current_w * img_h) / img_w 

	if (ratio_h < infoObject.current_h):
		#Use horizontal black bars
		#print "horizontal black bars"
		transform_y = ratio_h
		transform_x = infoObject.current_w
		offset_y = (infoObject.current_h - ratio_h) / 2
		offset_x = 0
	elif (ratio_h > infoObject.current_h):
		#Use vertical black bars
		#print "vertical black bars"
		transform_x = (infoObject.current_h * img_w) / img_h
		transform_y = infoObject.current_h
		offset_x = (infoObject.current_w - transform_x) / 2
		offset_y = 0
	else:
		#No need for black bars as photo ratio equals screen ratio
		#print "no black bars"
		transform_x = infoObject.current_w
		transform_y = infoObject.current_h
		offset_y = offset_x = 0

# set variables to properly display the image on screen at right ratio
def set_dimensions_debug(img_w, img_h):
	# Note this only works when in booting in desktop mode. 
	# When running in terminal, the size is not correct (it displays small). Why?
	# connect to global vars
	global transform_y, transform_x, offset_y, offset_x

	# based on output screen resolution, calculate how to display
	ratio_h = (debug_width * img_h) / img_w 

	if (ratio_h < debug_height):
		#Use horizontal black bars
		#print "horizontal black bars"
		transform_y = ratio_h
		transform_x = debug_width
		offset_y = (debug_height- ratio_h) / 2
		offset_x = 0
	elif (ratio_h > debug_height):
		#Use vertical black bars
		#print "vertical black bars"
		transform_x = (debug_height * img_w) / img_h
		transform_y = debug_height
		offset_x = (debug_width- transform_x) / 2
		offset_y = 0
	else:
		#No need for black bars as photo ratio equals screen ratio
		#print "no black bars"
		transform_x = debug_width
		transform_y = debug_height
		offset_y = offset_x = 0

def InitFolder():
	print("herhehrhher")
	#kill all gphoto2 processes:
	

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
		
def DisplayText(fontSize, textToDisplay):
	global Numeral
	global Message
	global screen
	global background
	global pygame
	global ImageShowed
	global screenPicture
	global backgroundPicture
	global CountDownPhoto

	if (BackgroundColor != ""):
			#print(BackgroundColor)
			background.fill(pygame.Color("black"))
	if (textToDisplay != ""):
			#print(displaytext)
			font = pygame.font.Font(None, fontSize)
			text = font.render(textToDisplay, 1, (227, 157, 200))
			textpos = text.get_rect()
			textpos.centerx = background.get_rect().centerx
			textpos.centery = background.get_rect().centery
			if(ImageShowed):
					backgroundPicture.blit(text, textpos)
			else:
					background.blit(text, textpos)
				
def UpdateDisplay(dfault = 1):
	# init global variables from main thread
	global Numeral
	global Message
	global screen
	global background
	global pygame
	global ImageShowed
	global screenPicture
	global backgroundPicture
	global CountDownPhoto
   
	background.fill(pygame.Color("white"))  # White background
	#DisplayText(100, Message)
	#DisplayText(800, Numeral)
	#DisplayText(500, CountDownPhoto)
	pygame.font.init()
	if (BackgroundColor != ""):
			#print(BackgroundColor)
			background.fill(pygame.Color("black"))
	if (Message != ""):
			#print(displaytext)
			font = pygame.font.Font(None, 100)
			text = font.render(Message, 1, (6, 96, 6))
			textpos = text.get_rect()
			textpos.centerx = background.get_rect().centerx
			textpos.centery = background.get_rect().centery
			if(ImageShowed):
					backgroundPicture.blit(text, textpos)
			else:
					background.blit(text, textpos)

	if (Numeral != ""):
			#print(displaytext)
			font = pygame.font.Font(None, 800)
			text = font.render(Numeral, 1, (6, 96, 6))
			textpos = text.get_rect()
			textpos.centerx = background.get_rect().centerx
			textpos.centery = background.get_rect().centery
			if(ImageShowed):
					backgroundPicture.blit(text, textpos)
			else:
					background.blit(text, textpos)

	if (CountDownPhoto != ""):
			#print(displaytext)
			font = pygame.font.Font(None, 500)
			text = font.render(CountDownPhoto, 1, (6, 96, 6))
			textpos = text.get_rect()
			textpos.centerx = background.get_rect().centerx
			textpos.centery = background.get_rect().centery
			if(ImageShowed):
					backgroundPicture.blit(text, textpos)
			else:
					background.blit(text, textpos)
	
	if(ImageShowed == True):
		screenPicture.blit(backgroundPicture, (0, 0))   	
	else:
		screen.blit(background, (0, 0))
   
	pygame.display.flip()
	return


def ShowPicture(file, delay):
	global pygame
	global screenPicture
	global backgroundPicture
	global ImageShowed
	backgroundPicture.fill(pygame.Color("white"))
	print(file)
	img = pygame.image.load(file)
	img = pygame.transform.scale(img, (int(img.get_size()[0]/img.get_size()[1]*screenPicture.get_size()[1]),int(screenPicture.get_size()[1])))  # Make the image full screen
	#backgroundPicture.set_alpha(200)
	screen.fill(pygame.Color("white")) # clear the screen	
	backgroundPicture.blit(img, (0,0))
	screen.blit(backgroundPicture, (screenPicture.get_size()[0]/2-img.get_size()[0]/2,\
									screenPicture.get_size()[1]/2-img.get_size()[1]/2))
	pygame.display.flip()  # update the display
	ImageShowed = True
	time.sleep(delay)
	

def ShowPicture_final(file, delay):
	global pygame
	global screenPicture
	global backgroundPicture
	global ImageShowed
	backgroundPicture.fill(pygame.Color("white"))
	print(file)
	img = pygame.image.load(file)
	img = pygame.transform.scale(img, (int(img.get_size()[0]/img.get_size()[1]*screenPicture.get_size()[1]),int(screenPicture.get_size()[1])))  # Make the image full screen
	#backgroundPicture.set_alpha(200)
	screen.fill(pygame.Color("white")) # clear the screen	
	backgroundPicture.blit(img, (0,0))
	screen.blit(backgroundPicture, (screenPicture.get_size()[0]/4-img.get_size()[0]/2,\
									screenPicture.get_size()[1]/4-img.get_size()[1]/2))
	pygame.display.flip()  # update the display
	ImageShowed = True
	time.sleep(delay)

# display one image on screen
def show_image(image_path):	
	screen.fill(pygame.Color("white")) # clear the screen	
	img = pygame.image.load(image_path) # load the image
	img = img.convert()	
	if not debug:
		set_dimensions(img.get_width(), img.get_height()) # set pixel dimensions based on image	
		x = (infoObject.current_w / 2) - (img.get_width() / 2)
		y = (infoObject.current_h / 2) - (img.get_height() / 2)
	else:
		set_dimensions_debug(img.get_width(), img.get_height()) # set pixel dimensions based on image	
		x = (debug_width / 2) - (img.get_width() / 2)
		y = (debug_height / 2) - (img.get_height() / 2)
	screen.blit(img,(x,y))
	pygame.display.flip()

def CapturePicture():
	global imagecounter
	global imagefolder
	global Numeral
	global Message
	global screen
	global background
	global screenPicture
	global backgroundPicture
	global pygame
	global ImageShowed
	global CountDownPhoto
	global BackgroundColor
	global camera
	global debug
	
	BackgroundColor = ""
	Numeral = ""
	Message = ""
	UpdateDisplay()
	if not debug:
		time.sleep(1)
	else:
		time.sleep(0.1)
	CountDownPhoto = ""
	UpdateDisplay()
	background.fill(pygame.Color("black"))
	screen.blit(background, (0, 0))
	pygame.display.flip()
	#camera.start_preview()
	BackgroundColor = "black"
	
	message_list = ["Choose a pose!", "Looking great", "Where's that big smile?"]

	for x in range(3, -1, -1):
		if x == 0:						
			Numeral = ""
			Message = message_list[int(random.random() * len(message_list))] 
		else:						
			Numeral = str(x)
			Message = ""	
		BackgroundColor = ""			
		UpdateDisplay()
		if not debug:
			time.sleep(1)
		else:
			time.sleep(0.1)
		BackgroundColor = ""
		Numeral = ""
		Message = ""
		UpdateDisplay()
	imagecounter = imagecounter + 1
	ts = time.time()
	filename = os.path.join(imagefolder, 'images', str(imagecounter)+"_"+str(ts) + '.jpg')
	if not debug:
		try:
			file_path = camera.capture(gp.GP_CAPTURE_IMAGE)
			camera_file  = camera.file_get(file_path.folder, file_path.name, gp.GP_FILE_TYPE_NORMAL)
			camera_file.save(filename)
		except Exception as e:
			try:
				kill_gphoto2()
				camera = gp.Camera()
				camera.init()
				camera.capture(gp.GP_CAPTURE_IMAGE)
				camera_file  = camera.file_get(file_path.folder, file_path.name, gp.GP_FILE_TYPE_NORMAL)
				camera_file
			except Exception as e:
				print("prblem with tknig the picture, will save a random color")
				picture =  PIL.Image.new('RGB', (5184, 3456), (randint(0,255),randint(0,255),randint(0,255)))
				camera_file = picture.save(filename) 
	else:
		picture =  PIL.Image.new('RGB', (5184, 3456), (randint(0,255),randint(0,255),randint(0,255)))
		camera_file = picture.save(filename) 
	#camera.capture(filename, resize=(IMAGE_WIDTH, IMAGE_HEIGHT))
	#camera.stop_preview()
	ShowPicture(filename, 2)
	ImageShowed = False
	return filename
	
	
def TakePictures():
	global imagecounter
	global imagefolder
	global Numeral
	global Message
	global screen
	global background
	global pygame
	global ImageShowed
	global CountDownPhoto
	global BackgroundColor
	global Printing
	global PhotosPerCart
	global TotalImageCount

	input(pygame.event.get())
	CountDownPhoto = "1/3"		
	filename1 = CapturePicture()

	CountDownPhoto = "2/3"
	filename2 = CapturePicture()

	CountDownPhoto = "3/3"
	filename3 = CapturePicture()

	CountDownPhoto = ""
	Message = "Processing your photos...."
	UpdateDisplay()


	photo1 = PIL.Image.open(filename1)
	photo2 = PIL.Image.open(filename2)
	photo3 = PIL.Image.open(filename3)
	size_ratio = photo1.size[0]/photo1.size[1]
	margin = 60
	photo1 = photo1.resize((bgimage.size[0]-margin*2,int((bgimage.size[0]-margin)/size_ratio)))
	photo2 = photo2.resize((bgimage.size[0]-margin*2,int((bgimage.size[0]-margin)/size_ratio)))
	photo3 = photo3.resize((bgimage.size[0]-margin*2,int((bgimage.size[0]-margin)/size_ratio)))
	

	photo1_print = photo1.resize((int(bgimage_print.size[0]/2)-margin*2,int((bgimage_print.size[0]/2-margin)/size_ratio)))
	photo2_print = photo2.resize((int(bgimage_print.size[0]/2)-margin*2,int((bgimage_print.size[0]/2-margin)/size_ratio)))
	photo3_print = photo3.resize((int(bgimage_print.size[0]/2)-margin*2,int((bgimage_print.size[0]/2-margin)/size_ratio)))
	
	TotalImageCount = TotalImageCount + 1
	
	bgimage.paste(photo1, (margin, margin+80))
	bgimage.paste(photo2, (margin, photo1.size[1]+margin+185))
	bgimage.paste(photo3, (margin, photo1.size[1]+photo2.size[1]+margin+150*2))
	
	bgimage_print.paste(photo1_print, (margin, margin+80))
	bgimage_print.paste(photo2_print, (margin, photo1_print.size[1]+margin+185))
	bgimage_print.paste(photo3_print, (margin, photo1_print.size[1]+photo2_print.size[1]+margin+150*2))
	bgimage_print.paste(photo1_print, (margin+int(bgimage_print.size[0]/2), margin+80))
	bgimage_print.paste(photo2_print, (margin+int(bgimage_print.size[0]/2), photo1_print.size[1]+margin+185))
	bgimage_print.paste(photo3_print, (margin+int(bgimage_print.size[0]/2), photo1_print.size[1]+photo2_print.size[1]+margin+150*2))
	
	
	# Create the final filename
	# Create the final filename
	ts = time.time()
	Final_Image_Name = os.path.join(imagefolder, "final", "Final_" + str(TotalImageCount)+"_"+str(ts) + ".jpg")
	print(Final_Image_Name)
	# Save it to the usb drive
	bgimage.convert("RGB").save(Final_Image_Name)

	# Save a temp file, its faster to print from the pi than usb
	bgimage.convert("RGB").save('/home/pi/Desktop/tempprint.jpg')
	# ShowPicture_final('/home/pi/Desktop/tempprint.jpg',3)
	
	ImageShowed = False
	# Message = "Press the button if you want to print this photo!"
	# UpdateDisplay()
	# time.sleep(1)
	# Message = ""
	# UpdateDisplay()
	Printing = False
	WaitForPrintingEvent(Final_Image_Name,3)
	Numeral = ""
	Message = ""
	print(Printing)
	if Printing:
		if (TotalImageCount <= PhotosPerCart):
			if os.path.isfile('/home/pi/Desktop/tempprint.jpg'):
				# Open a connection to cups
				conn = cups.Connection()
				# get a list of printers
				printers = conn.getPrinters()
				# select printer 0
				printer_name = list(printers.keys())[0]
				Message = "Printing... wait 40sec :)"
				UpdateDisplay()
				time.sleep(1)
				# print the buffer file
				printqueuelength = len(conn.getJobs())
				if printqueuelength > 1:
					ShowPicture('/home/pi/Desktop/tempprint.jpg',3)
					conn.enablePrinter(printer_name)
					Message = "There was an error... call Nuno for help :)"				
					UpdateDisplay()
					time.sleep(1)
				else:
					conn.printFile(printer_name, '/home/pi/Desktop/tempprint.jpg', "PhotoBooth", {})
					if not debug:
						time.sleep(40)
					else:
						time.sleep(1)
					
					Printing = False
					WaitForPrintingEvent_personal(Final_Image_Name,3)
					Numeral = ""
					Message = ""
					print(Printing)
					if Printing:
						if (TotalImageCount <= PhotosPerCart):
							if os.path.isfile('/home/pi/Desktop/tempprint.jpg'):
								# Open a connection to cups
								conn = cups.Connection()
								# get a list of printers
								printers = conn.getPrinters()
								# select printer 0
								printer_name = list(printers.keys())[0]
								Message = "Printing...wait 40 sec :)"
								UpdateDisplay()
								time.sleep(1)
								# print the buffer file
								printqueuelength = len(conn.getJobs())
								if printqueuelength > 1:
									ShowPicture('/home/pi/Desktop/tempprint.jpg',3)
									conn.enablePrinter(printer_name)
									Message = "There was an error... call Nuno for help :)"				
									UpdateDisplay()
									time.sleep(1)
								else:
									conn.printFile(printer_name, '/home/pi/Desktop/tempprint.jpg', "PhotoBooth", {})
									if not debug:
										time.sleep(40)
									else:
										time.sleep(1)
						else:
							Message = "Strange.. this shouldn't happen. Try again! :)"
							Numeral = ""
							UpdateDisplay()
							time.sleep(5)
					else:

						screen.fill(pygame.Color("white"))
						pygame.font.init()
						font = pygame.font.Font(None, int(60*screenPicture.get_size()[1]/540))
						text = font.render("Alright, the photo will not be printed.", 1, (6, 96, 6))
						screen.blit(text, (screenPicture.get_size()[0]/2-text.get_size()[0]/2,\
											screenPicture.get_size()[1]/4))
						text = font.render("Don't worry, it is saved", 1, (6, 96, 6))
						screen.blit(text, (screenPicture.get_size()[0]/2-text.get_size()[0]/2,\
											screenPicture.get_size()[1]/4+1.5*text.get_size()[1]))
						text = font.render("and we can send it to you later! :)", 1, (6, 96, 6))
						screen.blit(text, (screenPicture.get_size()[0]/2-text.get_size()[0]/2,\
											screenPicture.get_size()[1]/4+3*text.get_size()[1]))
						pygame.display.flip()  # update the display
						time.sleep(8)
		else:
			Message = "Strange.. this shouldn't happen. Try again! :)"
			Numeral = ""
			UpdateDisplay()
			time.sleep(5)
	else:

		screen.fill(pygame.Color("white"))
		pygame.font.init()
		font = pygame.font.Font(None, int(60*screenPicture.get_size()[1]/540))
		text = font.render("Alright, the photo will not be printed.", 1, (6, 96, 6))
		screen.blit(text, (screenPicture.get_size()[0]/2-text.get_size()[0]/2,\
							screenPicture.get_size()[1]/4))
		text = font.render("Don't worry, it is saved", 1, (6, 96, 6))
		screen.blit(text, (screenPicture.get_size()[0]/2-text.get_size()[0]/2,\
							screenPicture.get_size()[1]/4+1.5*text.get_size()[1]))
		text = font.render("and we can send it to you later! :)", 1, (6, 96, 6))
		screen.blit(text, (screenPicture.get_size()[0]/2-text.get_size()[0]/2,\
							screenPicture.get_size()[1]/4+3*text.get_size()[1]))
		pygame.display.flip()  # update the display
		time.sleep(8)

	Message = ""
	Numeral = ""
	ImageShowed = False
	UpdateDisplay()
	time.sleep(1)

def MyCallback(channel):
	global Printing
	GPIO.remove_event_detect(BUTTON_PIN)
	Printing=True
	
def WaitForPrintingEvent(file, delay):
	global BackgroundColor
	global Numeral
	global Message
	global Printing
	global pygame
	countDown = 5
	GPIO.add_event_detect(BUTTON_PIN, GPIO.RISING)
	GPIO.add_event_callback(BUTTON_PIN, MyCallback)

	backgroundPicture.fill(pygame.Color("white"))
	print(file)
	img = pygame.image.load(file)
	img = pygame.transform.scale(img, (int(img.get_size()[0]/img.get_size()[1]*screenPicture.get_size()[1]),int(screenPicture.get_size()[1])))  # Make the image full screen
	#backgroundPicture.set_alpha(200)
	screen.fill(pygame.Color("white")) # clear the screen	
	backgroundPicture.blit(img, (0,0))
	screen.blit(backgroundPicture, (screenPicture.get_size()[0]/4-img.get_size()[0]/2,\
									screenPicture.get_size()[1]/2-img.get_size()[1]/2))
	# pygame.display.flip()  # update the display
	ImageShowed = True
	time.sleep(delay)

	pygame.display.flip()  # update the display



	while Printing == False and countDown > 0:
		if(Printing == True):
			return
		for event in pygame.event.get():			
			if event.type == pygame.KEYDOWN:				
				if event.key == pygame.K_DOWN:
					GPIO.remove_event_detect(BUTTON_PIN)
					Printing = True
					return
				if event.key == pygame.K_ESCAPE:
					print("escpa")
					pygame.quit()

		if not debug:
			right_screen = pygame.Surface((screenPicture.get_size()[0]/2,screenPicture.get_size()[1]))
		else:
			right_screen = pygame.Surface((debug_width/2,debug_height))
		right_screen = right_screen.convert() 
		right_screen.fill(pygame.Color("white"))
		pygame.font.init()
		font = pygame.font.Font(None, int(40*screenPicture.get_size()[1]/540))
		text = font.render("Press the button if" , 1, (6, 96, 6))

		right_screen.blit(text, (right_screen.get_size()[0]/2-text.get_size()[0]/2,\
										right_screen.get_size()[1]/10-text.get_size()[1]/2))
		text = font.render("you want to print this photo!" , 1, (6, 96, 6))

		right_screen.blit(text, (right_screen.get_size()[0]/2-text.get_size()[0]/2,\
										right_screen.get_size()[1]/10+text.get_size()[1]/2))
		font = pygame.font.Font(None,int(300*screenPicture.get_size()[1]/540))
		text = font.render(str(countDown) , 1, (6, 96, 6))
		right_screen.blit(text, (right_screen.get_size()[0]/2-text.get_size()[0]/2,\
									right_screen.get_size()[1]/2-text.get_size()[1]/2))
		
		screen.blit(right_screen,  (screenPicture.get_size()[0]/2-img.get_size()[0]/2,\
									screenPicture.get_size()[1]/5*3-img.get_size()[1]/2))
		
		pygame.display.flip()  # update the display
		# BackgroundColor = ""
		# Numeral = str(countDown)
		# Message = ""
		# UpdateDisplay()		







		countDown = countDown - 1
		time.sleep(1)

	GPIO.remove_event_detect(BUTTON_PIN)


def WaitForPrintingEvent_personal(file, delay):
	global BackgroundColor
	global Numeral
	global Message
	global Printing
	global pygame
	countDown = 5
	GPIO.add_event_detect(BUTTON_PIN, GPIO.RISING)
	GPIO.add_event_callback(BUTTON_PIN, MyCallback)

	backgroundPicture.fill(pygame.Color("white"))
	print(file)
	img = pygame.image.load(file)
	img = pygame.transform.scale(img, (int(img.get_size()[0]/img.get_size()[1]*screenPicture.get_size()[1]),int(screenPicture.get_size()[1])))  # Make the image full screen
	#backgroundPicture.set_alpha(200)
	screen.fill(pygame.Color("white")) # clear the screen	
	backgroundPicture.blit(img, (0,0))
	screen.blit(backgroundPicture, (screenPicture.get_size()[0]/4-img.get_size()[0]/2,\
									screenPicture.get_size()[1]/2-img.get_size()[1]/2))
	# pygame.display.flip()  # update the display
	ImageShowed = True
	time.sleep(delay)

	pygame.display.flip()  # update the display



	while Printing == False and countDown > 0:
		if(Printing == True):
			return
		for event in pygame.event.get():			
			if event.type == pygame.KEYDOWN:				
				if event.key == pygame.K_DOWN:
					GPIO.remove_event_detect(BUTTON_PIN)
					Printing = True
					return
				if event.key == pygame.K_ESCAPE:
					print("escpa")
					pygame.quit()

		if not debug:
			right_screen = pygame.Surface((screenPicture.get_size()[0]/2,screenPicture.get_size()[1]))
		else:
			right_screen = pygame.Surface((debug_width/2,debug_height))
		right_screen = right_screen.convert() 
		right_screen.fill(pygame.Color("white"))
		pygame.font.init()
		font = pygame.font.Font(None, int(40*screenPicture.get_size()[1]/540))
		text = font.render("Press the button if you also" , 1, (6, 96, 6))

		right_screen.blit(text, (right_screen.get_size()[0]/2-text.get_size()[0]/2,\
										right_screen.get_size()[1]/10-text.get_size()[1]/2))
		text = font.render("want to print this photo to keep!" , 1, (6, 96, 6))

		right_screen.blit(text, (right_screen.get_size()[0]/2-text.get_size()[0]/2,\
										right_screen.get_size()[1]/10+text.get_size()[1]/2))
		font = pygame.font.Font(None,int(300*screenPicture.get_size()[1]/540))
		text = font.render(str(countDown) , 1, (6, 96, 6))
		right_screen.blit(text, (right_screen.get_size()[0]/2-text.get_size()[0]/2,\
									right_screen.get_size()[1]/2-text.get_size()[1]/2))
		
		screen.blit(right_screen,  (screenPicture.get_size()[0]/2-img.get_size()[0]/2,\
									screenPicture.get_size()[1]/5*3-img.get_size()[1]/2))
		
		pygame.display.flip()  # update the display
		# BackgroundColor = ""
		# Numeral = str(countDown)
		# Message = ""
		# UpdateDisplay()		







		countDown = countDown - 1
		time.sleep(1)

	GPIO.remove_event_detect(BUTTON_PIN)
		
	
def WaitForEvent():
	global pygame
	# NotEvent = True
	# while NotEvent:
	# 	print("here")
		
	notEvent = True
	clock = pygame.time.Clock()
	while notEvent:
		input_state = GPIO.input(BUTTON_PIN)
		if input_state == False:
			print("no event")
			NotEvent = False			
			return 	
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				print("pressed")
				if event.key == pygame.K_ESCAPE:
					print("escpa")
					pygame.quit()
				if event.key == pygame.K_DOWN:
					print("k_down")
					notEvent = False
					return
				# time.sleep(0.2)



def loop():
	clock = pygame.time.Clock()
	while not False:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return(False)
			if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
				print("escpa")
				pygame.quit()
			if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
				print("here")
		clock.tick(30)

def main(*args):
	InitFolder()
	while True:
		show_image('images/photo_booth_start.jpg')
		WaitForEvent()
		print("here")
		time.sleep(0.2)
		TakePictures()	
	GPIO.cleanup()

main()

# def main(threadName, *args):
# 	InitFolder()
# 	loop()
# 	while True:
# 		show_image('images/start_camera.jpg')
# 		WaitForEvent()
# 		time.sleep(0.2)
# 		TakePictures()
# 	GPIO.cleanup()


# launch the main thread
# Thread(target=main, args=('Main', 1)).start()

