#!/usr/bin/env python3

import sys, os
import logging
import csv
import subprocess
import pprint

import time
import tempfile

import requests
import requests_file
import json

import persist

from io import BytesIO
import urllib
import pycurl
from http import HTTPStatus


_LOGGER = logging.getLogger(__name__)

SCRIPT_DIR = os.path.dirname(__file__)      ## full path to script's directory

TMP_DIR        = os.path.join( SCRIPT_DIR, os.pardir, os.pardir, "tmp" )
CACHE_DIR      = os.path.join( TMP_DIR, "cache" )
CACHE_REPO_DIR = os.path.join( CACHE_DIR, "repo" )

OUTPUT_CSV = os.path.join( TMP_DIR, "github_repos.csv" )
OUTPUT_CSV = os.path.abspath( OUTPUT_CSV )


GITHUB_PROFILE_LINK = "https://github.com/anetczuk"


os.makedirs( CACHE_DIR, exist_ok=True )
os.makedirs( CACHE_REPO_DIR, exist_ok=True )


# ====================================================================
# ====================================================================


def read_repositories():
    REPOS_URL = "https://api.github.com/users/anetczuk/repos?per_page=999"
    _LOGGER.info( "reading repos from: %s", REPOS_URL )

    response = read_url( REPOS_URL )
    if response is None:
        return

    ## resp_status = response[0]
    repos_data = response[1]
    repos_data.sort(key=lambda d: d['created_at']) 

    repos_data_path = os.path.join( CACHE_DIR, "repos_data.txt" )
    with open( repos_data_path, 'w' ) as repos_file:
        pprint.pprint( repos_data, repos_file, sort_dicts=False )

    header = [ 'name', 'category', 'summary', 'create_date', 'push_date', 'stars', 'commits', 'loc' ]
    
    with open( OUTPUT_CSV, 'w', encoding='UTF8' ) as csv_file:
        writer = csv.writer( csv_file, delimiter=',', quoting=csv.QUOTE_ALL )
        writer.writerow( header )
    
        for repo_item in repos_data:
            row = read_repo_info( repo_item )
            if row is None:
                return
            _LOGGER.info( "item found: %s", row )
            writer.writerow( row )
        
        _LOGGER.info( "output stored to file: %s", OUTPUT_CSV )

    _LOGGER.info( "done" )


def read_repo_info( repo_data ):
    repoName = repo_data["name"]
    cache_data_path = os.path.join( CACHE_REPO_DIR, repoName + ".pickle" )
    cached_data = persist.load_object_simple( cache_data_path, silent=True )
    if is_cache_valid( repo_data, cached_data ):
        ## cache valid
        return get_row_from_dict( cached_data )
    
    _LOGGER.info( "cache not found, scraping: %s", repoName )
    cached_data = scrap_repo_info( repo_data )
    if cached_data is None:
        ## unable to scrap data
        return None
    persist.store_object_simple( cached_data, cache_data_path )
    return get_row_from_dict( cached_data )


def scrap_repo_info( repo_data ):
#         print( json.dumps(repo_data, indent=4) )
    repoName = repo_data["name"]
    
    category = ""
    category = append_string( category, repo_data["language"], "|" )
    if repo_data["fork"] is True:
        category = append_string( category, "Fork", "|" )

    stars = repo_data["stargazers_count"]
    if stars < 1:
        stars = ""

    contribUrl = repo_data["contributors_url"]
    ## contribUrl = "https://api.github.com/repos/anetczuk/{}/stats/contributors".format( repoName )

    ## read commits number
    
    response = read_url( contribUrl )
    if response is None:
        return

    ## resp_status = response[0]
    resp_data = response[1]

    commitsNum  = ""

    for commiterData in resp_data:
        authorName = commiterData['login']
        ##authorData = commiterData['author']
        ##authorName = authorData['login']
        if authorName == "anetczuk":
            commitsNum = commiterData['contributions']
            break
    
    ## clone repository and count lines
    linesOfCode = ""
    forked = repo_data["fork"]
    if forked is False:
        clone_url = repo_data["clone_url"]
        linesOfCode = count_lines( clone_url )
    
    created_at = repo_data["created_at"]
    pushed_at  = repo_data["pushed_at"]
    
    return { "name": repoName,
             "category": category,
             "description": repo_data["description"],
             "created_at": created_at,
             "updated_at": repo_data["updated_at"],
             "pushed_at": pushed_at,
             "stars": stars,
             "commits_count": commitsNum,
             "lines_of_code": linesOfCode
            }


