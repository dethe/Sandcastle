# -*- coding: utf-8 -*-

from sandcastle.entry import Entry
from sandcastle.config import get_config
from sandcastle.template import Template
import simplejson
import os

config = get_config()

def entry_files():
    source = config['entry_source']
    for filename in [os.path.join(source, e) for e in os.listdir(source) if e.endswith('.txt')]:
        if os.path.isfile(filename):
            yield filename
            
def published_entries():
    for filename in entry_files():
        entry = Entry(filename)
        if entry.ispublished():
            yield entry
            
def sorted_published_entries():
    entries = [(entry.attrs['published'], entry) for entry in published_entries()]
    entries.sort()
    return [entry for (date, entry) in entries]

def generate_entry_list():
    return [(entry.title, entry.html_uri()) for entry in sorted_published_entries]
    
def print_entry_list():
    print simplejson.dumps(generate_entry_list(), sort_keys=True, indent=4)
    
def print_html_entries():
    for entry in sorted_published_entries():
        print entry.html()
        print "\n=====================================\n"
        
def update_entries():
    '''Add next and previous links to text format'''
    prev = None
    for entry in sorted_published_entries():
        if prev:
            entry['prev_link'] = prev.html_uri()
            entry['prev_title'] = prev.title
            prev.attrs['next_link'] = entry.html_uri()
            prev.attrs['next_title'] = entry.title
            prev.savetext()
            entry.savetext()
        prev = entry
        
def generate_atom_feed():
    '''Create a full feed of all entries for importing into WordPress'''
    feed_atom_template = Template('feed.atom')
    entries = sorted_published_entries()
    entries.reverse()
    print feed_atom_template.generate(entries=entries, config=config)
            
    
if __name__ == '__main__':
#    print_entry_list()
#    print_html_entries()
#    print published_entries().next().html()
#    print config['site_title']
#    update_entries()
    generate_atom_feed()
