#!/usr/bin/env python3

import sys, os
import logging
import pathlib
import csv
import datetime
 
from pandas import DataFrame


_LOGGER = logging.getLogger(__name__)

SCRIPT_DIR = os.path.dirname(__file__)      ## full path to script's directory


GITHUB_PROFILE_LINK = "https://github.com/anetczuk"

SUBFIELD_SEPARATOR = "|"


# ====================================================================
# ====================================================================


class CategoriesDict():
    
    def __init__(self):
        self.dataDict = {}
        
    def keys(self):
        return list( self.dataDict.keys() )
    
    def items(self, key):
        return self.dataDict.get( key, None )
    
    def add(self, key, item):
        dictData = self.dataDict.get( key, list() )
        dictData.append( item )
        self.dataDict[ key ] = dictData
        
    def addKeys(self, keysList, item):
        for key in keysList:
            self.add( key, item )


# =============================================


def generate():
    csv_path = os.path.join( SCRIPT_DIR, "repos_description.csv" )
    _LOGGER.info( "parsing file %s", csv_path )
    configDict, dataMatrix = parse_csv( csv_path )
    
    configDict[ 'input_file' ] = csv_path
    
    # print( "config:", configDict )
    # print( "data:", dataMatrix )
    
    outputDir = os.path.join( SCRIPT_DIR, os.pardir, os.pardir, "docs" )
    generate_description( configDict, dataMatrix, outputDir )


def generate_description( configDict, dataMatrix, outputDir ):
    _LOGGER.info( "generating repositories description" )
    
    ## read categories
    categoriesMap = CategoriesDict()
    
    rowsList = []
    for _, row in dataMatrix.iterrows():
        rowsList.append( row )
    def sort_key_row_create_date( row ):
        return row['push_date']
    rowsList.sort( key=sort_key_row_create_date, reverse=True )
    
    for row in rowsList:
        item_categories = row['category']
        item_categories = item_categories.strip()
        if len(item_categories) < 1:
            continue
        categories = item_categories.split( SUBFIELD_SEPARATOR )
        categoriesMap.addKeys( categories, row )
    
#     print( "found categories:", categoriesMap.data )
    
    
    output_content = ""

    ### === file header ===
    input_file  = configDict[ "input_file" ]
    output_name = "repos.md"

    output_content += \
"""---
layout: default
home: true
allow_comments: true
---

%(file_preamble_info)s


# Repositories

Following page presents list of published repositories divided into few categories.

""" % {
        "file_name": output_name,
        "file_preamble_info": file_preamble( input_file, "[comment]: #" )
    }


    ### === file content ===

    category_order_first = configDict[ "category_order_first" ]
    category_order_first = category_order_first.split( SUBFIELD_SEPARATOR )
    category_order_last  = configDict[ "category_order_last" ]
    category_order_last  = category_order_last.split( SUBFIELD_SEPARATOR )
    
    categoriesList = categoriesMap.keys()
    categoriesList.sort()
    
    categoriesList = substract_list( categoriesList, category_order_first )
    categoriesList = substract_list( categoriesList, category_order_last )
    categoriesList = category_order_first + categoriesList + category_order_last
    
    ## generate table of content
    output_content += """Non-exclusive categories:\n""".format()
    for cat in categoriesList:
