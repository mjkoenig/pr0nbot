#!/usr/bin/env python

"""pr0nbot.py
Spidering robot for pr0n."""

__author__  = "Fabio FZero"
__version__ = "1.0.1 SVN"
__date__    = "Mar 20, 2007"

#===============================================================================
# Changes from 1.0:
# 
# - Merged checkconfig() and getconfig() - 
# Now getconfig does everything (much nicer).
# 
# - Renamed default_ignore to default_config. Maybe we'll put 
# something else besides the ignore list in the config file 
# in the future.
#
# - Replaced cPickle with pickle. We are not working with
# massive amounts of data anyway, so we can stick with the
# Python version. Maybe this will make it work on Mac (or
# even Jython, who knows).
#
# - getpr0n() is now ALWAYS called with aggro=True for image downloads, 
# even with regular spidering. 
#===============================================================================

import urllib2
import socket
import re
import time
import os
import sys
import getopt
import pickle
from urlparse import *


# Configuration and default values:

# Timeout for all connections, in seconds
timeout = 30
socket.setdefaulttimeout(timeout)

# Default dir for the dump
defaultdir = "pr0n"

# Default minimum size for file download
defaultminsize = 25

# Default ignore file contents
default_config = \
"""# This is the pr0nbot ignore list.
# 
# Write here any strings that should make pr0nbot ignore an URL.
# All lines beginning with '#' will be treated like comments. Blank
# lines can also be added to improve legibility. All strings should
# be lowercase (write "ignore" instead of "Ignore" or "IGNORE").
#
# One string per line ONLY. No regex or funny stuff here, just plain
# text.
#
# TIP: By default, pr0nbot is sexually neutral. This means it will
# download ALL KINDS OF PORN, including gay, lesbian, transexual,
# bestiality and whatever the fuck it finds along the way. If you want
# to avoid such things, uncomment some of the lines below. This will NOT
# guarantee that you will avoid ALL gay/tranny/lesbian/whatever porn (not 
# all websites name their content acconrdingly), but should keep it
# to a minimum.

# Porn categories
#gay
#lesbian
#bestiality
#beast
#animal
#tranny
#transexual
#anal
#oral
#creampie
#snuff
#fat
#chubby
#skinny
#anorexic
#thin
#ugly
#goldenshower
#pee
#peeing
#poop
#shit
#bisexual
#amateur
#camwhore

# Search engines, portals, nanny filters,
# redirectors, file hosting, hit counters, stores,
# ads etc.
google.com
yahoo.com
excite.com
altavista.com
aol.com
cybernanny.com
lycos.com
webcrawler.com
msn.com
hotbot.com
fucking-cash.com
webmaster
rapidshare
yousendit
imagevenue.com
texaslonghorn
imagesocket.com
submitter.com
trafficholder.com
trafficadept.com
netnanny.com
refer.ccbill.com
solidoak.com
surfwatch.com
cyberpatrol.com
icra.org
fosi.org
rtalabel.org
statcounter.com
youtube.com
orkut.com
flickr.com
globo.com
mozdev.org
hidebehind.com
sitemeter
fleshlight.com
fleshlightcash.com
/ad/
/ads/
portaldafamilia.org
buscape.com.br
lojadoprazer.com.br
bondfaro.com.br

# Protocols
javascript:
mailto:
rtsp:
mms:

# File types
.exe
.torrent
.swf
.mp3

# Top level domains
.gov.br
.gov
.mil.br
.edu

# Assorted fishy URL bits
header
member
membro
menu
button
botao
logo
rodape
footer
banner
lateral
shop
bemvindo
enquete
tabela
sendspace
publicidade
anuncio
template
title
jogo
game
biblia
jesus
oracao
bible
jeova
jehovah
mp3
music
musik
welcome
bem-vindo
bienvenido
"""


# stderr/stdout silencer
class NullWrite:
    def write(self, *s): pass


def getconfig(filename):
    """
    1. Checks if the config file exists.
    2. If not, creates it with the content in default_config.
    3. Reads the config file and returns it.
    
    Returns False in case of errors.
    """
    
    global default_config

    if os.path.exists(filename):
        configfile = open(filename, "r")
    else:
        try:
            f = open(filename, 'w')
            f.write(default_config)
            f.close()
            configfile = open(filename, "r")
        except IOError:
            return False

    ret = []

    for line in configfile:
        line = line.strip()
        if not line or line[0] == '#':
            continue
        else:
            ret.append(line)
            
    configfile.close()
    return ret


