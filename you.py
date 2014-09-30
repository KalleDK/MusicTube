#!/usr/bin/env python
import sys, getopt, ConfigParser, re, youtube_dl, os, subprocess
from mutagen.easymp4 import EasyMP4
from mutagen.mp4 import MP4, MP4Cover

cfg = ConfigParser.ConfigParser()
cfg.read('you.conf')

jobs = ConfigParser.ConfigParser()
jobs.read(cfg.get('SETTINGS','WORKDIR') + '/jobs/jobs')

class Job:
	artist = ''
	title = ''
	id = ''
	albumartist = ''
	album = ''
	status = ''
	info = {}
	def __init__(self, id):
		self.id = id
		self.title = jobs.get(id, 'TITLE')
		self.artist = jobs.get(id, 'ARTIST')
		self.albumartist = jobs.get(id, 'ALBUMARTIST')
		self.album = jobs.get(id, 'ALBUM')
		self.status = jobs.get(id, 'STATUS')
	def postname(self):
		p = re.compile('[^A-Za-z0-9._-]')
		return p.sub('_', self.artist + " - " + self.title + ".mp4")
	
def listJobs():
	print 'Jobs in queue'
	print
	for job in jobs.sections():
		j = Job(job)
		print 'ID:		' + job
		print 'Title:		' + jobs.get(job, 'TITLE')
		print 'Artist:		' + jobs.get(job, 'ARTIST')
		print 'AlbumArtist:	' + jobs.get(job, 'ALBUMARTIST')
		print 'Album:		' + jobs.get(job, 'ALBUM')
		print 'Status:		' + jobs.get(job, 'STATUS')
		print 'Postname:	' + j.postname()
		print

def printHelp():
	print 'Usage: ', sys.argv[0]
	print
	print 'Options:'
	print	'	-a Add Job'
	print '	-h	Help'
	print '	-p	Print Jobs'

def getJobFromUser():
	j = Job()
	j.id = raw_input("Youtube ID: ")
	j.title = raw_input("Title: ")
	j.artist = raw_input("Artist: ")
	j.albumartist = raw_input("Albumartist: ")
	if j.albumartist == '':
		j.albumartist = j.artist
	j.album = raw_input("Album: ")
	if j.album == '':
		j.album = j.title
	return j
	
def downloadJob(id):
	j = Job(id)
	print "Downloading: " + j.id
	settings = {}
	##settings['simulate'] = 'True'
	settings['outtmpl'] = cfg.get('SETTINGS','WORKDIR') + '/raw/%(id)s.%(ext)s'
	settings['format'] = '22/35/18/34/6/5/17/13'
	settings['writethumbnail'] = 'True'
	y = youtube_dl.YoutubeDL(settings)
	y.add_default_info_extractors()
	j.info = y.extract_info(j.id, download=False)
	##print j.info['format_id']
	y.download([j.id])
	j.status = "DOWNLOADED"
	convertJob(j)

def tagJob(j):
	os.rename(cfg.get('SETTINGS','WORKDIR') + '/converted/' + j.id + '.mp4', cfg.get('SETTINGS','WORKDIR') + '/tagged/' + j.id + '.mp4')
	os.rename(cfg.get('SETTINGS','WORKDIR') + '/converted/' + j.id + '.jpg', cfg.get('SETTINGS','WORKDIR') + '/tagged/' + j.id + '.jpg')
	video =  EasyMP4(cfg.get('SETTINGS','WORKDIR') + '/tagged/' + j.id + '.mp4')
	video.tags['title'] = unicode(j.title)
	video.tags['artist'] = unicode(j.artist)
	video.tags['albumartist'] = unicode(j.albumartist)
	video.tags['album'] = unicode(j.album)
	video.tags['comment'] = unicode(j.id)
	video.save()
	video =  MP4(cfg.get('SETTINGS','WORKDIR') + '/tagged/' + j.id + '.mp4')
	data = open(cfg.get('SETTINGS','WORKDIR') + '/tagged/' + j.id + '.jpg', 'rb').read()
	covr = []
	covr.append(MP4Cover(data,MP4Cover.FORMAT_JPEG))
	video.tags['covr'] = covr
	video.save()
	os.remove(cfg.get('SETTINGS','WORKDIR') + '/tagged/' + j.id + '.jpg')
	renameJob(j)
	
	
def convertJob(j):
	mp4_formats = ["18", "22", "37", "38", "82", "83", "84", "85"]
	if j.info['format_id'] in mp4_formats:
		os.rename(cfg.get('SETTINGS','WORKDIR') + '/raw/' + j.id + '.mp4', cfg.get('SETTINGS','WORKDIR') + '/converted/' + j.id + '.mp4')
		os.rename(cfg.get('SETTINGS','WORKDIR') + '/raw/' + j.id + '.jpg', cfg.get('SETTINGS','WORKDIR') + '/converted/' + j.id + '.jpg')
	tagJob(j)
	
def renameJob(j):
	os.rename(cfg.get('SETTINGS','WORKDIR') + '/tagged/' + j.id + '.mp4', cfg.get('SETTINGS','WORKDIR') + '/completed/' + j.postname())

def downloadJobs():
	pid = str(os.getpid())
	pidfile = "/tmp/you.pid"
	if os.path.isfile(pidfile):
		print "%s already exists, exiting" % pidfile
		sys.exit()
	else:
		file(pidfile, 'w').write(pid)
	missing = True
	while missing:
		missing = False
		jobs.read(cfg.get('SETTINGS','WORKDIR') + '/jobs/jobs')
		for id in jobs.sections():
			if jobs.get(id, 'STATUS') == 'ADDED':
				missing = True
				downloadJob(id)
				jobs.set(id, 'STATUS', 'COMPLETED')
				with open(cfg.get('SETTINGS','WORKDIR') + '/jobs/jobs', 'wb') as configfile:
					jobs.write(configfile)
	os.unlink(pidfile)
	
	
def addJob(j):
	jobs.add_section(j.id)
	jobs.set(j.id, 'TITLE', j.title)
	jobs.set(j.id, 'ARTIST', j.artist)
	jobs.set(j.id, 'ALBUM', j.album)
	jobs.set(j.id, 'ALBUMARTIST', j.albumartist)
	jobs.set(j.id, 'STATUS', 'ADDED')
	
	with open(cfg.get('SETTINGS','WORKDIR') + '/jobs', 'wb') as configfile:
		jobs.write(configfile)
		
def main(argv):
	try:
		opts, args = getopt.getopt(argv,"apdsh")
	except getopt.GetoptError:
		printHelp()
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			printHelp()
			sys.exit()
		if opt == '-p':
			listJobs()
			sys.exit()
		if opt == '-a':
			addJob(getJobFromUser())
			sys.exit()
		if opt == '-s':
			pidfile = "/tmp/you.pid"
			if os.path.isfile(pidfile):
				print "%s already exists, exiting" % pidfile
				sys.exit()
			else:
				subprocess.call( ["screen", "-d", "-m", "-S", "you", "you.py", "-d"] )
				sys.exit()
		if opt == '-d':
			downloadJobs()
			sys.exit()
			
if __name__ == "__main__":
	main(sys.argv[1:])

