import requests
import os
import datetime
import json
import time
from google.cloud import storage






def upload_blob(storage_client, bucket_name, destination_blob_name, content):
    """Uploads a string to a bucket. can create new 'folders' as it goes."""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"
    # The path to your file to upload
    # source_file_name = "local/path/to/file"
    # The ID of your GCS object
    # destination_blob_name = "storage-object-name"

    #storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    # Optional: set a generation-match precondition to avoid potential race conditions
    # and data corruptions. The request to upload is aborted if the object's
    # generation number does not match your precondition. For a destination
    # object that does not yet exist, set the if_generation_match precondition to 0.
    # If the destination object already exists in your bucket, set instead a
    # generation-match precondition using its generation number.
    #generation_match_precondition = 0
    try:
      blob.upload_from_string(content)
    except Exception as e:
      exstring = "an error occured while uploading a blob to " + destination_blob_name + " " + e + "\n" 
      print(exstring)
      return exstring
    return ''



def main(request):
  # load env vars
  SECRET = os.environ.get('NOTION_KEY').__str__()
  storage_client = storage.Client()
  bucket_name = "notionbackups"
  exlist = ''
  
  timestamp = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
  folder = 'notionbackup_' + timestamp
  



  headers = {
    'Authorization': 'Bearer '+ SECRET,
    'Notion-Version': '2022-06-28',
    'Content-Type': 'application/json',
  }
  print("requesting from notion...")
  response = requests.post('https://api.notion.com/v1/search', headers=headers, data = '{}')    
  

  print("uploading...")
  for block in response.json()['results']:

    upload_blob(storage_client, bucket_name, bucket_name + f'/{folder}/{block["id"]}.json',json.dumps(block))
    print("blob uploaded.")
    try:
      child_blocks = requests.get(
        f'https://api.notion.com/v1/blocks/{block["id"]}/children',
        headers=headers,
      )
      if child_blocks.json()['results']:
        for child in child_blocks.json()['results']:
          exlist = exlist + upload_blob(storage_client, bucket_name, bucket_name + f'/{folder}/{block["id"]}/{child["id"]}.json',json.dumps(child))
          print("child blob uploaded.")
    except Exception as e:
      exstring = "an error occurred getting children: " + e + "\n" 
      print(exstring)
      exlist = exlist + exstring
    

  if(exlist == ''):
    return ('', 200)
  else:
    return(exlist, 500)


