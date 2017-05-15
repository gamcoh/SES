# coding: utf8

import re
from cStringIO import StringIO
import sys
import ast
from pprint import pprint

class SES:
	ALLOWD_SCRIPT={
		'python': ('@@begin-python', '@@end-python', 'self.parsePython')
	}
	FILE_WATCHED=''

	def __init__(self, file):
		self.FILE_WATCHED=file
		self.parsePython()

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


if __name__ == '__main__':
	SES('example.txt')

