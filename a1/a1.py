from PIL import Image
import numpy as np
import math
from scipy import signal

#returns a 2D box filter of size - size X size
def boxfilter(size):
    assert size % 2 != 0, "Dimension must be odd!"
    assert size > 0, "Dimension must be positive!"
    return np.full((size, size), 1.0/(size*size))
    
# Box filter Tests: 
#boxfilter(7)  # Should run normally
#boxfilter(-1) # Should trigger Assertion error must be positive
#boxfilter(0)  # Should trigger Assertion error must be odd
#boxfilter(6)  # Should trigger Assertion error must be odd

print("boxfilter(5):")
print(boxfilter(5))
print("boxfilter(4):")
#print(boxfilter(4))
print("boxfilter(3):")
print(boxfilter(3))

# Returns 1D Gaussian
def gauss1d(sigma):
    
    #Multiply sigma by 6 and take its ceiling
    temp = int(math.ceil(sigma*6))
    
    #Round up to the next odd integer
    size = temp + 1 if temp % 2 == 0 else temp
    
    #Create array
    sigmaOneArray = np.arange(int(math.ceil(-size/2.0)), int(math.ceil(size/2.0)))
    
    #apply gaussian
    gaussianUnNormalizedArray = map(lambda x: math.exp(- x**2 / (2*sigma**2)), sigmaOneArray)

    arraySum = np.sum(gaussianUnNormalizedArray)  
    #return normalized array
    return map(lambda x: x/arraySum, gaussianUnNormalizedArray)
 
# Gaussian 1D tests:
print("gauss1d(0.3):")
print(gauss1d(0.3))
print("gauss1d(0.5):")
print(gauss1d(0.5))
print("gauss1d(1):")
print(gauss1d(1))
print("gauss1d(2):")
print(gauss1d(2))

def gauss2d(sigma):
    
    #Return 1D gaussian with given sigma
    oneDArray = np.array(gauss1d(sigma))
    
    #Create new row
    oneDArray = oneDArray[np.newaxis]
    
    #2D convolution of 1D gaussian with its transpose is the answer
    return signal.convolve2d(oneDArray, oneDArray.T)

print("gauss2d(0.5):")
print(gauss2d(0.5))
print("gauss2d(1):")
print(gauss2d(1))


def gaussconvolve2d(array,sigma):
    
    #Use 2D Gaussian as our filter
    filter = gauss2d(sigma)
    
    # 2D Convolution of our array and 2D Gaussian is the answer
    return signal.convolve2d(array,filter,'same')
    
dog = Image.open("/Users/osman/School/CPSC425/a1/dog.jpg")

#Convert to grey scale
dog = dog.convert("L")

#Convert dog image to numpy array
dogArray = np.asarray(dog)

#do the 2D gaussian convolution on our array version of image
dogArray = gaussconvolve2d(dog,3)

#convert dog array back to normal image so that we can see it
newDog = Image.fromarray(dogArray)
#newDog.save('/Users/osman/School/CPSC425/a1/greyDog.png','PNG')

#display the image
newDog.show()


#Part 2

#Question 1

#Open dog image
dog = Image.open("/Users/osman/School/CPSC425/a1/dog.jpg")

#Convert dog image to numpy array
dogArray = np.asarray(dog, dtype=float)

#divide the image dog array into seperate RGB channels
blue, green, red    = dogArray[:, :, 0], dogArray[:, :, 1], dogArray[:, :, 2]

#Blue channel
blueArray = gaussconvolve2d(blue,1)

#green channel
greenArray = gaussconvolve2d(green, 1)

#red channel
redArray = gaussconvolve2d(red,1)

#create our merged general RGB array
rgbArrayDog = np.zeros((361,410,3), 'uint8')
rgbArrayDog[..., 0] = blueArray
rgbArrayDog[..., 1] = greenArray
rgbArrayDog[..., 2] = redArray

#Convert merged RGB array to image
img = Image.fromarray(rgbArrayDog)
img.save('/Users/osman/School/CPSC425/a1/lowDog.png','PNG')

#show image
img.show()


#Question 2

#open cat image
cat = Image.open("/Users/osman/School/CPSC425/a1/cat.jpg")

#convert cat image to numpy array representation of the image
catArray = np.asarray(cat, dtype=float)

#divive the image array into seperate RGB channels
blue, green, red    = catArray[:, :, 0], catArray[:, :, 1], catArray[:, :, 2]

#Blue channel
blueArray = gaussconvolve2d(blue,1)

#green channel
greenArray = gaussconvolve2d(green,1)

#red channel
redArray = gaussconvolve2d(red,1)

#Subtract 2D gaussian convolution version of channels from the original channels
resultBlue = blue - blueArray
resultGreen = green - greenArray
resultRed = red - redArray

#Merge channels back together into one image array represantion
rgbArrayCat = np.zeros((361,410,3), 'uint8')

#note: we have to add 0.5 or 128 as was mentioned in the assignment
rgbArrayCat[..., 0] = resultBlue + 128
rgbArrayCat[..., 1] = resultGreen + 128
rgbArrayCat[..., 2] = resultRed + 128

#merge the image and display it
img = Image.fromarray(rgbArrayCat)
img.save('/Users/osman/School/CPSC425/a1/highCat.png','PNG')
img.show()

#Question 3
rgbArray = np.zeros((361,410,3), 'uint8')

#add the images and subtract 128 in order to fit it inside our 0 to 255 limit
rgbArray[..., 0] = (rgbArrayCat[..., 0] + rgbArrayDog[..., 0] - 128)
rgbArray[..., 1] = (rgbArrayCat[..., 1] + rgbArrayDog[..., 1] - 128)
rgbArray[..., 2] = (rgbArrayCat[..., 2] + rgbArrayDog[..., 2] - 128)

# no need for this because image is clipped from 0 to 255 already, values were
# float in the beginning as well but highlights remained nevertheless for some reason
# rgbArray = np.clip(rgbArray, 0, 255)

#Merged the combined dog and cat image and display it
img = Image.fromarray(rgbArray)
img.save('/Users/osman/School/CPSC425/a1/sigma1.png','PNG')
img.show()





