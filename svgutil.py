# -*- coding: utf-8 -*-

'''
Utilities for generating Web 2.0 graphics using SVG and ImageMagick

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

from xml.etree import ElementTree as etree
from string import Template

def _parse(svg):
    return etree.fromstring(svg)
    
def _string(svg):
    return etree.tostring(svg, 'utf-8')

def image(width, height):
    template = '''<?xml version="1.0" encoding="utf-8" ?>
    <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 20010904//EN"
        "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd">
    <svg xmlns="http://www.w3.org/2000/svg"
         xmlns:xlink="http://www.w3.org/1999/xlink" xml:space="preserve"
         width="${width}px" height="${height}px"
         viewBox="0 0 ${width} ${height}"
         zoomAndPan="disable" >
        <defs>
        </defs>
        <g>
        </g>
    </svg>'''
    return _parse(Template(template).substitute(width=width, height=height))
    
def picture(filename):
    # requires PIL
    import os, Image
    filepath = os.path.abspath(filename)
    temp = Image.open(filepath)
    width, height = temp.size
    svg = image(width, height)
    g = svg.find('{http://www.w3.org/2000/svg}g')
    im = etree.SubElement(g, '{http://www.w3.org/2000/svg}image', {'width': str(width), 'height': str(height), '{http://www.w3.org/1999/xlink}href': 'file:///' + filepath})
    return svg
    
def gradient(svg, color1, color2):
    '''A horizontal linear gradient'''
    defs = svg.find('{http://www.w3.org/2000/svg}defs')
    grad = etree.SubElement(defs, '{http://www.w3.org/2000/svg}linearGradient', {'x2': '0%', 'y2': '100%'})
    grad.set('id', 'gradient')
    grad.set('spreadMethod', 'pad')
    etree.SubElement(grad, '{http://www.w3.org/2000/svg}stop', {'offset': '0', 'stop-color': color1})
    etree.SubElement(grad, '{http://www.w3.org/2000/svg}stop', {'offset': '1', 'stop-color': color2})
    g = svg.find('{http://www.w3.org/2000/svg}g')
    rect = etree.SubElement(g, '{http://www.w3.org/2000/svg}rect', {'x': '0', 'y': '0', 'width': '100%', 'height': '100%', 'fill': 'url(#gradient)'})
    return svg
    
def color(svg, color):
    '''Apply a color as a fill to the image'''
    g = svg.find('{http://www.w3.org/2000/svg}g')
    etree.SubElement(g, '{http://www.w3.org/2000/svg}rect', {'x': '0', 'y': '0', 'width': '100%', 'height': '100%', 'fill': color})
    return svg
    
def rounded(svg, radius):
    defs = svg.find('{http://www.w3.org/2000/svg}defs')
    clip = etree.SubElement(defs, '{http://www.w3.org/2000/svg}clipPath', {'id': 'clippingrect'})
    etree.SubElement(clip, '{http://www.w3.org/2000/svg}rect', {'x': '0', 'y': '0', 'width': '100%', 'height': '100%', 'rx': str(radius), 'ry': str(radius)})
    g = svg.find('{http://www.w3.org/2000/svg}g')
    g.set('clip-path', 'url(#clippingrect)')
    return svg
    
def output(svg, filename):
    import Image
    from StringIO import StringIO
    pseudofile = StringIO(_string(svg))
    im = Image.open(pseudofile)
    im.save(filename)
    return svg
        
if __name__ == '__main__':
    print _string(output(rounded(gradient(image(100, 100), '#FF0000', '#00FF00'), 25),'gradient.png'))
    
    
    
    