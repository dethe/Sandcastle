# -*- coding: utf-8 -*-

from __future__ import with_statement
from string import Template
from StringIO import StringIO
import json

class AttributedFile(object):
    '''
    By giving a path to the config dict, it will open a file expecting to find lines of key: value pairs
    This will return a dict built from those pairs
    By adding text after an empty line a special text key will be created with the value of all of the remaining text
    The values may have placeholders interpolated from earlier values
    
    The title and body text do not interpolate values (it would cause problems if the text has a dollar sign, for one thing).
    '''
    def __init__(self, filepath=None, defaults=None, headers_only=False):
        self.attrs = defaults or {}
        self.title = None
        self.text = None
        self.filepath = filepath
        if defaults and hasattr(defaults, 'text'):
            self.text = defaults.text
        else:
            self.text = ''
        textmode = False
        titlemode = True
        text = None
        if not filepath: return
        with open(filepath) as sourcefile:
            for rawline in sourcefile:
                rawline = rawline.decode('utf-8')
                line = rawline.strip()
                if textmode:
                    # once we get into textmode, simply consume the rest of the file as text
                    text.write(rawline)
                    text.write(u'\n')
                elif line.startswith(u'%%'):
                    # it's a comment
                    pass
                elif line.startswith(u'#'):
                    # it's a key/value pair
                    titlemode = False
                    key,value = [s.strip() for s in line[1:].split(':', 1)] # trim off leading '#' and split on ':'
                    filled_value = Template(value).substitute(self.attrs)
                    try:
                        interpreted_value = json.loads(filled_value)
                    except ValueError:
                        interpreted_value = filled_value
                    self.attrs[key] = interpreted_value
                elif not line:
                    # empty lines are optional after the title and mandatory between key list and text
                    if headers_only and not titlemode: return
                    if not titlemode:
                        textmode = True # we've got all the header lines and are ready to start reading the text remaining
                        text = StringIO()
                elif titlemode:
                    # look for the optional title on first line
                    value = line
                    if value and not value.startswith(u'#'):
                        self.title = value
            if text:
                self.text = self.text +  text.getvalue()
                text.close()
                
    def __unicode__(self):
        text = StringIO()
        if self.title:
            text.write((u'%s\n\n' % self.title))
        for key in sorted(self.attrs.keys()):
            text.write((u'#%s: %s\n' % (key, self.attrs[key])))
        if self.text:
            text.write((u'\n%s' % self.text))
        return text.getvalue()
            