def get_row_from_dict( data_dict ):
    return [ data_dict["name"], 
             data_dict["category"], 
             data_dict["description"], 
             data_dict["created_at"], 
#              data_dict["updated_at"], 
             data_dict["pushed_at"], 
             data_dict["stars"], 
             data_dict["commits_count"],
             data_dict["lines_of_code"]
            ]


def is_cache_valid( item, cached_data ):
    if cached_data is None:
        return False
    if cached_data["updated_at"] != item["updated_at"]:
        return False
    if cached_data["pushed_at"] != item["pushed_at"]:
        return False
    return True


def count_lines( repoUrl ):
    _LOGGER.info( "counting lines for: %s", repoUrl )
    with tempfile.TemporaryDirectory() as tmpdirname:
        git_command = """git clone --depth 1 {} {}""".format( repoUrl, tmpdirname )
        cloneResult = subprocess.run( git_command, shell=True )
        if cloneResult.returncode != 0:
            _LOGGER.warning( "unable to clone repository: %s", repoUrl )
            return ""
        
        cloc_command="""cloc --exclude-lang=HTML,JSON,XML --exclude-dir=doc,lib,libs,external,build --json {0}""".format( tmpdirname )
        clocResult = subprocess.run( cloc_command, shell=True, stdout=subprocess.PIPE )
        if clocResult.returncode != 0:
            _LOGGER.warning( "unable to cloc repository: %s", repoUrl )
            return ""
    
        clocData = json.loads( clocResult.stdout )
        linesOfCode = clocData['SUM']['code']
        return linesOfCode

    return ""


def append_string( data1, data2, separator ):
    if data1 is None:
        return data2
    if len(data1) < 1:
        return data2
    return data1 + separator + data2


## return tuple: (status_code, content, headers)
def read_url_data_requests( urlpath ):
    session = requests.Session()
    session.mount( 'file://', requests_file.FileAdapter() )
#     session.config['keep_alive'] = False
#     response = requests.get( urlpath, timeout=5 )
    response = session.get( urlpath, timeout=20 )
#     response = requests.get( urlpath, timeout=5, hooks={'response': print_url} )
    return [ response.status_code, response.text, response.headers ]


def write_text( content, outputPath ):
    with open( outputPath, 'wt' ) as fp:
        fp.write( content )


# ====================================================================


class CUrlConnectionRAII():

    def __init__(self):
        self.connection = pycurl.Curl()

    def __enter__(self):
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()


def read_url_data_pycurl( url ):
    with CUrlConnectionRAII() as curl:
        # curl.setopt(pycurl.VERBOSE, 1)
        # curl.setopt( pycurl.HTTP_VERSION, pycurl.CURL_HTTP_VERSION_1_0 )        ## disable data chunks (causes pycurl to hang)

        # Set URL value
        curl.setopt( pycurl.URL, url )
        curl.setopt( pycurl.FOLLOWLOCATION, 1 )
        curl.setopt( pycurl.TIMEOUT, 30 )

        curl.setopt( pycurl.USERAGENT,
                    "Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko" )
#         curl.setopt( pycurl.USERAGENT,
#                     "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0" )
#         curl.setopt( pycurl.USERAGENT, "Mozilla/5.0 (X11; Linux x86_64)" )

        headers = {}
#         headers[ "Connection" ] = "keep-alive"

        headers.update( {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
#             "Accept-Encoding": "br",                          ## causes curl to receive bytes instead of string
            #"Accept-Encoding": "gzip, deflate, br",            ## causes curl to receive bytes instead of string
            "Accept-Language": "en-US,en;q=0.5",
        } )

        if len(headers) > 0:
            headersList = []
            for key, value in headers.items():
                headersList.append( f"{key}: {value}" )
            curl.setopt( pycurl.HTTPHEADER, headersList )

        # Write bytes that are utf-8 encoded

        header_obj = BytesIO()
        data_obj   = BytesIO()

        # curl.setopt( pycurl.WRITEFUNCTION, b_obj.write )
        curl.setopt( pycurl.HEADERFUNCTION, header_obj.write )
        curl.setopt( pycurl.WRITEDATA, data_obj )

