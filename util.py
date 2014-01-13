# -*- coding: utf-8 -*-

from config import get_config
import os, sys
import subprocess
from datetime import date

def pager(seq, size):
    start = 0
    last = size
    while last < len(seq):
        yield seq[start:last]
        start = last
        last += size
    yield seq[start:]

def uridata(uri):
    from httplib2 import Http
    conn = Http()
    response, content = conn.request(uri)
    return content

def filedata(filename):
    f = open(filename)
    data = f.read()
    f.close()
    return data

def titleToPermalink(title):
    temp = '_'.join(title.lower().split())
    return ''.join([x for x in temp if x.isalnum() or x == '_'])
    
def newFilename(trial_directory='', trial_filename='index.html', dated=False):
    if trial_directory:
        directory = os.path.join(config['publish_target'], directory)
    else:
        directory = config['publish_target']
    if dated:
        directory = os.path.join(directory, date.today().isoformat())
    if not os.path.exists(directory):
        os.makedirs(directory)
    trial_basename, extension = os.path.splitext(trial_filename)
    trial_path = os.path.join(directory, trial_filename)
    collisionFix = 0
    while os.path.exists(trial_path):
        collisionFix += 1
        trial_path = os.path.join(directory, '%s_%d.%s' % (trial_basename, collisionFix, extension))
    return trial_path
    
def uriForFile(filepath):
    # remove config['publish_target'], add in config['site_uri']
    return filepath.replace(config['publish_target'], config['site_uri'])

def atomUriForTag(base_uri, tag):
    return base_uri + 'tags/' + titleToPermalink(tag)
    
def atomFilenameForTag(base_uri, tag):
    return base_uri + 'tags/' + titleToPermalink(tag) + '/index.atom'
        
def writeToFile(filename, data):
    if not data:
        print >> sys.stderr, 'Error writing file, no data for %s' % filename
    if os.path.exists(filename):
        os.rename(filename, '%s.bak' % filename) # backup old file first
    else: # make sure all directories exist
        path = os.path.dirname(filename)
        if not os.path.exists(path):
            os.makedirs(path)
    openfile = open(filename, 'w')
    print >> openfile, data.encode('utf-8')
    openfile.close()
   # _filesWritten.append(filename)
    
def tag_weights(config=None):
    return range(config['min_tag_weight'], config['max_tag_weight'] + 1)

def ordinalsForTagmap(tagmap, largerThan=0):
    def ord(tag):
        return len(tagmap[tag])
    ordinals = [ord(tag) for tag in tagmap if ord(tag) > largerThan]
    ordinals = list(set(ordinals))
    ordinals.sort()
    return ordinals

def relWeights(numberOfOrdinals, config):
    ordinalsPerWeight, minWeights = divmod(numberOfOrdinals, len(tag_weights(config)))
    if ordinalsPerWeight < 1:
        ordinalsPerWeight = 1
        minWeights = 0
    rel_weights = [config['min_tag_weight']] * minWeights + tag_weights(config) * ordinalsPerWeight
    rel_weights.sort()
    return rel_weights

def tagsByWeight(tagmap, config, largerThan=0):
    ordinals = ordinalsForTagmap(tagmap, largerThan)
    rel_weights = relWeights(len(ordinals), config)
    weight_map = dict(zip(ordinals, rel_weights))
    def ord(tag):
        return len(tagmap[tag])
    # return tag,uri,weight tuples    
    tagtuples = [(tag, htmlUriForTag(config['site_uri'], tag), atomUriForTag(config['site_uri'], tag), weight_map[ord(tag)], ord(tag)) for tag in tagmap if ord(tag) > largerThan]
    tagtuples.sort()
    return tagtuples
    
def htmlUriForTag(base_uri, tag):
    return base_uri + 'tags/' + titleToPermalink(tag)
    
def htmlFilenameForTag(base_path, tag):
    return base_path + 'tags/' + titleToPermalink(tag) + '/index.html'