def unique(s):
    """
    Return a list of the elements in s, but without duplicates.

    For example, unique([1,2,3,1,2,3]) is some permutation of [1,2,3],
    unique("abcabc") some permutation of ["a", "b", "c"], and
    unique(([1, 2], [2, 3], [1, 2])) some permutation of
    [[2, 3], [1, 2]].

    For best speed, all sequence elements should be hashable.  Then
    unique() will usually work in linear time.

    If not possible, the sequence elements should enjoy a total
    ordering, and if list(s).sort() doesn't raise TypeError it's
    assumed that they do enjoy a total ordering.  Then unique() will
    usually work in O(N*log2(N)) time.

    If that's not possible either, the sequence elements must support
    equality-testing.  Then unique() will usually work in quadratic
    time.

    unique.py found at:
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52560
    """

    n = len(s)
    if n == 0:
        return []

    # Try using a dict first, as that's the fastest and will usually
    # work.  If it doesn't work, it will usually fail quickly, so it
    # usually doesn't cost much to *try* it.  It requires that all the
    # sequence elements be hashable, and support equality comparison.
    u = {}
    try:
        for x in s:
            u[x] = 1
    except TypeError:
        del u  # move on to the next method
    else:
        return u.keys()

    # We can't hash all the elements.  Second fastest is to sort,
    # which brings the equal elements together; then duplicates are
    # easy to weed out in a single pass.
    # NOTE:  Python's list.sort() was designed to be efficient in the
    # presence of many duplicate elements.  This isn't true of all
    # sort functions in all languages or libraries, so this approach
    # is more effective in Python than it may be elsewhere.
    try:
        t = list(s)
        t.sort()
    except TypeError:
        del t  # move on to the next method
    else:
        assert n > 0
        last = t[0]
        lasti = i = 1
        while i < n:
            if t[i] != last:
                t[lasti] = last = t[i]
                lasti += 1
            i += 1
        return t[:lasti]

    # Brute force is all that's left.
    u = []
    for x in s:
        if x not in u:
            u.append(x)
    return u


