#!/usr/bin/env python
#
#
# === Citizenhub Code License ==================================
#
#
#   Author : AJ Rahim @ Citizenhub
#   Support : open.plus.io/+docs
#
#
# Copyright 2013 Citizenhub, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
#
#
# === Google Code License ======================================
#
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.



###     Import necessary libraries                    ###



from webapp2_extras import routes
from google.appengine.ext import db
from google.appengine.ext.db import metadata
from google.appengine.ext.db import Key
from google.appengine.ext.db.metadata import Kind
from google.appengine.api.runtime import runtime
from google.appengine.api import oauth

import os
import cloudstorage
import webapp2
import json
import urllib2



###     Define Structure model by default                ###


currentcollection = "Structure"


class CustomCollection(db.Expando):
    time = db.StringProperty()
    @classmethod
    def kind(self):
        return "%s" % currentcollection


###     When you view the webpage from the internet      ###


class MainHandler(webapp2.RequestHandler):
    def get(self):
        pass


###     Get information on the app engine app itself (To Be Expanded)     ###


class AppInfo(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("%s({" % urllib2.unquote(self.request.get('callback')))
        self.response.out.write("'cpu_usage':'%s'," % runtime.cpu_usage())
        self.response.out.write("})")


###     Getting data from Google Cloud Storage / Allow user to delete files from Cloud Storage     ###

class Bucket(webapp2.RequestHandler):
    def get(self, bucket):
        self.response.out.write("%s([" % urllib2.unquote(self.request.get('callback')))
        stats = cloudstorage.listbucket('/%s' % bucket)
        count = 0
        for stat in stats:
            count += 1
            self.response.write("{'file' : \"%s\"}," % stat.filename)
        self.response.out.write("])")
    def delete(self, bucket):
        if self.request.get("file") != "":
            try:
                cloudstorage.delete(self.request.get("file"))
            except cloudstorage.NotFoundError:
                pass
        else:
            pass


###     Retrive and insert data in the main Structure      ###

class Structure(webapp2.RequestHandler):

    # Get rows from the structure kind by specifying a key_name

    def get(self):
        m = metadata.get_kinds()
        arr = {}
        count = 0
        for n in m:
            if n.startswith("_"):
                pass
            else:
                arr[count] = n
                count += 1

        # RESPONSE === BEGIN #
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write("%s(" % urllib2.unquote(self.request.get('callback')))
        self.response.out.write(json.dumps(arr))
        self.response.out.write(")")
        # RESPONSE === END #


class StructureKey(webapp2.RequestHandler):

    # Get rows from the structure kind by specifying a key_name

    def get(self, collection):

        global currentcollection
        currentcollection = collection.lower()
        c = CustomCollection()

        c.kind()
        n = c.all()

        if self.request.get("filter") != "":
            n.filter("%s" % self.request.get("filter"), "%s" %  self.request.get("value").replace(' ', '_'))
        else:
            pass

        if self.request.get("offset") != "":
            fil = n.fetch(int(self.request.get("limit")), int(self.request.get("offset")))
        elif self.request.get("limit") != "":
            fil = n.fetch(int(self.request.get("limit")))
        else:
            fil = n

        r = fil.count()

        m = metadata.get_properties_of_kind(collection.lower())
        arr = {}
        full = []
        count = 0
        for ab in m:
            arr[count] = ab
            count += 1
        arr[count] = "id"
        full.append(arr)
        string = {}
        string["count"] = r
        full.append(string)

        # RESPONSE === BEGIN #
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write("%s(" % urllib2.unquote(self.request.get('callback')))
        self.response.out.write(json.dumps(full))
        self.response.out.write(")")
        # RESPONSE === END #
        

###     Retrive and insert data in a specified Collection      ###

class Collection(webapp2.RequestHandler):
    
    # Get a list from a specified collection

    def get(self, collection):
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        global currentcollection
        currentcollection = collection.lower()
        c = CustomCollection()
        c.kind()
        n = c.all()

        if self.request.get("filter") != "":
            n.filter("%s" % self.request.get("filter"), "%s" %  self.request.get("value").replace(' ', '_'))
        else:
            pass

        if self.request.get("offset") != "":
            fil = n.fetch(int(self.request.get("limit")), int(self.request.get("offset")))
        elif self.request.get("limit") != "":
            fil = n.fetch(int(self.request.get("limit")))
        else:
            fil = n

        b = metadata.get_properties_of_kind(collection.lower())
        arr = []

        for g in fil:
            results = {}
            results["id"] = g.key().id()
            for a in b:
                try:
                    results[a] = getattr(g,a)
                except:
                    pass

            arr.append(results)

        # RESPONSE === BEGIN #
        self.response.out.write("%s(" % urllib2.unquote(self.request.get('callback')))
        self.response.out.write(json.dumps(arr))
        self.response.out.write(")")
        # RESPONSE === END #
    
    # Insert data into a specified collection

    def post(self, collection):
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        content = json.loads(self.request.body)
        global currentcollection
        currentcollection = collection.lower()
        c = CustomCollection()
        c.kind()  

        for (x,y) in content.iteritems():
            setattr(c,x,y)

        c.put()

        # RESPONSE === BEGIN #
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write('collection %s : PUT' % collection)
        # RESPONSE === END #

###     Get data from a collection based on an ID value      ###

class CollectionItem(webapp2.RequestHandler):

    def get(self, collection, item):
        global currentcollection
        currentcollection = collection.lower()
        c = CustomCollection()
        c.kind()
        n = c.all().filter("__key__ =", db.Key.from_path(collection, int(item)))
        b = metadata.get_properties_of_kind(collection.lower())
        arr = {}

        for g in n:
            for a in b:
                try:
                    arr[a.lower()] = getattr(g,a)
                except:
                    pass

        # RESPONSE === BEGIN #
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write("%s(" % urllib2.unquote(self.request.get('callback')))
        self.response.out.write(json.dumps(arr))
        self.response.out.write(")")
        # RESPONSE === END #

    def post(self, collection, item):
        content = json.loads(self.request.body)
        global currentcollection
        currentcollection = collection.lower()
        c = CustomCollection()
        c.kind()
        n = c.all().filter("__key__ =", db.Key.from_path(collection, int(item)))

        for g in n:
            for (x,y) in content.iteritems():
                setattr(g,x.lower(),y)
            g.put()

    def delete(self, collection, item):
        global currentcollection
        currentcollection = collection.lower()
        c = CustomCollection()
        c.kind()
        n = c.all().filter("__key__ =", db.Key.from_path(collection, int(item)))
        db.delete(n)

        # RESPONSE === BEGIN #
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write("%s(" % urllib2.unquote(self.request.get('callback')))
        self.response.out.write("{'delete':'successful'}")
        self.response.out.write(")")
        # RESPONSE === END #



###     App Engine routes                                        ###



app = webapp2.WSGIApplication([
    webapp2.Route(r'/', MainHandler),
    webapp2.Route(r'/app', AppInfo),
    webapp2.Route(r'/structure', Structure),
    webapp2.Route(r'/structure/<collection:\w+>', StructureKey),
    webapp2.Route(r'/collection/<collection:\w+>', Collection),
    webapp2.Route(r'/collection/<collection:\w+>/<item:\w+>', CollectionItem),
    webapp2.Route(r'/bucket/<bucket:\w+>', Bucket)
], debug = True)







