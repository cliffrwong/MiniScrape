import os
import time
import string
import urllib
import re

# from unidecode import unidecode
from bs4 import BeautifulSoup
# from werkzeug.urls import url_fix
# import MySQLdb
# from makedb.globalz import addhttp_header, downloads_path, getsoup, cursor

def removeDuplicates(seq):
    """ Remove duplicates from seq while preserving order
    
    """
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

def imdbBingSearch(query):
    """ Search query string on Bing. Only get results from the imdb domain name.
    Return list of imdb IDs

    Parameters
    ----------
    query : the query string

    Returns
    -------
    imdbIDs : list
        list of imdbID's found by Bing

    """
    sitelink_begin = r'imdb\.com/title/tt'
    numResults = 5
    urltitle = urllib.parse.quote("site:\"imdb.com/title\" {0}".format(query))
    url = 'http://www.bing.com/search?q={query}&go=Submit&qs=n&form=QBRE&count'\
          '={numResults}&pq={query}'.format(query=urltitle, numResults=numResults)
    resp = getContent(url)
    if resp:
        content = resp.read()
        sitesearch = sitelink_begin + '([0-9]+)/\" h'
        imdbIDs = re.findall(sitesearch, content.decode())
        imdbIDs = removeDuplicates(imdbIDs)
    else:
        imdbIDs = []
    return imdbIDs

def getContent(url):
    """ Takes the url and returns the response from urlopen
    Creating a separate function avoids checking for exceptions all
    through the code.

    Parameters
    ----------
    url : string
    
    Returns
    -------
    resp : HTTPResponse object

    """
    req = urllib.request.Request(url)
    req.add_header('User-Agent', "'Mozilla/5.0 (Windows NT 6.1; WOW64)")
    try:
        resp = urllib.request.urlopen(req)
    except urllib.error.URLError as e:
        if hasattr(e, 'reason'):
            print('We failed to reach a server.')
            print('Reason: ', e.reason)
        elif hasattr(e, 'code'):
            print('The server couldn\'t fulfill the request.')
            print('Error code: ', e.code)
        return None
    return resp

def getAmazonURL(link):
    """ The link on IMDB to the movie's corresponding amazon page needs to be 
    redirected. This function returns the final destination URL on amazon. 

    Parameters
    ----------
    link : string
        this is the path of the url that goes to the movie's amazon page.
        But it's domain name is imdb.com and needs to be redirected. 

    Returns
    -------
    finalurl : string
        the final url with amazon.com domain name for the movie.

    """
    url = 'http://www.imdb.com' + link
    resp = getContent(url)
    if resp:
        finalurl = resp.geturl()
        return finalurl
    else:
        return ""


def fancyIMDBpages(imdbDict, soup):
    """ Same as bsIMDB to extract data from IMDB page except this 
    is for promotional movies where the html is different.
    
    Parameters
    ----------
    imdbDict : dictonary
        contains current information about this movie
    soup : beautiful soup object of imdb page

    Returns
    -------
    imdbDict : dictionary
        contains info about this movie that we got from the imdb page.
    
    """
    # Extract the movie title
    try:
        header = soup.find("h1", {"class":"header"})
        titleStr = header.get_text()
        imdbDict['title'] = re.sub('\([^\(\)]+\)', '', titleStr).strip()
    except (AttributeError, TypeError) as e:
        return None

    # Extract the movie's released year
    try:
        imdbDict["year"] = header.find('a').get_text().strip()
    except (AttributeError, TypeError) as e:
        # The year is not available, this is probably a TV show so ignore this.
        imdbDict["year"] = '0000'
    
    # Extract the movie's "type". This is usually the movie's rating.
    # This helps me tell the difference between this being a movie or TV show
    try:
        infobar = soup.find("div", { "class" : "infobar" })
        movType = infobar.find('meta',{'itemprop':'contentRating'})['content']
        imdbDict["type"] = movType
    except (AttributeError, TypeError) as e:
        imdbDict["type"] = 'NA'
    
    return imdbDict
    
