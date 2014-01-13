import markdown

text = '''ok:
author: Dethe Elza
date: 22 February 2010

# Test of markdown extensions

## Fenced code blocks and code highlighting

~~~~{.python}
def fenced_code_block():
    return 'some code'
~~~~

## Abbreviations

*[ABBR]: Abbreviation

This paragraph has an ABBR in it.

## And of course, this tests the table of contents extension

'''

md = markdown.Markdown(extensions=['abbr', 'fenced_code', 'meta', 'headerid'], output_format='html')

code = md.convert(text)
print 'Meta:', md.Meta
print 'Code:', code
