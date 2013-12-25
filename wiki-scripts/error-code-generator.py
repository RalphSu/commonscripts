#!/usr/bin/python

from StringIO import StringIO
import getpass, traceback
import xmlrpclib
import json
import pprint   
import pycurl
import sys 
import os
import httplib2
import StringIO
import re

SPACEKEY = "CLOUD"
CONFLUENCE_URL = 'https://wiki.vip.corp.ebay.com/rpc/xmlrpc'
CONFLUENCE_LOGIN = "_cms_ss_client"
CONFLUENCE_PASSWORD = "1nt3Gr1tY"
CODE_SOURCE = "https://github.scm.corp.ebay.com/cloud-cms/cms.open"
SERVER = None
TOKEN = None

httpClient = httplib2.Http(".cache")

def main():
    initWikiLogin()
    writePage(genereatePageContent(getErrorCodeList()))
    print "Write completed!"

class Error:
    def __init__(self):
        self.code = " "
        self.name = ""
        self.component = ""
        self.description = " "

def getErrorCodeList():
    errors = []
    # dal errors
    _dal_errors(errors)
    # dual-write error
    _dualwrite_error(errors)

    # entmgr errors
    _entmgr_errors(errors)
    # query errors
    _query_errors(errors)
    print "Found total errors number : " + str(len(errors))
    return errors

def _dualwrite_error(errors) :
    e = Error()
    e.code = "1400"
    e.name = "ODB write error"
    e.description = "Exception trace will be in the json block"
    e.component = "cms dualwrite"
    errors.append(e)
    errors.append(Error())

def _entmgr_errors(errors):
    global httpClient
    entmgr_url = "https://github.scm.corp.ebay.com/cloud-cms/cms.open/raw/cms_release_w52/cms-core/entmgr/src/main/java/com/ebay/cloud/cms/entmgr/exception/CmsEntMgrException.java"
    enum_name = "EntMgrErrCodeEnum"
    resp, content = httpClient.request(entmgr_url, "GET")
    _get_error(errors, content, enum_name, "cms-entmgr")
    errors.append(Error())
    #print content

def _get_error(errors, content, enum_name, module):
    buf = StringIO.StringIO(content)
    start = False
    end = False
    comment = True
    description = ""
    # a simple state machine
    for line in buf:
        line = line.strip()
        print "Handling line: " + line
        if len(line) == 0:
            continue
        if (not start) and line.find(enum_name) >= 0:
            print "Start error enum: " + enum_name
            start = True
            continue
        if (start and (not end)) and line.find(enum_name) >= 0:
            print "End error enum: " + enum_name
            end = True
            break
        # start of comment
        if (start and (not end) and (not comment)) and (line.startswith('/*') or line.startswith('//')):
            print "Start comments"
            comment = True
            continue
        if (start and (not end) and comment) and line.endswith('*/') :
            print "End comments"
            comment = False
            continue
        if (start and comment) and (line.startswith('*')) :
            print "Appending comment" + line[1:]
            description = description + line[1:]
            continue
        # the error code line
        if start and (not end):
            m = re.search(r"([A-Z_].*)\((\d+)\)", line)
            if not m == None:
                print "     Add error %s(%s)" % (m.group(1), m.group(2))
                e = Error()
                e.name = m.group(1)
                e.code = m.group(2)
                e.description = description
                e.component = module
                # reset description
                description = ""
                errors.append(e)

    buf.close()


def _dal_errors(errors):
    global httpClient
    dal_url = "https://github.scm.corp.ebay.com/cloud-cms/cms.open/raw/cms_release_w52/cms-core/dal/src/main/java/com/ebay/cloud/cms/dal/exception/CmsDalException.java"
    enum_name= "DalErrCodeEnum"
    resp, content = httpClient.request(dal_url, "GET")
    _get_error(errors, content, enum_name, "cms-dal")
    errors.append(Error())

def _query_errors(errors):
    global httpClient
    query_url = "https://github.scm.corp.ebay.com/cloud-cms/cms.open/raw/cms_release_w52/cms-core/query/src/main/java/com/ebay/cloud/cms/query/exception/QueryException.java"
    enum_name = "QueryErrCodeEnum"
    resp, content = httpClient.request(query_url, "GET")
    _get_error(errors, content, enum_name, "cms-query")
    errors.append(Error())


def genereatePageContent(errors):
    global CODE_SOURCE
    content=''' <HTML>
    <body>
    <H1>Description</H1>
    <p> Please note: This page is automcatically generated from <a href=%s>CMS code source</a>. 
    <p> This wiki page to address CMS rest API error code. CMS rest api result will have two error code, one is http code, which mostly conform to the <a href="https://wiki.vip.corp.ebay.com/display/CLOUD/RESTful+design+standard">RESTful design standard</a>. Besides, CMS also defines a CMS own error code, based on the error code, the client would understand which happens when some service doesn't work.
    </body>
    <H1>CMS Rest API Error Code List</H1>
    <TABLE border=1>
    <THEAD><TH>ErrorCode</TH><TH>Error Code Name</TH><TH>Component</TH><TH>Description</TH></THEAD>
    <TBODY>
        '''
    for error in errors:
        td_start = "<TD>"
        td_end = "</TD>\n"
        if error.description.find("@deprecated") >= 0 :
            td_start = "<TD><s><em>"
            td_end = "</em></s></TD>\n"

        line = "<TR>\n"
        line = line + td_start + error.code + td_end
        line = line + td_start + error.name + td_end
        line = line + td_start + error.component + td_end
        line = line + td_start + error.description + td_end
        line = line + "</TR>\n"
        content = content + line

    content = content + '''
    </TBODY>
    </TABLE>
    </body>
    </HTML>'''
    content = content % CODE_SOURCE
    # print content
    return content

def writePage(content):
    global SERVER
    global TOKEN
    page = {}
    pagename = "CMS Rest API Error Code List"
    try:
        page = SERVER.confluence2.getPage(TOKEN, SPACEKEY, pagename)
        pass
    except xmlrpclib.Fault as err:
        print(err)
    if page == {}:
        print '''Could not find page %s : %s. Will try create a new one!''' % (SPACEKEY, TOKEN)
    else:
        print '''Found page %s : %s. Will try override!''' % (SPACEKEY, pagename)

    page['space'] = SPACEKEY
    page['title'] = pagename
    page['parentId'] = "173823877" ## this is the page id for https://wiki.vip.corp.ebay.com/display/CLOUD/CMS+Rest+API+Error+Code+Category
    page['content'] = content
    SERVER.confluence2.storePage(TOKEN, page)

def initWikiLogin():
    global SERVER, TOKEN, CONFLUENCE_LOGIN, CONFLUENCE_PASSWORD
    #CONFLUENCE_LOGIN=raw_input('Confluence Username: ')
    #CONFLUENCE_PASSWORD=getpass.getpass('Confluence Password: ')
    SERVER = xmlrpclib.ServerProxy(CONFLUENCE_URL);
    TOKEN = SERVER.confluence2.login(CONFLUENCE_LOGIN, CONFLUENCE_PASSWORD);


if __name__ == "__main__":
    main()