def bsIMDB(imdbID):
    """ Extact info about movie from the imdb page and store it in movieList.
    Parameters
    ----------
    imdbID : string
        unique imdb ID for the movie

    Returns
    -------
    imdbDict : dictionary
        contains info about this movie that we got from the imdb page.
    
    """
    # initialize movie's info dictonary
    imdbDict = {}
    imdbDict['imdbID'] = 'tt' + imdbID
    url = 'http://www.imdb.com/title/tt{imdbID}'.format(imdbID=imdbID)
    print(url)
    resp = getContent(url)
    if resp:
        content = resp.read()
    else:
        return None
    # Create beautiful soup object from imdb page's content
    soup = BeautifulSoup(content, "lxml")

    # Get the movie title
    try:
        result = soup.find("div", { "class" : "title_wrapper" })
        result2 = result.find("h1", {"itemprop":"name"})
        titleStr = result2.get_text()
        titleStr = re.sub('\([^\(\)]+\)', '', titleStr)
        imdbDict['title'] = titleStr.strip()
    except (AttributeError, TypeError) as e:
        imdbDict['title'] = ""
    
    # The above extraction may not work for some promotional movies with 
    # a big splash page. Call fancyIMDBpages in that case.
    if not imdbDict['title']:
        return fancyIMDBpages(imdbDict, soup)
        
    # Get the movie's release year
    try:
        year = result2.find('a').get_text()
        imdbDict["year"] = year.strip()
    except (AttributeError, TypeError) as e:
        imdbDict["year"] = '0000'
    
    # Get the movie type/content rating. 
    try:
        movType = result.find('meta',{'itemprop':'contentRating'})['content']
        imdbDict["type"] = movType
    except (AttributeError, TypeError) as e:
        imdbDict["type"] = 'NA'

    # Get imageURL
    try:
        imdbImageStr = soup.find('link',{'rel':'image_src'}).get('href')
        # print(imdbImageStr)
        imageURL_begin = "http:\/\/ia\.media-imdb\.com\/images\/M\/"
        imageURL_end = "\._V1"
        m = re.search(imageURL_begin + "(.*)" + imageURL_end, imdbImageStr)
        imdbDict["imageURL"] = m.group(1)
    except (AttributeError, TypeError) as e:
        imdbDict["imageURL"] = ""
    
    # Get the amazon ID 
    try:
        amazonIDpat = r"(B0\d\w+)"
        amazonIDpat_obj = re.compile(amazonIDpat)
        amazonOrigLink = soup.find('a',{'class':'segment-link'}).get('href')
        finalAmazonURL = getAmazonURL(amazonOrigLink)
        match = amazonIDpat_obj.search(finalAmazonURL)
        imdbDict["amazonID"] = match.group(1).strip() if match else ""
    except (AttributeError, TypeError) as e:
        imdbDict["amazonID"] = ""

    return imdbDict

def alreadyExist(movieDict):
    """ Check if movie that we want to add is already in the database.
    This is commented out for github. Implement your own method to check db here.
    Right now it always returns False.

    Parameters
    ----------
    movieDict : dictonary containing movie's info

    Returns
    -------
    exists : bool
        returned value tells whether movieDict already exists in db
    """
    return False
    """ Uncomment below to check if this movie is already in database """
    # cursor.execute('SELECT movID, pbmovname, hashX FROM subtitleserver_movies'\
    #                'WHERE imdbID = %(imdbID)s', movieDict)
    # row = cursor.fetchone()
    # if row is not None:
    #   movieDict['movID_old'] = row[0]
    #   return True
    # else:
    #   return False

def insert2DB(movieDict):
    """ Insert the selected movie into the database. This is commented out below.
    It just prints the movie's dictionary into stdout.

    Parameters
    ----------
    movieDict : dictonary containing movie's info

    """
    print(movieDict)
    # cursor.execute('INSERT INTO subtitleserver_movies (imdbID, imageURL, title,'\
    #               'year, pbmovname, hashX, type, amazonID, lastupdate) VALUES'\
    #               '(\"{0[imdbID]}\", \"{0[imageURL]}\", \"{0[title]}\",'\
    #               '{0[year]}, \"{0[pbmovname]}\", \"{0[hashX]}\", \"{0[type]}\"'\
    #               ', \"{0[amazonID]}\', \"{1}\") \
    #               'ON DUPLICATE KEY UPDATE pbmovname = \"{0[pbmovname]}\", hashX'\
    #               '= \"{0[hashX]}\", amazonID = \"{0[amazonID]}\", lastupdate ='\
    #               '\"{1}\", rtmatch = 0, inQueue=0, downloaded=0, dlnormal=0, '\
    #               'audified=0, hashified=0, uploaded=0, mastersubhere=0, '\
    #               'subprocessed=0, mastersub1found=0, done=0'.format(movieDict,\
    #               time.strftime('%Y-%m-%d %H:%M:%S')))
    # movieDict['movID'] = cursor.lastrowid
    # print(cursor.lastrowid)
    
