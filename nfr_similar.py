# -*- coding: utf-8 -*-

# http://stackoverflow.com/a/17388505
from difflib import SequenceMatcher

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def hamming_distance(s1, s2):
    #Return the Hamming distance between equal-length sequences
    if len(s1) != len(s2):
        raise ValueError("Undefined for sequences of unequal length")
    return sum(ch1 != ch2 for ch1, ch2 in zip(s1, s2))
similar2 = hamming_distance

from PIL import Image
def Ximhash(filepath): # http://blog.safaribooksonline.com/2013/11/26/image-hashing-with-python/
    try:
        im = Image.open(filepath)
        im = im.resize((8, 8), Image.ANTIALIAS) # Reduce it’s size.
        im = im.convert('L') # Convert it to grayscale.
        # Next we find the average pixel value of the image:
        pixels = list(im.getdata())
        avg = sum(pixels) / len(pixels)
        bits = ''.join(map(lambda pixel: '1' if pixel < avg else '0', pixels)) # '00010100...'
        hexadecimal = int(bits, 2).__format__('016x').upper()
    except:
        return None # 'unphashable'
    return hexadecimal

def supported_image_ext(extension):
    #while extension and extension[0] == '.':
    #    extension = extension[1:]
    return extension.strip('.') in ('bmp','dib','dcx','eps','ps','gif','im','jpg','jpe','jpeg','pcd','pcx','pdf','png','pbm','pgm','ppm','tif','tiff','xbm','xpm','psd') # psd

import os
def imhashable(filepath):
    if not supported_image_ext(os.path.splitext(filepath)[1]):
        return False
    if not os.path.isfile(filepath):
        return False
    return True

#from blockhash import blockhash # http://blockhash.io/
import blockhash
def imhash(filepath, bits=8):
    try:
        im = Image.open(filepath)
        im = im.resize((bits**2, bits**2), Image.ANTIALIAS) # Reduce it’s size.

        # convert indexed/grayscale images to RGB
        if im.mode == '1' or im.mode == 'L' or im.mode == 'P':
            im = im.convert('RGB')
        elif im.mode == 'LA':
            im = im.convert('RGBA')

        return blockhash.blockhash(im, bits)
    except:
        return None
        
def imhash_im_object(im, bits=8):
    try:
        #im = Image.open(filepath)
        im = im.resize((bits**2, bits**2), Image.ANTIALIAS) # Reduce it’s size.

        # convert indexed/grayscale images to RGB
        if im.mode == '1' or im.mode == 'L' or im.mode == 'P':
            im = im.convert('RGB')
        elif im.mode == 'LA':
            im = im.convert('RGBA')

        return blockhash.blockhash(im, bits)
    except:
        return None

# https://pypi.python.org/pypi/ImageHash
# http://www.pybytes.com/pywavelets/
# https://fullstackml.com/2016/07/02/wavelet-image-hash-in-python/
        
# http://stackoverflow.com/a/902779
#import imghdr
#def determine_image_type(filepath):
#    return imghdr.what(filepath)
#determine_image_type = imghdr.what