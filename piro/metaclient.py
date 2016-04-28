import metadisk,hashlib,os,writefile,json
print " \n           ===building metadisk client===            "
print metadisk.authenticate(email='bigchobbit@gmail.com', password=hashlib.sha256(b'12345678').hexdigest())
def returnfiles():
	bucketid="as"
	listbuckets=metadisk.buckets.all()
	for l in listbuckets:
		print l.id
		bucketid=l.id
	new_bucket=metadisk.buckets.get(bucketid)
	print "new bucket id \n",new_bucket.id,"\n \n list files ..."
	l1= new_bucket.files.all()
	#print l1.name
	retstring="Bucket ID = "+new_bucket.id
	for fname in l1:
		print fname.name,fname.size,fname.hash
		retstring=retstring+" "+fname.name+" Size= "+str(fname.size)+" Bytes ...Hash = "+fname.hash
	print "returnstring \n", retstring
	return retstring
#print new_bucket.files.upload('file.txt')
#	# 570c997da2ae841d2ea9798e
#Or a file handle
#	with open('/path/to/another/file.png') as file:
#   	another_bucket.files.upload(file)"""

def gethashidformetadiskid():
	return "TBD"

def storefiles(bucketid,filepath):
	#every capsule raw file will be inside a folder within staging
	#staging/usernamedate
	#Usage: Pass in the bucket name and directory of file staging
	#Will return a hash id for the (metadisk file on storj)
	print "current directory \n",os.path.dirname(__file__)
	path1=os.path.dirname(__file__)
	#path2=filepath
	dirpath=os.path.join(path1,'static','staging',filepath)
	filelist=os.listdir(dirpath)
	print "file list",filelist
	#return "logs"
	#return filelist
	bucketid=filepath
	#new_bucket=metadisk.buckets.get(bucketid)
	new_bucket = metadisk.buckets.create(name=bucketid)
	print "bucket created"
	print new_bucket,new_bucket.id
	#new_bucket=metadisk.buckets.get('570c997da2ae841d2ea9798e')
	#print "bucket"
	#print new_bucket
	returnobject={}
	returnobject['bucketid']=new_bucket.id
	writefile.writetologs("Bucket created "+new_bucket.id)
	returnobject['files']=[]
	#create metadisk text file
	for filename in filelist:
		fileid=os.path.join(dirpath,filename)
		#note the below line - you cant pass a file directly into api, pass the fpath instead
		#laso note documentation for python api maybe messy
		with open(fileid) as file1:
			print "upload started...",fileid
			print "filetype",type(fileid)
			try:
				#hash1=new_bucket.files.upload(fileid)
				hash1=new_bucket.files.upload(fileid)#line 188 sdk.py
			except Exception as e:
				print "Exception for",fileid,e
				writefile.writetologs("Exception for "+fileid+str(e)+"\n")
			print "upload over",filename
			#returnobject['files'].append(hash1)
	listoffilesinbucket= new_bucket.files.all()
	print type(listoffilesinbucket)
	for fname in listoffilesinbucket:
		if fname.name in filename:
			returnobject['files'].append(fname.hash)
	print returnobject
	allhashes=""
	#writeMetaDiskToFile(returnobject)
	for filehash in returnobject['files']:
		allhashes=allhashes+filehash+"\n"
	fileid=os.path.join(dirpath,"metadisk.txt")
		#create metadisk
	with open(fileid,"a") as myfile:
		myfile.write(allhashes)
		#file auto closes-ready to upload
	print "now uploading metadisk text file"
	new_bucket.files.upload(fileid)
	return returnobject

def viewfilesinbucket(bucketid):
	new_bucket=metadisk.buckets.get(bucketid)
	listoffilesinbucket= new_bucket.files.all()
	print "list",listoffilesinbucket
	returnobject={}
	returnobject['files']=[]
	for fname in listoffilesinbucket:
		returnobject['files'].append(fname)
	return returnobject


def deletebucket(bucketid):
	return metadisk.buckets.delete(bucket_id=bucketid)

def returnbuckets():
	bucketid="as"
	returnobj=[]
	listbuckets=metadisk.buckets.all()
	for l in listbuckets:
		tempbucket={}
		tempbucket['bucketid']=l.id
		tempbucket['files']=[]
		print "getting bucket="+l.id
		new_bucket=metadisk.buckets.get(l.id)
		l1= new_bucket.files.all()
		print "files="+str(len(l1))
		for fname in l1:
			filedata={}
			filedata['name']=fname.name
			filedata['size']=fname.size
			filedata['hash']=fname.hash
			tempbucket['files'].append(filedata)
		returnobj.append(tempbucket)
	return returnobj
def getadmindata():
	returnobj=returnbuckets()
	return returnobj