def crawl(url, ignorelist=[], aggro=False):
    """
    Spiders a given URL dodging everything on ignorelist
    and returns a dictionary:

    dict['links'] = list of links to other pages
    dict['pics'] = list of links to .jpg files
    dict['movies'] = list of links to video files
    
    If aggro is True, img tags are scanned too.
    
    Returns False in case of errors.
    """

    # Let's pretend we're Firefox
    headers = { 'User-Agent' :
                "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.2) " \
                "Gecko/20070225 Firefox/2.0.0.2" }
    findlinks  = r'<a href=".*?">'
    findimgs   = r'src=".*?\.jpg"'
    findframes = r'<frame .*?src=".*?">'
    moviexts   = ('avi', 'mpg', 'wmv', 'mov')
    
    # I know, I could have used htmllib to parse the html,
    # but I made some tests and discovered that my quick, 
    # dirty and procedural approach using the re module 
    # is MUCH faster and needs considerably less code.
    # Makes you think, doesn't it? - FZero

    try:
        req      = urllib2.Request(url, None, headers)
        socket   = urllib2.urlopen(req)
        mimetype = socket.info().gettype()
        html     = socket.read()
    except (urllib2.HTTPError, urllib2.URLError, IOError):
        return False
    
    if not "text" in mimetype:
        return False

    ret = { 'links'  : [],
            'pics'   : [],
            'movies' : [] }
    
    if url.count('/') > 2:
        baseurl = re.findall(r'.*/', url)[0]
    else:
        baseurl = url + '/'

    # In the lines below: urlparse(...)[0] returns the "http"
    # part of the url. If it's present, we have an absolute url.
    # Otherwise, it's a relative url and we have to splice the baseurl
    # using urljoin().

    frames = re.findall(findframes, html, re.MULTILINE|re.IGNORECASE)
    
    if frames:
        for frame in frames:
            prefix = ''
            l = re.findall('src=".*?"',
                           frame, re.IGNORECASE)[0].split('"')[1] # woo-hoo!
            if not urlparse(l)[0]:
                prefix = baseurl
            ret['links'].append(urljoin(prefix, l))

        ret['links'] = unique(ret['links'])
        return ret

    links = re.findall(findlinks, html, re.MULTILINE|re.IGNORECASE)
    
    for link in links:
    
        # Is the link in the ignorelist?
        if ignorelist:
            ignore = False
            for item in ignorelist:
                if item in link.lower():
                    ignore = True
                    break
            if ignore: continue
    
        link = link.split('"')[1]

        # Cut the intermediaries: if there's more than one
        # "http://" in the url, get only the LAST one. This
        # avoids most redirection mechanisms.
        if link.count("http://") > 1:
            link = 'http://' + link.split('http://')[-1]
        
        # Is it an image?
        if re.search('\.jpg$', link, re.IGNORECASE):
            prefix = ''
            if not urlparse(link)[0]:
                prefix = baseurl
            ret['pics'].append(urljoin(prefix, link))
            continue
        
        # Is it a movie?
        ismovie = False
        for ext in moviexts:
            if re.search('\.%s$' % ext, link, re.IGNORECASE):
                ismovie = True
                prefix = ''
                if not urlparse(link)[0]:
                    prefix = baseurl
                    ret['movies'].append(urljoin(prefix, link))
                break
        if ismovie: continue
        
        # If it's not denied, a pic or a movie, then it's a link!
        prefix = ''
        if not urlparse(link)[0]: prefix = baseurl
        ret['links'].append(urljoin(prefix, link))


    if aggro:
        # If we're aggro, we look into <img> tags too.
        imgs = re.findall(findimgs, html, re.MULTILINE|re.IGNORECASE)
        if imgs:
            for img in imgs:
                # Is the image in the ignorelist?
                if ignorelist:
                    ignore = False
                    for item in ignorelist:
                        if item in img.lower():
                            ignore = True
                            break
                    if ignore: continue
                prefix = ''
                i = img.split('"')[1]
                if not urlparse(i)[0]:
                    prefix = baseurl
                ret['pics'].append(urljoin(prefix, i))
 

    # Eliminates duplicate entries before returning the values
    ret['links'] = unique(ret['links'])
    ret['pics'] = unique(ret['pics'])
    ret['movies'] = unique(ret['movies'])
    ret['pics'].sort()
    ret['movies'].sort()

    return ret


def getpr0n(url, minsize=0, aggro=False):
    """
    Downloads a pr0n url to a file following the format:

    server_name-time_as_unix_epoch-filename_from_url
    
    The file must be bigger than minsize to be downloaded.

    If aggro is true, getpr0n tries to follow simple
    redirections to get "disguised" files.
    
    Returns True if everything's gone smooth or False
    if the file wasn't downloaded for any reason.
    """
    
    # Yep, we're still Firefox!
    # I wonder if this script will inflate the statistics
    # if it gets too popular...
    headers = { 'User-Agent' :
                "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.2) " \
                "Gecko/20070225 Firefox/2.0.0.2" }

    try:
        req    = urllib2.Request(url, None, headers)
        socket = urllib2.urlopen(req)
    except (urllib2.HTTPError, urllib2.URLError, IOError):
        return False
    
    # Aggro processing of html disguised as .jpg
    if "text" in socket.info().gettype():
        if aggro:
            # If we have a .jpg url inside a text/html wrapper,
            # we can try a little harder. Some sites
            # do this to avoid spidering, hehehe.
            if re.search('\.jpg$', url, re.IGNORECASE):
                html = socket.read()
                socket.close()
                # Gotta check if it really is html
                if "<html>" in html.lower():
                    f = url.split('/')[-1]
                    to_find = 'src=".*?\/%s"' % f
                    s = re.findall(to_find, html, re.IGNORECASE)
                    if s:
                        src = s[0].split('"')[1]
                    else:
                        # Let's not waste time. If we can't find the
                        # original file name, we were probably
                        # redirected to another gallery or a sign-in page.
                        return False
                    # Now we open a new socket with the right URL
                    try:
                        if not urlparse(src)[0]:
                            baseurl = re.findall(r'.*/', url)[0]
                            src = urljoin(baseurl, src)
                        print "-> %s" % src
                        req    = urllib2.Request(src, None, headers)
                        socket = urllib2.urlopen(req)
                    except (urllib2.HTTPError, urllib2.URLError, IOError):
                        return False
                else:
                    # If it's more complicated than that, we give up...
                    return False
        else:
            # Not aggro? Don't bother then.
            return False

    # File too short? It's HTML or a placeholder. Ignore it.
    # "Too short" is anything < minsize.
    if 'content-length' in socket.info().dict:
        if int(socket.info().dict['content-length']) < (minsize * 1024):
            return False
    
    f = url.split('/')[-1]
    filename = "%s-%s-%s" % (url.split('/')[2],
                             ('%.2f' % time.time()).replace('.', ''), f)
    
    try:
        the_file = open(filename,'wb')
    except IOError:
        return False
    
    # If Ctrl+C is pressed during the download, 
    # exits as gracefully as possible. This is specially
    # important for movies.
    try:
        the_file.write(socket.read())
    except KeyboardInterrupt:
        socket.close()
        the_file.close()
        os.remove(filename)
        return False
    
    socket.close()
    the_file.close()
    
    return True


