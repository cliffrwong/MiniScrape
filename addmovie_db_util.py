#!/usr/bin/env python
# -*- coding: utf-8 *
""" Helper methods for database access.

The database code has been commented out but you can change this for your
database setup.

"""


# import MySQLdb
# from makedb.globalz import cursor

def alreadyExist(movieDict):
    """ Check if movie that we want to add is already in the database.
    This is commented out for github. Implement your own method to check db
    here. Right now it always returns False.

    Parameters
    ----------
    movieDict : dictonary containing movie's info

    Returns
    -------
    exists : bool
        returned value tells whether movieDict already exists in db
    """
    return False
    # Uncomment below to check if this movie is already in database
    # cursor.execute('SELECT movID, pbmovname, hashX FROM'
                   # 'subtitleserver_movies WHERE imdbID = %(imdbID)s',
                   # movieDict)
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
    # cursor.execute('INSERT INTO subtitleserver_movies (imdbID, imageURL,'
    #                'title, year, pbmovname, hashX, type, amazonID,'
    #                'lastupdate) VALUES (\"{0[imdbID]}\", \"{0[imageURL]}\",'
    #                '\"{0[title]}\", {0[year]}, \"{0[movname]}\",'
    #                '\"{0[hashX]}\", \"{0[type]}\" , \"{0[amazonID]}\','
    #                '\"{1}\") ON DUPLICATE KEY UPDATE movname ='
    #                '\"{0[movname]}\", hashX = \"{0[hashX]}\", amazonID ='
    #                '\"{0[amazonID]}\", lastupdate = \"{1}\", rtmatch = 0,'
    #                'inQueue=0, downloaded=0, dlnormal=0, audified=0,'
    #                'hashified=0, uploaded=0, mastersubhere=0,'
    #                'subprocessed=0, mastersub1found=0, done=0'
    #                .format(movieDict, time.strftime('%Y-%m-%d %H:%M:%S')))
    # movieDict['movID'] = cursor.lastrowid
    # print(cursor.lastrowid)
