# -*- coding: utf-8 -*-

from simple_entry_list import published_entries
import simplejson

def generate():
    tag_to_html_entries = {}
    for entry in published_entries():
        print 'processing entry %s' % entry.title
        for tag in entry.tags():
            print 'setting tag %s' % tag
            tag_to_html_entries.setdefault(tag, []).append([entry.title, entry.html_uri()])
    print simplejson.dumps(tag_to_html_entries, sort_keys=True, indent=4)
    
if __name__ == '__main__': generate()
            
