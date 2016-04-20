
import json
def storj_fetch_file_given_hash(storj_hash):
    # call storj api for file download


# Input: compact disk object
# Output: Images on the disk
def fetch_images_on_disk(compact_disk_object):
    full_stroj_hash = compact_disk_object['storjHash']
    full_disk_object = storj_fetch_file_given_hash(full_stroj_hash)
    image_list = list()
    
