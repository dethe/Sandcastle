# -*- coding: utf-8 -*-

import os
from bisect import bisect
from sandcastle.util import *
from sandcastle.entry import Entry
from sandcastle.template import Template
from sandcastle.config import get_config
from sandcastle import widgets

config = get_config()
tag_cloud_template = Template('tagcloud.html')
archive_widget_template = Template('archives.html')
page_template = Template('page.html')
recent_widget_template = Template('recent_posts.html')
projects_template = Template('projects.html')
feed_atom_template = Template('feed.atom')

VERBOSE = True

class EntryList(object):

    def __init__(self):
        self.directory = config['entry_source']
        filenames = list(self.textFiles(self.directory))
        self.tagmap = {}
        self.projects = [Entry(filename) for filename in self.textFiles(config['project_source'])]
        for project in self.projects:
            for tag, url in project.taglist():
                self.tagmap.setdefault(tag, []).append(project)
        self.entries = [Entry(filename) for filename in self.textFiles(config['entry_source'])]
        for entry in self.entries:
            for tag, url in entry.taglist():
                self.tagmap.setdefault(tag, []).append(entry)
        self.filteredlist = self.entries
        self.css = None
        self.js = None
        for filename in filenames:
            entry = self.link_prev_next(Entry(filename))
            
            
    def textFiles(self, directory):
        return [os.path.join(directory, filename) for filename in sorted(os.listdir(directory)) if filename.endswith('.txt')]
        
    def tags(self, largerThan=0):
        sortable = [(len(self.tagmap[key]), key) for key in self.tagmap if len(self.tagmap[key]) > largerThan]
        sortable.sort()
        sortable.reverse()
        return [key for count,key in sortable]
        
    def generateTagCloud(self):
        tagCloud =  tagsByWeight(self.tagmap, config, 1)
        if VERBOSE: print 'generateTagCloud() for %d tags' % len(self.tagmap)
        tagpath = os.path.join(config['site_source_root'], 'widgets', 'tagcloud.html')
        writeToFile(tagpath, tag_cloud_template.generate(tagCloud=tagCloud))

    def generateArchives(self):
        years = {}
        for entry in self.entriesForTag('*'):
            year = years.setdefault(entry.attrs['published'][:4], [])
            year.append(entry)
        if VERBOSE: print 'generateArchives() for %d years' % len(years)
        widget_path = os.path.join(config['site_source_root'], 'widgets', 'archives.html')
        writeToFile(widget_path, archive_widget_template.generate(years=years))
        # FIXME: give projects dates so they can show up here
        for year in years:
            path = os.path.join(config['site_source_root'], 'archives', year)
            writeToFile(path, page_template.generate(title='%s Archives' % year, entries=years[year], projects=[], type="Index"))
        
    
    def generateRecent(self):
        # FIXME: This should just return the last x in list that match
        if VERBOSE: print 'generateRecent() for last 10 posts'
        widget_path = os.path.join(config['site_source_root'], 'widgets', 'recent_posts.html')
        entries = [entry for entry in self.entries[-10:]]
        entries.reverse()
        writeToFile(widget_path, recent_widget_template.generate(entries=entries))
        
    def entriesForTag(self, tag):
        if tag is None or tag == 'Untagged':
            entries = [entry for entry in self.entries if not entry.taglist()]
        elif tag == '*':
            entries = self.entries
        else:
            entries = [entry for entry in self.tagmap[tag] if entry.attrs['type'] == 'Journal Post']
        return reversed(entries) # we always work on a list in reverse chronological order
        
    def projectsForTag(self, tag):
        if tag is None or tag == 'Untagged':
            projects = [project for project in self.projects if not project.taglist()]
        elif tag == '*':
            projects = self.projects
        else:
            projects = [project for project in self.tagmap[tag] if project.attrs['type'] == 'Project']
        return projects
        
    def recentlyModified(self, tag='*', startIndex=0, howMany=10):
        return list(self.entriesForTag(tag))    [:howMany]
                            
    def stageProjects(self):
        if VERBOSE: print 'stageProjects() for  %s projects' % len(self.projects)
        for entry in self.projects:
            entry.savehtml()
        project_index = os.path.join(config['site_source_root'], 'widgets', 'projects.html')
        writeToFile(project_index, projects_template.generate(entries=self.projects))
            
    def stageWidgets(self):
        self.generateTagCloud()
