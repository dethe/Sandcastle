from sandcastle.humanize import humanizeTimeDiff
from datetime import datetime
from sandcastle.util import writeToFile, titleToPermalink
from sandcastle.template import Template
from sandcastle.config import get_config
import os

config = get_config()
bookmarks_template = Template('pinboard.html')
twitter_template = Template('twitter.html')

def generateBookmarks():
    import feedparser
    feed = feedparser.parse(config['bookmarks_url'])
    filename = os.path.join(config['site_source_root'], 'widgets', 'bookmarks.html')
    writeToFile(filename, bookmarks_template.generate(entries=feed.entries))
    
def catchUpToToday():
    import datetime
    import time
    day = datetime.timedelta(1)
    date = datetime.date(2009, 6, 29)
    today = datetime.date.today()
    while date < today:
        bookmarksToEntry(date.isoformat())
        twitterToEntry(date.isoformat(), (date + day).isoformat())
        date += day
        time.sleep(60) # limit how fast we hit the servers
    # Save today as next startdate
    
def bookmarksToEntry(date):
    # Date should be ISO-8601: 2009-06-29
    # My pinboard bookmarks start on June 29, 2009
    feed = feedparser.parse(config['bookmarks_by_date_url'] + date)
    if feed.entries:
        filename = os.path.join(config['site_source_root'], 'entries', '%s_bookmarks.html' % date)
        writeToFile(filename, bookmarks_template.generate(entries=feed.entries))

def twitterToEntry(date, nextdate):
    # Date should be ISO-8601: 2008-08-26
    # My twitter start date is Aug 26, 2008
    url = 'http://search.twitter.com/search.atom?rpp=100&since=%s&until=%s'
    
def generateTwitterFeed():
    print 'staging Twitter widget'
    import feedparser
    import calendar
    statuses = feedparser.parse(config['twitter_posts_url']).entries
    favourites = feedparser.parse(config['twitter_favourites_url']).entries
    mentions = feedparser.parse(config['twitter_mentions_url']).entries
    for favourite in favourites:
        favourite.fave = True
    statuses.extend(favourites)
    statuses.extend(mentions)
    statuses.sort(key=lambda x: x.published, reverse=True)
    entries = []
    for e in statuses:
        entry = {
            'link': e.link, 
            'fave': getattr(e, 'fave', False),
            'time': since(e.published_parsed, e.published),
            'author_name': e.author_detail['name'],
            'author_link': None,
            'timestamp': e.published,
        }
        if 'href' in e.author_detail:
            entry['author_link'] = e.author_detail['href']
        entry['author_nick'], entry['content'] = e.title.split(':', 1)
        entry['content'] = twitparse(entry['content'])
        entries.append(entry)
    filename = os.path.join(config['site_source_root'], 'widgets', 'twitter.html')
    writeToFile(filename, twitter_template.generate(entries=entries))
            
def since(timestamp, published):
    ts = datetime(*timestamp[:6])
    return humanizeTimeDiff(ts)
    
def twitparse(text):
    # source: http://teebes.com/blog/17/simple-python-twitter-rss-feed-parser
    # parse links
    import re
    text = re.sub(
        r"[^\"](http://(\w|\.|/|\?|=|%|&)+)",
        lambda x: "<a href='%s'>%s</a>" % (x.group(), x.group()),
        text)
    
    # parse @tweeter
    text = re.sub(
        r'@(\w+)',
        lambda x: "<a href='http://twitter.com/%s'>%s</a>"\
             % (x.group()[1:], x.group()),
        text)
    
    # parse #hashtag
    text = re.sub(
        r'#(\w+)',
        lambda x: "<a href='http://twitter.com/search?q=%%23%s'>%s</a>"\
             % (x.group()[1:], x.group()),
        text)
    return text

