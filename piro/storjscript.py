import metadisk,pymongo,os,datetime,hashlib

def writetologs(strtowrite):
	dirpath=os.path.join(os.path.dirname(__file__),'static','logs')
	fileid=os.path.join(dirpath,"cronlogfile.txt")
	with open(fileid,"a") as myfile:
		myfile.write(strtowrite)

def main():
	print folderobj
	for listdir in folderobj:
		print listdir
		uploadapi(listdir['user']+"-"+listdir['date'])

def liststagingfiles():
	print "current directory \n",os.path.dirname(__file__)
	path1=os.path.dirname(__file__)
	dirpath=os.path.join(path1,'static','staging')
	retobj=[]
	for curdir,folders,files in os.walk(dirpath):
		print "iterating ",curdir,"\n",folders
		if len(folders)==0:
			#implies this is a end directory
			#means curdir is "*\staging\uname\date"
			#whatcomesafterlast"static\staging" and then split by \
			print "inside loop now"
			print "curdir",curdir,"pathsep",os.sep
			ind=curdir.index("static"+os.sep+"staging")
			indrest=len(curdir)-ind
			print "ind",ind,"indrest",indrest,"curdir len",len(curdir)
			print 15+ind,len(curdir)-15-ind
			#restdir=curdir[15+ind:len(curdir)-15-ind]
			restdir=curdir[-(len(curdir)-15-ind):]
			print "restdir",restdir
			if os.sep in restdir:
				uid=restdir.split(os.sep)[0]
				date=restdir.split(os.sep)[1]
				print "numfiles-",len(files)
				tempdict={'user':uid,'date':date,'numfiles':len(files)}
				retobj.append(tempdict)
				print "added",tempdict
	return retobj
#[{'date': '20010101', 'user': 'alex', 'numfiles': 9}, {'date': '20010102', 'user': 'alex', 'numfiles': 9}, {'date': '20010104', 'user': 'alex', 'numfiles': 5}]
#@app.route('/uploadapi/<userfolder>', methods=['GET', 'POST'])
def uploadapi(userfolder):
	uid=userfolder.split('-')[0]
	date=userfolder.split('-')[1]
	#returnobj=uploadfilestostorj(str(uid),str(date))
	#print "Object returned from upload api", returnobj
	returnobj=False
	if returnobj:
		writestorjtomongo(str(uid),str(date),returnobj['buckethash'],returnobj['filehash'])
	#return render_template('myfiles.html', files=str(returnobj))

def writestorjtomongo(userid,date,buckethash,filehash):
	print "inside write storj to mongo, writing to mongo now"
	print "userid,date,buckethash,filehash=",userid,date,buckethash,filehash
	writeobj={'userid':userid,'date':date,'buckethash':buckethash,'filehash':filehash}
	print "writeobj",writeobj
	storjHashesBefore = storjHashes.find({'userId': userid}).count()
	storjHashes.insert(writeobj)
	storjHashesAfter = storjHashes.find({'userId': userid}).count()
	response = 'Successfully inserted'

def uploadfilestostorj(userid,date1):
	print "current directory \n",os.path.dirname(__file__)
	date=str(date1)
	path1=os.path.dirname(__file__)
	dirpath=os.path.join(path1,'static','staging',str(userid),date)
	print "upload dir ----",dirpath
	filelist=os.listdir(str(dirpath))
	#the above line resolved the unicode tell issue..goddamn apparently the dirpath needs to be str then the listdir returns str
	print "file list",filelist
	bucketid=userid+date
	try:
		print "Creating Metadisk Bucket For "+userid+" and date "+date
		print metadisk.api_client.api_url
		new_bucket = metadisk.buckets.create(name=bucketid)
	except Exception as e:
		print "=====                    metadisk break                      ====","\n",e
	print "bucket created"
	print new_bucket,new_bucket.id
	returnobject={}
	returnobject['bucketid']=new_bucket.id
	print "returnobject",returnobject,"\n","writing to logs"
	writefile.writetologs("Bucket created "+new_bucket.id)
	returnobject['files']=[]
	#create metadisk text file
	for filename in filelist:
		fileid=os.path.join(dirpath,filename)
		#note the below line - you cant pass a file directly into api, pass the fpath instead
		#laso note documentation for python api maybe messy
		with open(fileid) as file1:
			#print "filetype",type(fileid)
			print "upload started...",fileid
			try:
				#hash1=new_bucket.files.upload(fileid)
				hash1=new_bucket.files.upload(fileid)#line 188 sdk.py
			except Exception as e:
				print "Exception for",fileid,e
				writetologs("Exception for "+fileid+str(e)+"\n")
				return False
			print "upload over",filename
			#returnobject['files'].append(hash1)
	print "-------uploaded all files to bucket-------"
	print "----now searching bucket for uploaded files----"
	listoffilesinbucket= new_bucket.files.all()
	#print type(listoffilesinbucket)
	for fname in listoffilesinbucket:
		if fname.name in filelist:
			tempdict1={'fileName': fname.name,'storjFileHash': fname.hash}
			returnobject['files'].append(tempdict1)
	print "---uploaded files----\n",returnobject
	allhashes=""
	retobj={}
	#writeMetaDiskToFile(returnobject)
	#for filehash in returnobject['files']:
		#allhashes=allhashes+filehash+"\n"
	print "---Creating Metadisk file---"
	print "---CONTENT for METADISK---\n",allhashes
	fileid=str(os.path.join(dirpath,"metadisk.txt"))
		#create metadisk
	with open(fileid,"a") as myfile:
		json.dump(returnobject['files'],myfile)
		#myfile.write(allhashes)
		#file auto closes-ready to upload
	print "---now uploading metadisk text file---"
	metahash=""
	try:
		metahash=new_bucket.files.upload(fileid)
	except Exception as e:
		print "Exception for",fileid,e
		writefile.writetologs("Exception for "+fileid+str(e)+"\n")
		print "Metadisk upload failed! Cancel PUSH TO storj"
		return False
	print "Metadisk successfully uploaded - ",metahash
	print "\n\n Listing uploaded files in bucket"
	l1= new_bucket.files.all()
	#print l1.name
	# retstring="Bucket ID = "+new_bucket.id
	for fname in l1:
		if ("metadisk" in fname.name):
			metahash=fname.hash
	print "metadisk hash is....",metahash
	retobj['filehash']=metahash
	retobj['buckethash']=returnobject['bucketid']
	return retobj

if __name__ == '__main__':
	writetologs("starting script at" + str(datetime.datetime.now()))
	metadisk.authenticate(email='bigchobbit@gmail.com', password=hashlib.sha256(b'12345678').hexdigest())
	client = pymongo.MongoClient()
	storjHashesDb = client.storjHashesDb
	storjHashes = storjHashesDb.storjHashes
	folderobj=liststagingfiles()
	main()