#! /opt/local/bin/python
# coding: utf8

import re
from cStringIO import StringIO
import sys
from os import path
import subprocess

class SES:
	ALLOWD_SCRIPT={
		'python': ('@@begin-python', '@@end-python', 'self.parsePython'),
		'sql': ('@@begin-sql', '@@end-sql', 'self.parseSql'),
		'bash': ('@@begin-bash', '@@end-bash', 'self.parseBash')
	}
	FILE_WATCHED=''

	def __init__(self, file):
		if not path.exists(file):
			print 'Error could not get the file: '+file
			sys.exit(1)

		self.FILE_WATCHED=file
		content = open(file, 'r').read()
		
		# find if there is a python script
		if re.findall(self.ALLOWD_SCRIPT['python'][0]+'.*'+self.ALLOWD_SCRIPT['python'][1], content, re.DOTALL):
			self.parsePython()

		# find if there is a sql script
		if re.findall(self.ALLOWD_SCRIPT['sql'][0]+'.*'+self.ALLOWD_SCRIPT['sql'][1], content, re.DOTALL):
			self.parseSql()

		# find if there is a bash script
		if re.findall(self.ALLOWD_SCRIPT['bash'][0]+'.*'+self.ALLOWD_SCRIPT['bash'][1], content, re.DOTALL):
			self.parseBash()

	def parsePython(self):
		content = open(self.FILE_WATCHED, 'r').read()
		code = re.findall(self.ALLOWD_SCRIPT['python'][0]+'(.*)'+self.ALLOWD_SCRIPT['python'][1], content, re.DOTALL)

		if not code:
			return

		# getting the stdout
		old_stdout = sys.stdout
		sys.stdout = mystdout = StringIO()

		# exec the code from the file
		exec code[0]
		newCode = mystdout.getvalue()

		# reset stdout
		sys.stdout = old_stdout
		content = content.replace(self.ALLOWD_SCRIPT['python'][0]+code[0]+self.ALLOWD_SCRIPT['python'][1], newCode)
		newFile = open(self.FILE_WATCHED, 'w').write(content)

	def parseSql(self):
		print 'sql'

	def parseBash(self):
		content = open(self.FILE_WATCHED, 'r').read()
		code = re.findall(self.ALLOWD_SCRIPT['bash'][0]+'(.*)'+self.ALLOWD_SCRIPT['bash'][1], content, re.DOTALL)

		if not code:
			return

		bashCommand = code[0]
		
		process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
		output, error = process.communicate()
		content = content.replace(self.ALLOWD_SCRIPT['bash'][0]+code[0]+self.ALLOWD_SCRIPT['bash'][1], output)
		newFile = open(self.FILE_WATCHED, 'w').write(content)

if __name__ == '__main__':
	try:
		SES(sys.argv[1])
	except Exception as e:
		print 'The script need a file to process'

