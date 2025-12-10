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
from wordpress_xmlrpc.methods import posts

# Your code here
url = "http://pressed.htb/xmlrpc.php"
username = "admin"
password = "uhc-jan-finals-2022"  # Or whatever password you have

client = Client(url, username, password)
plist = client.call(posts.GetPosts())

for post in plist:
    print(f"ID: {post.id}, Title: {post.title}, Date: {post.date}")

# Drop into interactive shell
print("\n" + "="*50)
print("Dropping into interactive shell...")
print("Client object is available as 'client'")
print("Type 'exit()' to quit")
print("="*50 + "\n")

import code
code.interact(local=locals())