#         output_content += """## {}\n\n""".format( cat )
        items = categoriesMap.items( cat )
        if items is None or len(items) < 1:
            continue
        category_anchor = section_link_id( cat, "#cat_" )
        output_content += """- [{0}]({1})\n""".format( cat, category_anchor )
        
    output_content += "\n\n"
    output_content += """Repositories are also presented in form of <a href="#repos_table">sortable table</a>"""
    
    output_content += "\n\n"
    
    output_content += "## Categories:\n\n"
    
    ## generate content
    for cat in categoriesList:
        category_anchor = section_link_id( cat, "cat_" )
        output_content += """### <a name="{1}"></a> {0}\n\n""".format( cat, category_anchor )
        items = categoriesMap.items( cat )
        if items is None or len(items) < 1:
            continue
        
        category_loc = 0
        category_commits = 0
        category_stars = 0
        
        for row in items:
            item_name       = row['name']
            
            if item_name.startswith( "#" ):
                output_content += """\n"""
                continue
    
            ## item_categories = row['category']
            item_summary    = row['summary']
            item_stars      = row.get( "stars", 0 )
            item_commits    = row.get( "commits", 0 )
            item_loc        = row.get( "loc", "" )
            
            if item_loc == "":
                item_loc = 0
            else:
                item_loc = int( item_loc )
            
            if cat == "Fork":
                ## do not put LOC for Forks
                item_loc = 0
            
            if len( item_commits ) > 0:
                item_commits = int( item_commits )
            else:
                item_commits = 0
            
            if len( item_stars ) > 0:
                item_stars = int( item_stars )
            else:
                item_stars = 0
            
            commits_entry = ""
            if item_commits > 0:
                commits_entry = """<br/>\ncommits: {0}""".format( item_commits )
            stars_entry = ""
            if item_stars > 0:
                stars_entry = """<br/>\nstars: {0}""".format( item_stars )           
            loc_entry = ""
            if item_loc > 0:
                loc_entry = """<br/>\nlines of code: {0}""".format( item_loc )

            output_content += """[{0}]({1}/{0})<br/>\n{2}{3}{4}{5}\n\n""".format( item_name, GITHUB_PROFILE_LINK, item_summary, commits_entry, stars_entry, loc_entry )
            
            category_commits += item_commits
            category_loc     += item_loc
            category_stars   += item_stars

        output_content += "<br/>\nCategory summary:\n"
        output_content += "<br/>\nprojects: %s" % len(items)
        output_content += "<br/>\ncommits: %s" % category_commits
        output_content += "<br/>\nlines of code: %s" % category_loc
        output_content += "<br/>\nstars: %s" % category_stars
        output_content += "\n\n"

    output_content += "\n\n"

    #### generate table -- GitHub markdown does not support sorted tables, so it's needed to use HTML directly
    output_content += "## Repositories table\n"
    
    ## sortable taken from: https://www.kryogenix.org/code/browser/sorttable    
    output_content += """<script src="/js/sorttable.js"></script>\n"""
    output_content += """<a name="repos_table"></a>\n"""
    output_content += """<table class="sortable">\n"""
    output_content += """<thead> <tr>
    <th>Repository</th>
    <th>Create date</th>
    <th>Last commit</th>
    <th style="text-align:center">Commits</th>
    <th style="text-align:center">Stars</th>
    <th style="text-align:center">Lines of code</th>
</tr> </thead>\n<tbody>\n"""

    commits_sum = 0
    stars_sum = 0
    loc_sum = 0
    for row in rowsList:
        commits = row[ "commits" ]
        stars = row[ "stars" ]
        locs = row[ "loc" ]
        createDate = row[ "create_date" ]
        createDate = datetime.datetime.strptime( createDate, "%Y-%m-%dT%H:%M:%SZ" )
        pushDate = row[ "push_date" ]
        pushDate = datetime.datetime.strptime( pushDate, "%Y-%m-%dT%H:%M:%SZ" )
        output_content += """<tr>
        <td><a href="{1}/{0}">{0}</a></td>
        <td>{2}</td> <td>{3}</td> <td style="text-align:center">{4}</td>
        <td style="text-align:center">{5}</td>
        <td style="text-align:center">{6}</td>
</tr>\n""".format( row[ "name" ], GITHUB_PROFILE_LINK, createDate, pushDate, commits, stars, locs )
        if len(commits) > 0:
            commits_sum += int( commits )
        if len(stars) > 0:
            stars_sum += int( stars )
        if len(locs) > 0:
            loc_sum += int( locs )
    output_content += """\n</tbody>\n"""
    output_content += """<tfoot> <tr>
      <th id="total" colspan="3" style="text-align:right">Total:</th>
      <th style="text-align:center">{}</th>
      <th style="text-align:center">{}</th>
      <th style="text-align:center">{}</th>
</tr> </tfoot>""".format( commits_sum, stars_sum, loc_sum )
    output_content += """</table>\n"""
    

    # _LOGGER.debug( "generated file:\n%s" + output_content )

    ### === writing to file ===
    os.makedirs( outputDir, exist_ok=True )
    outputFile = os.path.join( outputDir, output_name )
    with open( outputFile, "w" ) as enumFile:
        enumFile.write( output_content )


