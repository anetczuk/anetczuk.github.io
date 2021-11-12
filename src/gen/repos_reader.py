#!/usr/bin/env python3

import sys, os
import logging
import csv
import subprocess

import tempfile

import requests
import requests_file
import json


_LOGGER = logging.getLogger(__name__)

SCRIPT_DIR = os.path.dirname(__file__)      ## full path to script's directory

OUTPUT_CSV = os.path.join( SCRIPT_DIR, "..", "..", "tmp", "github_repos.csv" )
OUTPUT_CSV = os.path.abspath( OUTPUT_CSV )


GITHUB_PROFILE_LINK = "https://github.com/anetczuk"


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
    #         print( json.dumps(item, indent=4) )
            repoName = item["name"]
            
            category = ""
            category = append_string( category, item["language"], ";" )
            if item["fork"] is True:
                category = append_string( category, "Fork", ";" )
        
            created_at = item["created_at"]
            pushed_at  = item["pushed_at"]
        
            stars = item["stargazers_count"]
            if stars < 1:
                stars = ""
            
            ## read commits number
            commitsNum = ""
            contribUrl = "https://api.github.com/repos/anetczuk/{}/stats/contributors".format( repoName )
            contribJson = read_url_response( contribUrl )
            contribData = json.loads( contribJson.text )
             
            if contribJson.status_code != 200:
                print( "data:", contribData )
                _LOGGER.error( "message: %s status: %s", contribData["message"], contribJson.status_code )
                return
             
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
            
            row = [ item["name"], category, item["description"], created_at, pushed_at, stars, commitsNum, linesOfCode ]
            _LOGGER.info( "item found: %s", row )
            writer.writerow( row )
        
        _LOGGER.info( "output stored to file: %s", OUTPUT_CSV )

    _LOGGER.info( "done" )


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


def read_url_response( urlpath ):
    session = requests.Session()
    session.mount( 'file://', requests_file.FileAdapter() )
#     session.config['keep_alive'] = False
#     response = requests.get( urlpath, timeout=5 )
    response = session.get( urlpath, timeout=5 )
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