def savestate(state):
    """
    Saves the current spidering state in a pickle file called
    pr0nbot.state.
    """
    try:
        f = open('pr0nbot.state', 'wb')
        pickle.dump(state, f)
        f.close()
    except (IOError, pickle.PickleError):
        return False
        
    return True


def loadstate(the_dir):
    """
    Loads the last spidering state, if it exists.
    """
    try:
        f = open(os.path.join(the_dir,'pr0nbot.state'), 'rb')
        state = pickle.load(f)
        f.close()
    except (IOError, pickle.PickleError):
        return False
    
    return state


def usage(msg = None):
    "Usage message, with possible insertion of error message"

    print "\nPr0nbot v%s by %s (%s)" % (__version__, __author__, __date__)
    print "- Because you're horny and lazy!\n"
    print "Usage: pr0nbot [options] url\n"
    print "\turl\t\tStarting URL for spidering."
    print "\nOptions:"
    print "\t-d x, --dir=x\t" \
          "Directory for downloaded pr0n (default: %s)." % defaultdir
    print "\t-m x, --min=x\t" \
          "Minimum size in k for download (default %d)." % defaultminsize
    print "\t-a, --aggro\tAGGRO MODE! Downloads from <img> tags too."
    print "\t-i, --ignore\tIgnores the saved spidering state."
    print "\t-v, --verbose\tBe talkative and annoying."
    print "\t-q, --quiet\tBe absolutely quiet."
    print "\t-h, --help\tThis help screen (whee!)."
    print "\t--nomovies\tDon't download movies."
    print "\t--nopics\tDon't download pictures.\n"
    if msg: print "%s\n" % msg


