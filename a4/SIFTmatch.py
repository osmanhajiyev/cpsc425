from PIL import Image, ImageDraw
import numpy as np
import csv
import math

def ReadKeys(image):
    """Input an image and its associated SIFT keypoints.

    The argument image is the image file name (without an extension).
    The image is read from the PGM format file image.pgm and the
    keypoints are read from the file image.key.

    ReadKeys returns the following 3 arguments:

    image: the image (in PIL 'RGB' format)

    keypoints: K-by-4 array, in which each row has the 4 values specifying
    a keypoint (row, column, scale, orientation).  The orientation
    is in the range [-PI, PI] radians.

    descriptors: a K-by-128 array, where each row gives a descriptor
    for one of the K keypoints.  The descriptor is a 1D array of 128
    values with unit length.
    """
    im = Image.open(image+'.pgm').convert('RGB')
    keypoints = []
    descriptors = []
    first = True
    with open(image+'.key','rb') as f:
        reader = csv.reader(f, delimiter=' ', quoting=csv.QUOTE_NONNUMERIC,skipinitialspace = True)
        descriptor = []
        for row in reader:
            if len(row) == 2:
                assert first, "Invalid keypoint file header."
                assert row[1] == 128, "Invalid keypoint descriptor length in header (should be 128)."
                count = row[0]
                first = False
            if len(row) == 4:
                keypoints.append(np.array(row))
            if len(row) == 20:
                descriptor += row
            if len(row) == 8:
                descriptor += row
                assert len(descriptor) == 128, "Keypoint descriptor length invalid (should be 128)."
                #normalize the key to unit length
                descriptor = np.array(descriptor)
                descriptor = descriptor / math.sqrt(np.sum(np.power(descriptor,2)))
                descriptors.append(descriptor)
                descriptor = []
    assert len(keypoints) == count, "Incorrect total number of keypoints read."
    print "Number of keypoints read:", int(count)
    return [im,keypoints,descriptors]

def AppendImages(im1, im2):
    """Create a new image that appends two images side-by-side.

    The arguments, im1 and im2, are PIL images of type RGB
    """
    im1cols, im1rows = im1.size
    im2cols, im2rows = im2.size
    im3 = Image.new('RGB', (im1cols+im2cols, max(im1rows,im2rows)))
    im3.paste(im1,(0,0))
    im3.paste(im2,(im1cols,0))
    return im3

def DisplayMatches(im1, im2, matched_pairs):
    """Display matches on a new image with the two input images placed side by side.

    Arguments:
     im1           1st image (in PIL 'RGB' format)
     im2           2nd image (in PIL 'RGB' format)
     matched_pairs list of matching keypoints, im1 to im2

    Displays and returns a newly created image (in PIL 'RGB' format)
    """
    im3 = AppendImages(im1,im2)
    offset = im1.size[0]
    draw = ImageDraw.Draw(im3)
    for match in matched_pairs:
        draw.line((match[0][1], match[0][0], offset+match[1][1], match[1][0]),fill="red",width=2)
    im3.show()
    return im3

def RANSAC(matched_pairs):

    # generate random numbers for ransac
    randomNumbers = np.random.randint(0, high=len(matched_pairs), size=10000)

    orientationDifferenceDegrees = 1 # in degrees
    scaleDifference = 0.1 # in percentages

    all_subsets = []

    orientationDifferenceThreshold = orientationDifferenceDegrees*math.pi/180
    subset = []

    # find a consistent set of all elements with the random matched pair
    for i in randomNumbers:

        # orientation difference between random matched pair
        baseOrientationDifference = abs((matched_pairs[i][0][3] - matched_pairs[i][1][3]) % (math.pi * 2))

        # scale difference of the random matched pair
        baseScaleDifference = matched_pairs[i][1][2]/matched_pairs[i][0][2]

        # Find consistent set of all matched pairs for this specific random matched pair
        for j in range(len(matched_pairs)):

            # orientation difference of the current jth matched pair
            targetOrientationDifference = abs((matched_pairs[j][0][3] - matched_pairs[j][1][3]) % (math.pi * 2))

            # difference in orientations between random pair and the jth pair
            finalOrientationDifferenceBetweenKeypoints = abs(baseOrientationDifference - targetOrientationDifference)

            # difference in scale between two keypoints in the jth matched pair
            targetScaleDifference = matched_pairs[j][1][2]/matched_pairs[j][0][2]

            # if consistent then add to consistent set of the random matched pair
            if abs(finalOrientationDifferenceBetweenKeypoints <= orientationDifferenceThreshold) and (abs(baseScaleDifference - targetScaleDifference) <= scaleDifference*baseScaleDifference):
                subset.append(matched_pairs[j])

        # add the consistent set of a random pair i to the set of all consistent sets
        all_subsets.append(subset)


    # return the best consistent set that encompasses the most matched pairs
    return max(all_subsets, key=len)


def match(image1,image2, useRansac):
    """Input two images and their associated SIFT keypoints.
    Display lines connecting the first 5 keypoints from each image.
    Note: These 5 are not correct matches, just randomly chosen points.

    The arguments image1 and image2 are file names without file extensions.

    Returns the number of matches displayed.

    Example: match('scene','book')
    """
    im1, keypoints1, descriptors1 = ReadKeys(image1)
    im2, keypoints2, descriptors2 = ReadKeys(image2)

    # CODE STARTS HERE
    matched_pairs = [] 
    threshold = 0.5

    # iterate over every descriptor in the first image
    for i in range(len(descriptors1)):
        all_angles = []
        tempAngle = 0.0

        #iterate over every descriptor in the second image
        for j in range(len(descriptors2)):
            # find the angle between the two points
            tempAngle = math.acos(np.dot(descriptors1[i], descriptors2[j]))
            all_angles.append(tempAngle)

        # Sort the list
        sortedList = sorted(all_angles)

        # if ratio between smallest and second smallest is than a threshold then it is matched pair!
        if sortedList[0]/sortedList[1] < threshold:
            matched_pairs.append([keypoints1[i],keypoints2[all_angles.index(sortedList[0])]])

    # USE RANSAC
    if useRansac == 1:
        final_matches = RANSAC(matched_pairs)
        im4 = DisplayMatches(im1, im2, final_matches)
        return im4

    #
    # END OF SECTION OF CODE TO REPLACE
    #
    im3 = DisplayMatches(im1, im2, matched_pairs)
    return im3

#Test run...

# use 0 as 3rd input if you don't want to use ransac, use 1 for Ransac
match('scene','box', 0)

