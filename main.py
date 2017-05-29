#! /opt/local/bin/python
# coding: utf8

import re
from cStringIO import StringIO
import sys
from os import path
import subprocess
import mysql.connector

class SES:
    ALLOWD_SCRIPT = {
        'python': ('@@begin-python', '@@end-python', 'self.parsePython()'),
        'sql': ('@@begin-sql', '@@end-sql', 'self.parseSql()'),
        'bash': ('@@begin-bash', '@@end-bash', 'self.parseBash()')
    }
    FILE_WATCHED = ''
    MYSQL_LOGIN = {'login': 'LOGIN', 'password': 'PASS', 'host': 'HOST', 'database': 'DB'}

    def __init__(self, file):
        if not path.exists(file):
            print 'Error could not get the file: '+file
            sys.exit(1)

        self.FILE_WATCHED = file
        content = open(file, 'r').read()

        for lang, macros in self.ALLOWD_SCRIPT.items():
            if re.findall(self.ALLOWD_SCRIPT[lang][0]+'.*'+self.ALLOWD_SCRIPT[lang][1], content, re.DOTALL):
                exec macros[2]

    def parsePython(self):
        oldContent = open(self.FILE_WATCHED, 'r').read()
        codes = re.findall(self.ALLOWD_SCRIPT['python'][0]+'(.*?)'+self.ALLOWD_SCRIPT['python'][1], oldContent, re.DOTALL)

        # if there is not python codes
        if not codes:
            return

        toReplace = {}
        for code in codes:
            pythonCommand = code

            # getting the stdout
            old_stdout = sys.stdout
            sys.stdout = mystdout = StringIO()

            # exec the code from the file
            exec pythonCommand
            newCode = mystdout.getvalue()

            # reset stdout
            sys.stdout = old_stdout

            # init a dict to store what there is to replace in the file
            toReplace[self.ALLOWD_SCRIPT['python'][0]+pythonCommand+self.ALLOWD_SCRIPT['python'][1]] = newCode

        finalContent = ''
        i = 0
        for oldCode, newCode in toReplace.items():
            if i == 0:
                finalContent = oldContent.replace(oldCode, newCode)
            else:
                finalContent = finalContent.replace(oldCode, newCode)
            i += 1
        
        open(self.FILE_WATCHED, 'w').write(finalContent)

    def parseSql(self):
        oldContent = open(self.FILE_WATCHED, 'r').read()
        codes = re.findall(self.ALLOWD_SCRIPT['sql'][0]+'(.*?)'+self.ALLOWD_SCRIPT['sql'][1], oldContent, re.DOTALL)

        # if there is not sql codes
        if not codes:
            return

        # mysql connection
        cnx = mysql.connector.connect(user=self.MYSQL_LOGIN['login'], password=self.MYSQL_LOGIN['password'], host=self.MYSQL_LOGIN['host'], database=self.MYSQL_LOGIN['database'])
        cursor = cnx.cursor()

        toReplace = {}
        for code in codes:
            # executing the query
            query = (code)
            cursor.execute(query)

            res = '\n'.join([str(x[0]) for x in cursor])

            # init a dict to store what there is to replace in the file
            toReplace[self.ALLOWD_SCRIPT['sql'][0]+code+self.ALLOWD_SCRIPT['sql'][1]] = res

        finalContent = ''
        i = 0
        for oldCode, newCode in toReplace.items():
            if i == 0:
                finalContent = oldContent.replace(oldCode, newCode)
            else:
                finalContent = finalContent.replace(oldCode, newCode)
            i += 1
        
        open(self.FILE_WATCHED, 'w').write(finalContent)

        # deconnection
        cnx.commit()
        cursor.close()
        cnx.close()
        cnx.disconnect()

    def parseBash(self):
        oldContent = open(self.FILE_WATCHED, 'r').read()
        codes = re.findall(self.ALLOWD_SCRIPT['bash'][0]+'(.*?)'+self.ALLOWD_SCRIPT['bash'][1], oldContent, re.DOTALL)

        # if there is not bash codes
        if not codes:
            return

        toReplace = {}
        for code in codes:
            bashCommand = code

            process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
            output, error = process.communicate()

            # init a dict to store what there is to replace in the file
            toReplace[self.ALLOWD_SCRIPT['bash'][0]+code+self.ALLOWD_SCRIPT['bash'][1]] = output

        finalContent = ''
        i = 0
        for oldCode, newCode in toReplace.items():
            if i == 0:
                finalContent = oldContent.replace(oldCode, newCode)
            else:
                finalContent = finalContent.replace(oldCode, newCode)
            i += 1
        
        open(self.FILE_WATCHED, 'w').write(finalContent)

if __name__ == '__main__':
    try:
        SES(sys.argv[1])
    except Exception as e:
        print 'The script need a file to process'

