#! /usr/bin/python

import os
import sys
from sys import argv
import time
import datetime
import re

class GitLogEntry :
	def __init__(self):
		self.commitId = ""
		self.author=""
		self.email=""
		self.fileChanged = 0
		self.lineInserted = 0
		self.lineDeleted = 0

class GitCommitAnalyzer : 
	def __init__(self) :
		self.commitNumByAuthor = {}
		self.pattern = re.compile(' (\d+).*, (\d+).*, (\d+).*')

	def getGitLog(self, analyzeDay) :
		''' get all git log of the git repo at the given git folder'''

		# fetch the git commit log
		today = datetime.date.today()
		delta = datetime.timedelta(days=analyzeDay)
		start = today - delta
		gitCommand="git log --since='{0}' --pretty=\"%h -- %an -- %ae\" --shortstat --no-merges > git.log".format(start.isoformat())
		os.system(gitCommand)
		print gitCommand

		logfile = open('git.log')
		i = 0
		logEntries = []
		checked = False
		for line in logfile:
			if checked == False :	
				if i == 0 : 
					if line.startswith('fatal: Not a git repository') :
						raise Error()
				checked = True
			if i == 0 :
				logEntry = GitLogEntry()
				result = line.split(' -- ')
				logEntry.commitId = result[0]
				logEntry.author = result[1]
				logEntry.email = result[2]
				logEntries.append(logEntry)
			# ignore second line
			elif i == 2:
				#print line
				result = self.pattern.match(line)
				if result == None :
					continue
				logEntry.fileChanged = int(result.group(1))
				logEntry.lineInserted = int(result.group(2))
				logEntry.lineDeleted = int(result.group(3))
			i = (i+1) % 3

		return logEntries

	def analysis(self, logEntries) :
		# print first
		for log in logEntries:
			#print "[%s - %s -- %s -- %s -- %s -- %s]" % (log.commitId, log.author, log.email, log.fileChanged, log.lineInserted, log.lineDeleted)
			pass

		for log in logEntries : 
			if log.author not in self.commitNumByAuthor :
				self.commitNumByAuthor[log.author] = 1
			else :
				count = self.commitNumByAuthor[log.author]
				self.commitNumByAuthor[log.author] = count+1
			pass

		for (k,v) in self.commitNumByAuthor.iteritems() :
			print k, v
		pass

day = 30
if len(argv) >= 1 :
	day = int(argv[1])
gca = GitCommitAnalyzer()
logs = gca.getGitLog(day)
gca.analysis(logs)