#        self.generateArchives()
        self.generateRecent()
        widgets.generateBookmarks()
        widgets.generateTwitterFeed()

    def stage_all(self):
        self.stageHtml()
        self.stageHtmlIndexes()
        self.stageAtomFeeds()
        self.stageProjects()
        self.generateArchives()
#        self.stageWidgets()
        
    def stage_entry(self):
        entry = self.entries[-1]     # We want to stage the latest entry
        previous = self.entries[-2]  # We need to update the previous entry's "next" links
        entry.savehtml()
        previous.savehtml()
        entry.savehtml(html_filename=os.path.join(config['site_source_root'],'index.html'))
        self.stageHtmlIndexes(entry.taglist())
        entry.saveatom()
        self.stageAtomFeeds(entry.taglist())
        return filesWritten()
        
    def stageHtml(self):
        for entry in self.entries:
            entry.savehtml()
        self.entries[-1].savehtml(
            html_filename=os.path.join(config['site_source_root'],
            'index.html')) # special handling for latest entry
        
    def stageHtmlIndexes(self, tags=None):
        if tags is None:
            tags = self.tags()
        # Create an index for each tag
        if VERBOSE: print 'stageHtmlIndexes() for %d tags' % len(tags)
        for tag in tags:
            writeToFile(
                htmlFilenameForTag(
                    config['publish_target'], tag),
                page_template.generate(
                    title=tag,
                    type='Index',
                    entries=self.entriesForTag(tag),
                    projects=self.projectsForTag(tag)))
        # Also save a page listing all entries 
        if VERBOSE: print 'stageHtmlIndexes() staging archive of all entries'
        writeToFile(
            os.path.join(
                config['entry_target'], 
                'index.html'),
            page_template.generate(
                title='Archive',
                type='Index',
                entries=self.entriesForTag('*'),
                projects=self.projects))
        # And a page listing all tags
        if VERBOSE: print 'stageHtmlIndexes() staging index of all tags'
        writeToFile(
            os.path.join(
                config['site_source_root'], 
                'tags', 
                'index.html'),
            page_template.generate(
                title='All Tags',
                type='Tag Index',
                allTags=tagsByWeight(
                    self.tagmap, config, 0)))
        
    def stageAtomFeeds(self, tags=None):
        if tags is None:
            tags = self.tags()
        # Create main index. FIXME: This should be followable to get all entries
        if VERBOSE: print 'stageAtomFeeds() staging atom index for recently modified files'
        # This block creates the atom feeds for the history of the site, linked forward and back
        paged_entries = list(pager(self.entries, 10))
        pages = len(paged_entries)
        for idx, entries in enumerate(paged_entries):
            if not idx:
                curr_url = 'index.atom'
                prev_url = None
            else:
                curr_url = 'index_%d.atom' % idx
                if idx > 1:
                    prev_url = 'index_%d.atom' % (idx - 1)
                else:
                    prev_url = 'index.atom'
            if idx < (pages - 1):
                next_url = 'index_%d.atom' % (idx + 1)
            else:
                next_url = None
            last_url = 'index_%d.atom' % (pages - 1)
            writeToFile(
                os.path.join(
                    config['site_source_root'], 
                    curr_url),
                feed_atom_template.generate(
                    render='xml',
                    curr_url=curr_url,
                    prev_url=prev_url,
                    next_url=next_url,
                    last_url=last_url,
                    tag=None, 
                    entries=entries))
        # Create index for each tag. FIXME: Should list projects as well
        if VERBOSE: print 'stageAtomFeeds() staging feeds for %d tags' % len(tags)
        for tag in tags:
            if not tag: continue
            entries = self.recentlyModified(tag)
            if not entries: continue # no entries, just projects
            writeToFile(
                atomFilenameForTag(
                    config['publish_target'], 
                    tag), 
                feed_atom_template.generate(
                    render='xml',
                    tag=tag, 
                    entries=entries,
                    curr_url = '/tags/%s/index.atom' % tag,
                    atom_uri=atomUriForTag(
                        config['publish_target'], 
                        tag)))
        # FIXME: Each project should have a feed for updates
            
    def link_prev_next(self, entry):
        if self.entries:
            prev = self.entries[-1]
            prev.attrs['next_link'], prev.attrs['next_title'] = entry.html_uri(), entry.title
            entry.attrs['prev_link'], entry.attrs['prev_title'] = prev.html_uri(), prev.title
        return entry
        