# On to business!
if __name__ == "__main__":

    if sys.platform in ('darwin', 'linux2'):
        homedir = os.environ['HOME']
    elif 'win' in sys.platform:
        homedir = os.environ['USERPROFILE']
    else:
        homedir = os.curdir
    configfile = os.path.join(homedir, ".pr0nbot.rc")
    ignorelist = getconfig(configfile)
    if not ignorelist:
        print "\nSomething is VERY wrong in your system: " \
              "can't read nor write in your home directory!\n"
        sys.exit(1)

    # Defaults
    the_dir   = defaultdir
    minsize   = defaultminsize
    start_url = ""
    quiet     = False
    verbose   = False
    nopics    = False
    nomovies  = False
    aggro     = False
    ignore    = False

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   "d:aim:vqh",
                                   ["dir=", "aggro", "ignore", "min=",
                                    "verbose", "quiet", "help",
                                    "nopics", "nomovies"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
        
    for o, a in opts:
        if o in ("-a", "--aggro")  : aggro    = True
        if o in ("-v", "--verbose"): verbose  = True
        if o in ("-q", "--quiet")  : quiet    = True
        if o in ("-i", "--ignore") : ignore   = True
        if o == "--nopics"         : nopics   = True
        if o == "--nomovies"       : nomovies = True

        if o in ("-d", "--dir"):
            if a:
                the_dir = a
            else:
                usage("You need to put something after --dir.")
                sys.exit(2)

        if o in ("-m", "--min"):
            if a:
                try:
                    minsize = int(a)
                except ValueError:
                    usage("--min needs a number!")
                    sys.exit(2)
            else:
                usage("--min needs a number!")
                sys.exit(2)

        if o in ("-h", "--help"):
            usage()
            sys.exit()

    if nopics and nomovies:
        # You eediot!
        print "\nYou specified --nopics and --nomovies... nothing to do!\n"
        sys.exit(2)
    
    state = None
    if ignore:
        statemsg = "Ignoring saved spidering state.\n"
    else:
        statemsg = ""
    if os.path.exists(os.path.join(the_dir, 'pr0nbot.state')) and not ignore:
        state = loadstate(the_dir)
        
    if state:
        statemsg  = "Saved state from previous spidering found! Resuming...\n"
        start_url = state['start_url']
        urls      = state['urls']
        visited   = state['visited']
        minsize   = state['minsize']
        nopics    = state['nopics']
        nomovies  = state['nomovies']
        aggro     = state['aggro']

    else:
        if args:
            if "http://" in args[0]:
                start_url = args[0]
            else:
                # Yo, pay attention!
                usage("You need to specify a complete url, "
                      "as in http://anysite.com/")
                sys.exit(2)
        else:
            usage("You must specify an URL or a directory "
                  "with a saved state to start.")
            sys.exit(2)
    
        try:
            if not os.path.exists(the_dir):
                os.mkdir(the_dir)
        except (OSError, IOError):
            print "\nYou don't have permission " \
                  "to write on this directory (%s).\n" % the_dir
            sys.exit(1)

    os.chdir(the_dir)
    
    if quiet: sys.stdout = NullWrite()

    print "\nPr0nbot v%s by %s (%s)\n" % (__version__, __author__, __date__)
    print "Pr0nbot has started!\n%s" % statemsg
    print "Starting URL: %s\nDirectory: %s\n" % (start_url, the_dir)
    if nopics:
        print "I won't download pictures."
        if aggro:
            aggro = False
            print "AGGRO MODE only works for pictures! I'm turning it off."
    if nomovies:
        print "I won't download movies."
    if aggro:
        print "AGGRO MODE, bitch!"
    print "Minimum file size for download: %dk." % minsize
    print "\nPress Ctrl+C at any time to stop.\n\n"

    if not verbose: sys.stdout = NullWrite()

    # Now, the main spidering loop.
   
    if not state:
        visited = []
        urls = [start_url]   

    while urls:
        try:
            url = urls.pop(0)
            # Don't run in circles
            if url in visited: continue
    
            result = crawl(url, ignorelist, aggro)
            if not result: continue
    
            print "URL: %s\n" % url
    
            if result['links']:
                urls += result['links']
    
            if result['pics'] and not nopics:
                print "Pics:\n"
                for pic in result['pics']: 
                    print pic
                    getpr0n(pic, minsize, True)
                print "\n"
    
            if result['movies'] and not nomovies:
                print "Movies:\n"
                for movie in result['movies']:
                    print movie
                    getpr0n(movie, minsize, False)
                print "\n"
    
            visited.append(url)
            visited = unique(visited)

        except:
            # Yeah, we're catching EVERYTHING. The code below
            # makes an elegant retreat in either accidental
            # or intentional interruptions.
            # TODO: Discover how to trap a SIGKILL properly.
            #       Right now it terminates the script without
            #       saving the state. As we're already catching
            #       EVERYTHING, I'm lost right now. - FZero
            ok = savestate( {'start_url':start_url,
                             'urls'     :urls,
                             'visited'  :visited,
                             'minsize'  :minsize,
                             'nopics'   :nopics,
                             'nomovies' :nomovies,
                             'aggro'    :aggro} )
            if ok:
                endmsg = "Spidering state saved."
            else:
                endmsg = "Spidering state could not be saved, sorry."

            if not quiet:
                sys.stdout = sys.__stdout__
            print "\nPr0nbot stopped! %s\n" % endmsg
            sys.exit()