## =========================================================================


def substract_list( from_list, items ):
    return [fruit for fruit in from_list if fruit not in items]

    
def section_link_id( text, prefix ):
    text = text.replace( " ", "_" )
    return prefix + text.lower()


def file_preamble( input_file, line_comment ):
    info = \
"""%(line_comment)s
%(line_comment)s        File was automatically generated by: %(generator)s
%(line_comment)s        Input file: %(input_file)s
%(line_comment)s
%(line_comment)s        Any change in file will be lost.
%(line_comment)s""" % { 
                "line_comment": line_comment,
                "generator": generator_name(), 
                "input_file": input_dir_name( input_file )
            }
    return info


def generator_name():
    path = pathlib.Path( *pathlib.Path(__file__).parts[-4:] )
    return str(path)


def input_dir_name( input_file ):
    workdir = os.path.join( SCRIPT_DIR, ".." )
    path = os.path.relpath( input_file, workdir)
    return str(path)


# def parameter_from_row( row, parameter, defaultValue ):
#     parameter_name = row.get( "parameter", defaultValue )
#     if len( parameter_name ) > 0:
#         return parameter_name
#      
#     enum_value = row['enum_value']
#     return enum_value.lower()


# ===================================================================


## returns tuple ( config_dict, data_matrix )
def parse_csv( csv_path ):
    with open( csv_path, newline='' ) as csvfile:
        dataReader = csv.reader( csvfile, delimiter=',', quotechar='"' )
        
        configPart = False
        dataPart   = False
    
        configList = list()
        dataList   = list()
        
        for line in dataReader:
            # print( line )
            rawLine = ''.join( line )
            if len(rawLine) > 0:
                if rawLine == "Config:":
                    configPart = True
                    continue
                if rawLine == "Data:":
                    dataPart = True
                    continue
                # if rawLine[0] == '#':
                #    continue
                # if rawLine.startswith( "//" ):
                #    continue
            else:
                configPart = False
                dataPart   = False
                continue

            if configPart is True:
                configList.append( line )
            elif dataPart is True:
                dataList.append( line )

        configMatrix = create_matrix( configList )
        dataMatrix   = create_matrix( dataList )
        
        ## convert matrix to dict
        zip_iterator = zip( configMatrix["parameter"], configMatrix["value"] )
        configDict   = dict( zip_iterator )
        
        return ( configDict, dataMatrix )
    return ( None, None )


def create_matrix( dataList ):
    if len(dataList) < 1:
        raise Exception( "No data field found" )

    matrixHeader = dataList[ 0 ]
    matrixData   = DataFrame( dataList )

    ## remove redundant columns
    headerSize = len(matrixHeader)
    colsNum = len(matrixData.columns)
    if colsNum > headerSize:
        for _ in range( headerSize, colsNum ):
            colName = matrixData.columns[len(matrixData.columns)-1]
            matrixData.drop(colName, axis=1, inplace=True)

    matrixData.columns = matrixHeader

    matrixData = matrixData.iloc[1:]        ## remove first row (containing header labels)

    return matrixData


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
    generate()
    _LOGGER.info( "done" )


if __name__ == '__main__':
    main()

