#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Utilities for generating Web 2.0 graphics using Quartz and CoreImage

Implemented: 

image [width] [height] => creates a new, blank svg image with the appropriate size
picture [filename] => creates a new svg image based on an existing picture file
rounded [radius] => rounds the corners using clipping
gradient [topcolor] [lowercolor] => create and apply a horizontal gradient to image
color [color] => fill image with color
output [filename] => where to put the results

Not yet implemented:

resize_absolute [width] [height] => scale it
resize_relative [percent] => scale it
border [size] [color] => make a border
polaroid [text] => make a white non-uniform border with caption
button [cornerradius] [directoryname] => slice image for sliding doors and create example HTML
'''

from CoreGraphics import *

def hexfloat(hh):
    '''Converts a two-digit hex string to a float between 0.0 and 1.0, inclusive'''
    return float(int(hh, 16)) / float(int('FF', 16))

def hexcolor(h):
    '''Converts a string of the form #RRGGBB to an NSColor'''
    r,g,b = [hexfloat(x) for x in (h[1:3], h[3:5], h[5:7])]
    return r,g,b,1.0
    #return NSColor.colorWithCalibratedRed_green_blue_alpha_(r,g,b,1.0)

class WebImage(object):
    
    def __init__(self, canvas=None, image=None):
        self.canvas = canvas
        self.gradient = None
        self.image = image
        self.color = None
        self.clip = NSBezierPath.bezierPathWithRect_(self.rect())
        
    def size(self):
        return self.canvas.size()
        
    def rect(self):
        return (0,0), self.canvas.size()
                
    def evaluateToFile_(self, filename):
        self.canvas.lockFocus()
        if self.clip:
            self.clip.setClip()
        if self.image:
            self.image.compositeToPoint_operation_((0,0), NSCompositeCopy)
        elif self.gradient:
            self.gradient.drawInBezierPath_angle_(self.clip, -90)
        elif self.color:
            self.clip.fill(self.color)
        self.canvas.unlockFocus()
        image_data = self.canvas.TIFFRepresentation()
        image_rep = NSBitmapImageRep.imageRepWithData_(image_data)
        data = image_rep.representationUsingType_properties_(NSPNGFileType, None)
        data.writeToFile_atomically_(filename, False)
        

def image(width, height):
    return WebImage(canvas=NSImage.alloc().initWithSize_((width, height)))
    
def picture(filename):
    import os
    filepath = os.path.abspath(filename)
    image = NSImage.alloc().initWithContentsOfFile_(filepath)
    canvas = NSImage.alloc().initWithSize_(image.size())
    return WebImage(canvas=canvas, image=image)
    
def gradient(img, topcolor, bottomcolor):
    img.gradient = NSGradient.alloc().initWithStartingColor_endingColor_(hexcolor(topcolor), hexcolor(bottomcolor))
    return img
    
def rounded(img, radius):
    img.clip = NSBezierPath.bezierPath()
    img.clip.appendBezierPathWithRoundedRect_xRadius_yRadius_(img.rect(), radius, radius)
    return img
    
def color(img, color):
    img.color = hexcolor(color)
    return img
    
def output(img, filename):
    img.evaluateToFile_(filename)
    return img
    
if __name__ == '__main__':
    print output(rounded(gradient(image(100, 100), '#FF0000', '#00FF00'), 25),'gradient.png')
