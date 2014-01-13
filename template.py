# -*- coding: utf-8 -*-

from genshi.template import TemplateLoader, MarkupTemplate
from lxml import etree
from StringIO import StringIO
from sandcastle.config import get_config

config = get_config()

class Template(object):
    def __init__(self, filename):
        # print 'trying to load %s from %s' % (filename, config['template_source'])
        loader = TemplateLoader(config['template_source'])
        self.template = loader.load(filename, cls=MarkupTemplate)
    def generate(self, postprocess=True, render='html', **kws):
        
        html = self.template.generate(config=config, **kws).render(render, encoding=None)
        if postprocess:
            try:
                return self.postprocess(html)
            except Exception:
                import sys
                with open('/tmp/bad_template.html', 'w') as output:
                    output.write(html.encode('utf-8'))
                sys.stderr.write('Wrote template output to /tmp/bad_template.html\n')
                raise
        else:
            return html
    def postprocess(self, html):
        '''Move link tags to the head and (most) script tags to the bottom'''
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(html.encode('utf-8')), parser)
        head = tree.find('head')
        body = tree.find('body')
        if head is None or body is None:
            return html
        # Move all scripts to page bottom
        # Move all CSS to page top
        scripts = body.findall('.//script')
        links = body.findall('.//link')
        # print 'postprocessing %s with %d scripts and %d links' % (tree.getroot().tag, len(scripts), len(links))
        body.extend(scripts)
        head.extend(links)
        return u'<!DOCTYPE html>' + etree.tostring(tree.getroot(), pretty_print=True, method='html').decode('utf-8')
        
    

