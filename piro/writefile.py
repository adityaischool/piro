import os

def writetologs(strtowrite):
	dirpath=os.path.join(os.path.dirname(__file__),'static','logs')
	fileid=os.path.join(dirpath,"logfile.txt")
	#create metadisk
	with open(fileid,"a") as myfile:
		myfile.write(strtowrite)

print "log writer loaded... "