#         curl.setopt(pycurl.HTTP_VERSION, pycurl.CURL_HTTP_VERSION_2_0)
#         curl.setopt(pycurl.SSL_VERIFYPEER, 0)
#         curl.setopt(pycurl.SSL_VERIFYHOST, 0)
#         curl.setopt(pycurl.COOKIEFILE, "")

        _LOGGER.debug( "performing curl request for %s", url )

        # Perform a file transfer
        curl.perform()

        resp_code = curl.getinfo( pycurl.RESPONSE_CODE )
#         if resp_code != 200:
#             message = HTTPStatus( resp_code ).phrase
# #             _LOGGER.info( "error code: %s: %s", resp_code, message )
#             raise urllib.error.HTTPError( url, resp_code, message, None, None )

        _LOGGER.debug( "converting curl response from %s", url )

        # Get the content stored in the BytesIO object (in byte characters)
        response_header = header_obj.getvalue()
        response_body   = data_obj.getvalue()

        # print( "xxx:", type(b_obj), type(get_body) )
        # print( "ccccc:", get_body )
        # print( 'Output of GET request:\n%s' % get_body.decode('utf8') )

        try:
            ## try convert to string
            converted_header = response_header.decode('utf8')
        except UnicodeDecodeError:
            ## it seems that received binary data (e.g. xls or zip)
            ## _LOGGER.error( "unable to convert curl response to string" )
            converted_header = response_header

        try:
            ## try convert to string
            converted_data = response_body.decode('utf8')
        except UnicodeDecodeError:
            ## it seems that received binary data (e.g. xls or zip)
            ## _LOGGER.error( "unable to convert curl response to string" )
            converted_data = response_body

        return [ resp_code, converted_data, converted_header ]


# read_url_data = read_url_data_pycurl
read_url_data = read_url_data_requests


def read_url( url_path ):
    print( "reading url:", url_path )
    while True:
        response = read_url_data( url_path )

        response_status = response[0]
        if response_status == 202:
            ## accepted: correct request but have to wait for response
#             print( "response headers:" )
#             header_dict = dict( response[2] )
#             pprint.pprint( header_dict )

            raise Exception( f"got 202 - seems like bad request: {url_path}" ) 
#             print( "got 202 status - wait and request:", url_path )
#             time.sleep( 2 )
#             continue

        response_data = response[1]
        data_dict = json.loads( response_data )

        if response_status != 200:
            print( "data:" )
            pprint.pprint( data_dict )

            print( "response headers:" )
            header_dict = dict( response[2] )
            pprint.pprint( header_dict )

            mess = data_dict.get( "message" , "<no message field>")
            _LOGGER.error( "message: %s status: %s", mess, response_status )
            return None

        return [ response_status, data_dict ]


# ====================================================================
# ====================================================================


def configure_logger( level=None ):
    formatter = create_formatter()
    consoleHandler = logging.StreamHandler( stream=sys.stdout )
    consoleHandler.setFormatter( formatter )

    logging.root.addHandler( consoleHandler )
    if level is None:
        logging.root.setLevel( logging.INFO )
    else:
        logging.root.setLevel( level )


def create_formatter(loggerFormat=None):
    if loggerFormat is None:
        loggerFormat = '%(asctime)s,%(msecs)-3d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s'
#        loggerFormat = ('%(asctime)s,%(msecs)-3d %(levelname)-8s %(threadName)s %(name)s:%(funcName)s '
#                        '[%(filename)s:%(lineno)d] %(message)s')
    dateFormat = '%H:%M:%S'
#    dateFormat = '%Y-%m-%d %H:%M:%S'
    return logging.Formatter( loggerFormat, dateFormat )


def main():
    configure_logger( "INFO" )
    read_repositories()


if __name__ == '__main__':
    main()

