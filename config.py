# -*- coding: utf-8 -*-

from os.path import join
import sandcastle
import keyring

def twpw():
    twitter_user = 'dethe'
    password = keyring.get_password('twitter_password', twitter_user)
    if not password:
        import getpass
        password = getpass.getpass('Twitter password for %s:\n', twitter_user)
        keyring.set_password('twitter_password', twitter_user, password)
    return twitter_user, password

def pbpw():
    pinboard_user = 'dethe'
    password = keyring.get_password('pinboard_password', pinboard_user)
    if not password:
        import getpass
        password = getpass.getpass('Pinboard password for %s:\n', pinboard_user)
        keyring.set_password('pinboard_password', pinboard_user, password)
    return pinboard_user, password


def set_config(base_uri, publish_target):
    '''
        base_uri is for http access
        publish_target is where the files are stored
    '''
    #
    # user config
    #
    user_name='Dethe Elza'
    user_email='kudzu@livingcode.org'
    user_uri=base_uri
    user_picture=join(user_uri, 'images', 'dethe_sm.png')
    user_description='My name is Dethe Elza. I\'m a programmer and writer in Vancouver, British Columbia, Canada.'
    #
    # Generator config
    #
    generator_name='Sandcastle'
    generator_url=join(base_uri, 'projects', 'sandcastle')
    generator_verbose=False
    site_source_root=publish_target
    generator_root=sandcastle.__path__[0]
    template_theme='thirteen'
    template_dir=join(generator_root, 'templates')
    template_source=join(template_dir, template_theme)
    entry_source=join(site_source_root, 'src', 'entries')
    entry_target=join(site_source_root, 'entries')
    tag_target=join(site_source_root, 'tags')
    project_source=join(site_source_root, 'src', 'projects')
    project_target=join(site_source_root, 'projects')
    # a time sufficiently in the past:
    epoch='1965-02-04T08:15:00Z'
    min_tag_weight=12
    max_tag_weight=20
    #
    # Site config
    #
    site_title='Living Code'
    site_tagline='A program is a process, not a thing'
    site_uri=base_uri
    site_icon=join(site_uri, 'favicon.ico')
    site_logo=join(site_uri, 'images', 'dethe_sm.png')
    site_description='This is my site for talking about code, kids, and other things that grow, like gardens, bread, and deficits.'
    site_publish_entries=join(publish_target, 'entries')
    #
    # Associated site info
    #
    # bookmarks_url='http://feeds.pinboard.in/rss/u:dethe'
    # bookmarks_by_date_url='https://%s:%s@api.del.icio.us/v1/posts/get?dt=' % pbpw()
    # twitter_posts_url='http://%s:%s@api.twitter.com/1/statuses/user_timeline.atom?count=5' % twpw()
    # twitter_favourites_url='http://%s:%s@api.twitter.com/1/favorites.atom?count=5' % twpw()
    # twitter_mentions_url = 'http://%s:%s@api.twitter.com/1/statuses/mentions.atom?count=5' % twpw()
    cfg = locals()
    global _config
    _config = cfg
        
def get_config():
    return _config