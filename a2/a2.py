# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw
import numpy as np
import math
from scipy import signal
import ncc

#Open all of the images
judybats = Image.open("/Users/osman/School/CPSC425/cpsc425/a2/hw2/faces/judybats.jpg")
sports = Image.open("/Users/osman/School/CPSC425/cpsc425/a2/hw2/faces/sports.jpg")
fans = Image.open("/Users/osman/School/CPSC425/cpsc425/a2/hw2/faces/fans.jpg")
family = Image.open("/Users/osman/School/CPSC425/cpsc425/a2/hw2/faces/family.jpg")
students = Image.open("/Users/osman/School/CPSC425/cpsc425/a2/hw2/faces/students.jpg")
tree = Image.open("/Users/osman/School/CPSC425/cpsc425/a2/hw2/faces/tree.jpg")

#A function for creating a pyramid of images where every successor image is 0.75x size of its predecessor
def MakePyramid(image, minsize):
  # get the dimensions of the image
  width, height = image.size
  pyramid = [image]
  #check if reducing dimensions further will make width or height go below minsize
  while (width * 0.75 > minsize) and (height * 0.75 > minsize):
  	width = int(width*0.75)
  	height = int(height*0.75)
  	#create a smaller image
  	image = image.resize((width, height), Image.BICUBIC)
  	#add the smaller image to the list
  	pyramid.append(image)
  return pyramid


def ShowPyramid(pyramid):
  #Get the dimensions of the original image
  width, height = pyramid[0].size
  i = 0
  resultWidth = 0
  
  #Calculate the total width of the pyramid
  for image in pyramid:
      widthTmp, heightTmp = image.size
      resultWidth = resultWidth + widthTmp
      i = i + 1
      
  #Create a blank canvas/image to paste our pyramid onto
  canvas = Image.new("L", (int(resultWidth), height))
  offset_x = 0
  offset_y = 0
  
  #Paste image from pyramid to our canvas
  for image in pyramid:
  	width, height = image.size
 	canvas.paste(image,(offset_x,offset_y))
 	offset_x = offset_x + width
  canvas.show()
  
suggestedTemplateWidth = 15

#Function for finding the occurences of the template in a given image
def FindTemplate(pyramid, template, threshold):
    #Get dimensions of the template
    tempWidth, tempHeight = template.size
    #Resize template to the suggested size in order to speed up NCC computations
    template = template.resize((suggestedTemplateWidth, (tempHeight*suggestedTemplateWidth/tempWidth)), Image.BICUBIC)
    
    #Call NCC and get Cross Correlation Coefficients for every image in the pyramid
    crossCorrCoefficients = []
    for image in pyramid:
        value = ncc.normxcorr2D(image, template)
        crossCorrCoefficients.append(value)
    
    
    #Once you have the NCC stuff use that to find faces by checking every pixel
    k = 0
    
    #Loop over Cross Correlation Coefficients List of every image in the pyramid 
    for correlationArray in crossCorrCoefficients:
        
        #access elements of pixel correlation matrix
        for i in range(len(correlationArray)):
            for j in range(len(correlationArray[0])):
                #if correlation at the specific pixel is above threshold then draw a rectangle around the face
                if correlationArray[i][j] > threshold:
                    draw = ImageDraw.Draw(pyramid[0])
                    
                    #Draw rectangle around a detected face
                    draw.line(((j-tempWidth/2)/(0.75**k),(i-tempHeight/2)/(0.75**k),(j+tempWidth/2)/(0.75**k),(i-tempHeight/2)/(0.75**k)),fill="red",width=2)
                    draw.line(((j-tempWidth/2)/(0.75**k),(i-tempHeight/2)/(0.75**k),(j-tempWidth/2)/(0.75**k),(i+tempHeight/2)/(0.75**k)),fill="red",width=2)
                    draw.line(((j-tempWidth/2)/(0.75**k),(i+tempHeight/2)/(0.75**k),(j+tempWidth/2)/(0.75**k),(i+tempHeight/2)/(0.75**k)),fill="red",width=2)
                    draw.line(((j+tempWidth/2)/(0.75**k),(i+tempHeight/2)/(0.75**k),(j+tempWidth/2)/(0.75**k),(i-tempHeight/2)/(0.75**k)),fill="red",width=2)
                    
                    #convert rectangle to color red
                    pyramid[0] = pyramid[0].convert('RGB')
                    del draw
        k = k+1
    #show the original image
    pyramid[0].show()
    return 0

#DEMO BELOW. CODE BELOW CALLS THE FUNCTIONS AND PERFORMS THE NECESSARY OPERATIONS

#Pyramids of the images
pyramidJudybats = MakePyramid(judybats, 15)
pyramidSports = MakePyramid(sports, 15)
pyramidFans = MakePyramid(fans, 15)
pyramidFamily = MakePyramid(family, 15)
pyramidStudents = MakePyramid(students, 15)
pyramidTree = MakePyramid(tree, 15)

ShowPyramid(pyramidJudybats)

#8 false negatives and 8 false positives with threshold = 0.6
threshold = 0.6

template = Image.open("/Users/osman/School/CPSC425/cpsc425/a2/hw2/faces/template.jpg")
FindTemplate(pyramidJudybats, template, threshold)
FindTemplate(pyramidSports, template, threshold)
FindTemplate(pyramidFans, template, threshold)
FindTemplate(pyramidFamily, template, threshold)
FindTemplate(pyramidStudents, template, threshold)
FindTemplate(pyramidTree, template, threshold)