def storefilesinbucket(bucketid,filepath):
	path1=os.path.dirname(__file__)
	dirpath=os.path.join(path1,'static','staging',filepath)
	filelist=os.listdir(dirpath)
	print "file list",filelist
	#bucketid=filepath
	new_bucket=metadisk.buckets.get(bucketid)
	#new_bucket = metadisk.buckets.create(name=bucketid)
	print "bucket created"
	print new_bucket,new_bucket.id
	returnobject={}
	returnobject['bucketid']=new_bucket.id
	writefile.writetologs("Bucket created "+new_bucket.id)
	returnobject['files']=[]
	#create metadisk text file
	for filename in filelist:
		fileid=os.path.join(dirpath,filename)
		#note the below line - you cant pass a file directly into api, pass the fpath instead
		#laso note documentation for python api maybe messy
		with open(fileid) as file1:
			print "upload started...",fileid
			try:
				hash1=new_bucket.files.upload(fileid)
			except Exception as e:
				print "Exception for",fileid,e
				writefile.writetologs("Exception for "+fileid+str(e)+"\n")
			print "upload over",filename
			#returnobject['files'].append(hash1)
	listoffilesinbucket= new_bucket.files.all()
	print type(listoffilesinbucket)
	for fname in listoffilesinbucket:
		if fname.name in filename:
			returnobject['files'].append(fname.hash)
	print returnobject
	allhashes=""
	#writeMetaDiskToFile(returnobject)
	for filehash in returnobject['files']:
		allhashes=allhashes+filehash+"\n"
	fileid=os.path.join(dirpath,"metadisk.txt")
		#create metadisk
	with open(fileid,"a") as myfile:
		myfile.write(allhashes)
		#file auto closes-ready to upload
	print "now uploading metadisk text file"
	new_bucket.files.upload(fileid)
	return returnobject


def storefileswithtoken(bucketid,filepath):
	path1=os.path.dirname(__file__)
	dirpath=os.path.join(path1,'static','staging',filepath)
	filelist=os.listdir(dirpath)
	print "file list",filelist
	#bucketid=filepath
	new_bucket=metadisk.buckets.get(bucketid)
	push_token = new_bucket.tokens.create(operation='PUSH')
	#new_bucket = metadisk.buckets.create(name=bucketid)
	print "bucket created"
	print new_bucket,new_bucket.id
	returnobject={}
	returnobject['bucketid']=new_bucket.id
	writefile.writetologs("Bucket created "+new_bucket.id)
	returnobject['files']=[]
	#create metadisk text file
	for filename in filelist:
		fileid=os.path.join(dirpath,filename)
		#note the below line - you cant pass a file directly into api, pass the fpath instead
		#laso note documentation for python api maybe messy
		with open(fileid) as file1:
			print "upload started...",fileid
			try:
				hash1=new_bucket.files.upload(fileid)
			except Exception as e:
				print "Exception for",fileid,e
				writefile.writetologs("Exception for "+fileid+str(e)+"\n")
			print "upload over",filename
			#returnobject['files'].append(hash1)
	listoffilesinbucket= new_bucket.files.all()
	print type(listoffilesinbucket)
	for fname in listoffilesinbucket:
		if fname.name in filename:
			returnobject['files'].append(fname.hash)
	print returnobject
	allhashes=""
	#writeMetaDiskToFile(returnobject)
	for filehash in returnobject['files']:
		allhashes=allhashes+filehash+"\n"
	fileid=os.path.join(dirpath,"metadisk.txt")
		#create metadisk
	with open(fileid,"a") as myfile:
		myfile.write(allhashes)
		#file auto closes-ready to upload
	print "now uploading metadisk text file"
	new_bucket.files.upload(fileid)
	return returnobject

def storefilesapi(userid,date1):
	print "current directory \n",os.path.dirname(__file__)
	date=str(date1)
	path1=os.path.dirname(__file__)
	dirpath=os.path.join(path1,'static','staging',str(userid),date)
	print "upload dir ----",dirpath
	filelist=os.listdir(str(dirpath))
	#the above line resolved the unicode tell issue..goddamn apparently the dirpath needs to be str then the listdir returns str
	print "file list",filelist
	print type(filelist)
	bucketid=userid+date
	#new_bucket=metadisk.buckets.get(bucketid)
	try:
		print "Creating Metadisk Bucket For "+userid+" and date "+date
		print metadisk.api_client.api_url
		new_bucket = metadisk.buckets.create(name=bucketid)
	except Exception as e:
		print "=====                    metadisk break                      ====","\n",e
	print "bucket created"
	print new_bucket,new_bucket.id
	#new_bucket=metadisk.buckets.get('570c997da2ae841d2ea9798e')
	#print "bucket"
	#print new_bucket
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
				writefile.writetologs("Exception for "+fileid+str(e)+"\n")
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

def liststagingfiles():
	#every capsule raw file will be inside a folder within staging
	#staging/usernamedate
	#Usage: Pass in the bucket name and directory of file staging
	#Will return a hash id for the (metadisk file on storj)
	print "current directory \n",os.path.dirname(__file__)
	path1=os.path.dirname(__file__)
	# #path2=filepath
	dirpath=os.path.join(path1,'static','staging')
	# filelist=os.listdir(dirpath)
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
