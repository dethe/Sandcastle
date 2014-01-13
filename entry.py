# -*- coding: utf-8 -*-

from __future__ import with_statement
import os, sys
from datetime import date
from uuid import uuid4 as uuid
from markdown import Markdown
from sandcastle.config import get_config
from sandcastle.template import Template
from sandcastle.util import *
from sandcastle.attributedfile import AttributedFile

config = get_config()
entry_template = Template('entry.html')
page_template = Template('page.html')
entry_atom_template = Template('entry.atom')

md = Markdown(extensions=['abbr', 'fenced_code', 'meta', 'headerid'], output_format='html')
def markdown(text):
    output = md.convert(text)
    return output, md.Meta

class Entry(AttributedFile):

    def __init__(self, filepath=None):
        AttributedFile.__init__(self, filepath)
        self.isDirty = False
        self.attrs.setdefault(u'published', '')
        self.attrs[u'published'] = self.attrs[u'published'][:10]
        self.attrs.setdefault(u'type', 'Journal Post')
        self.attrs.setdefault(u'uuid', uuid())
        self.attrs.setdefault(u'prev_link', '')
        self.attrs.setdefault(u'prev_title', '')
        self.attrs.setdefault(u'next_link', '')
        self.attrs.setdefault(u'next_title', '')
        self.attrs.setdefault(u'prev_link',  '')
        self.attrs.setdefault(u'prev_title', '')
        self.attrs.setdefault(u'next_link', '')
        self.attrs.setdefault(u'next_title', '')
        self.attrs.setdefault(u'tags', '')
        if not filepath:
            self.isDirty = True
        else:
            self.isDirty = False
            
    def savedirectory(self):
        if self.attrs['type'] == 'Journal Post':
            base_path = config['entry_target']
        elif self.attrs['type'] == 'Project':
            base_path = config['project_target']
        else:
            raise KeyError('Unrecognized file type')
        return os.path.join(base_path, self.basename())
            
    def basename(self):
        ''' file name without path or extension '''
        filename = os.path.basename(self.filepath)
        return os.path.splitext(filename)[0]

    def savebasepath(self):
        ''' full path without file extension '''
        return os.path.join(self.savedirectory(), self.basename())
        
    def permalink(self):
        '''filename without file extension'''
        return os.path.split(self.savebasepath())[-1]        
    def rights(self):
        return 'Copyright %s %s' % (self.attrs['published'][:4], config['user_name'])
        
    def taglist(self):
        return [(tag, htmlUriForTag(config['site_uri'], tag)) for tag in self.tagsplit(self.attrs['tags'])]
               
    def tagsplit(self, tagstring):
        taglist = list(set([x.strip() for x in tagstring.split(',')]))
        taglist.sort()
        return taglist

    def text_filename(self):
        # FIXME: use the util.newFilename() routine instead of this code
        date_part = self.attrs['published']
        def permalinkToPath(link, collisionFix=''):
            return '%s/%s_%s%s.txt' % (config['entry_source'], date_part, self.permalink(), collisionfix)
        if not self.title:
            raise AttributeError('Cannot save Entry without a title')
        if not self.permalink():
            trial_permalink = titleToPermalink(self.title)
            self.filepath = permalinkToPath(trial_permalink)
            collisionFix = 0
            while os.path.exists(self.filepath):
                collisionFix += 1
                self.filepath = permalinkToPath(trial_permalink, collisionFix)
        return self.filepath

    def html_filename(self):
        return os.path.join(self.savedirectory(), 'index.html')
        
    def html_uri(self, entrytype=None):
        if entrytype is None:
            entrytype = {'Journal Post': 'entries',
                         'Project': 'projects'}[self.attrs['type']]
        return os.path.join(config['site_uri'], entrytype, self.permalink())
                
    def parsedcontent(self):
        output, meta = markdown(self.text)
        self.meta = meta
        return output
        
    def content(self):
        return entry_template.generate(entry=self, postprocess=False)
        
    def html(self):
        from genshi.template.eval import UndefinedError
        try:
            return page_template.generate(render='xhtml', entry=self, content=self.content(), title=self.title, type='Entry')
        except UndefinedError:
            print 'Error generating %s (template %s), apparently missing a key in %s' % (self.title, 'page.html', self.attrs.keys())
            raise
         
    def atom(self):
        return entry_atom_template.generate(entry=self)
        
    def savehtml(self, html_filename=None):
        if not os.path.exists(self.savedirectory()):
            os.makedirs(self.savedirectory())
        elif not os.path.isdir(self.savedirectory()):
            raise RuntimeError('Path to save file is not a directory')
        if not html_filename:
            html_filename = self.html_filename()
        # print 'saving to %s' % html_filename
        with open(html_filename, 'w') as savefile:
            print >> savefile, self.html().encode('utf-8')
        
    def __getattr__(self, key):
        return self.attrs[key]

