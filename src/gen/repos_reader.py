#!/usr/bin/env python3

import sys, os
import logging
import csv
import subprocess
import pprint

import tempfile

import requests
import requests_file
import json

import persist


_LOGGER = logging.getLogger(__name__)

SCRIPT_DIR = os.path.dirname(__file__)      ## full path to script's directory

TMP_DIR   = os.path.join( SCRIPT_DIR, os.pardir, os.pardir, "tmp" )
CACHE_DIR = os.path.join( TMP_DIR, "cache" )

OUTPUT_CSV = os.path.join( TMP_DIR, "github_repos.csv" )
OUTPUT_CSV = os.path.abspath( OUTPUT_CSV )


GITHUB_PROFILE_LINK = "https://github.com/anetczuk"


os.makedirs( CACHE_DIR, exist_ok=True )


# ====================================================================
# ====================================================================


def read_repositories():
    REPOS_URL = "https://api.github.com/users/anetczuk/repos?per_page=999"
    _LOGGER.info( "reading repos from: %s", REPOS_URL )
    
    userJson = read_url_response( REPOS_URL )
    userData = json.loads( userJson.text )
    
    if userJson.status_code != 200:
        _LOGGER.error( "message: %s status: %s", userData["message"], userJson.status_code )
        return

    header = [ 'name', 'category', 'summary', 'create_date', 'push_date', 'stars', 'commits', 'loc' ]
    
    with open( OUTPUT_CSV, 'w', encoding='UTF8' ) as csv_file:
        writer = csv.writer( csv_file, delimiter=',', quoting=csv.QUOTE_ALL )
        writer.writerow( header )
    
        for item in userData:
            row = read_repo_info( item )
            if row is None:
                return
            _LOGGER.info( "item found: %s", row )
            writer.writerow( row )
        
        _LOGGER.info( "output stored to file: %s", OUTPUT_CSV )

    _LOGGER.info( "done" )


def read_repo_info( item ):
    repoName = item["name"]
    cache_data_path = os.path.join( CACHE_DIR, repoName + ".pickle" )
    cached_data = persist.load_object_simple( cache_data_path, silent=True )
    if is_cache_valid( item, cached_data ):
        ## cache valid
        return get_row_from_dict( cached_data )
    
    _LOGGER.info( "cache not found, scraping: %s", repoName )
    cached_data = scrap_repo_info( item )
    if cached_data is None:
        ## unable to scrap data
        return None
    persist.store_object_simple( cached_data, cache_data_path )
    return get_row_from_dict( cached_data )


def scrap_repo_info( item ):
#         print( json.dumps(item, indent=4) )
    repoName = item["name"]
    
    category = ""
    category = append_string( category, item["language"], ";" )
    if item["fork"] is True:
        category = append_string( category, "Fork", ";" )

    stars = item["stargazers_count"]
    if stars < 1:
        stars = ""
    
    ## read commits number
    commitsNum = ""
    contribUrl = "https://api.github.com/repos/anetczuk/{}/stats/contributors".format( repoName )
    contribResp = read_url_response( contribUrl )
    contribData = json.loads( contribResp.text )
     
    if contribResp.status_code != 200:
        print( "data:", contribData, "raw:", contribResp, "headers:" )
        pprint.pprint( dict( contribResp.headers ) )
        mess = contribData.get( "message" , "<no message field>")
        _LOGGER.error( "message: %s status: %s", mess, contribResp.status_code )
        return None
     
    for commiterData in contribData:
        authorData = commiterData['author']
        authorName = authorData['login']
        if authorName == "anetczuk":
            commitsNum = commiterData['total']
            break
    
    ## clone repository and count lines
    linesOfCode = ""
    forked = item["fork"]
    if forked is False:
        clone_url = item["clone_url"]
        linesOfCode = count_lines( clone_url )
    
    created_at = item["created_at"]
    pushed_at  = item["pushed_at"]
    
    return { "name": repoName,
             "category": category,
             "description": item["description"],
             "created_at": created_at,
             "updated_at": item["updated_at"],
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
        
        cloc_command="""cloc --exclude-lang=HTML --exclude-dir=doc,lib,libs,external,build --json {0}""".format( tmpdirname )
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


def read_url_response( urlpath ) -> requests.Response:
    session = requests.Session()
    session.mount( 'file://', requests_file.FileAdapter() )
#     session.config['keep_alive'] = False
#     response = requests.get( urlpath, timeout=5 )
    response = session.get( urlpath, timeout=10 )
#     response = requests.get( urlpath, timeout=5, hooks={'response': print_url} )
    return response


def read_url( urlpath ):
    response = read_url_response( urlpath )
    return response.text


def write_text( content, outputPath ):
    with open( outputPath, 'wt' ) as fp:
        fp.write( content )


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

