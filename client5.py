import metadisk,hashlib
# Get all registered public keys
(private_key, public_key) = metadisk.generate_new_key_pair()
print metadisk.authenticate(email='bigchobbit@gmail.com', password=hashlib.sha256(b'12345678').hexdigest())
#key_list = metadisk.public_keys.all()
#print key_list
# Add a key
#metadisk.public_keys.add(public_key)
# Remove one key
#metadisk.public_keys.remove(public_key)
# Remove all keys
#metadisk.public_keys.clear()
#print key_list
#notes - you will always need to auth the metadisk object
#new_bucket = metadisk.buckets.create(name='my first bucket')
#print new_bucket
bucketid="as"
listbuckets=metadisk.buckets.all()
for l in listbuckets:
	print l.id
	bucketid=l.id
new_bucket=metadisk.buckets.get(bucketid)
print "new bucket id \n",new_bucket.id,"\n \n list files ..."
l1= new_bucket.files.all()
print type(l1)
for fname in l1:
	print fname
#print new_bucket.files.upload('file.txt')
#	# 570c997da2ae841d2ea9798e
#Or a file handle
#	with open('/path/to/another/file.png') as file:
#   	another_bucket.files.upload(file)"""