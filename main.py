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
import webapp2
import json
import urllib2



###     Define Structure model by default                ###



currentcollection = "Structure"

class Structure(db.Model):
    rows = db.StringProperty()

class CustomCollection(db.Expando):
    time = db.StringProperty()
    @classmethod
    def kind(self):
        return "%s" % currentcollection



###     When you view the webpage from the internet      ###



class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write("%s({" % urllib2.unquote(self.request.get('callback')))
        self.response.out.write("'Status':'Good'")
        self.response.write('})')



###     Retrive and insert data in the main Structure      ###



class Struc(webapp2.RequestHandler):
    # Get rows from the structure kind by specifying a key_name
    def get(self, key):
        dbdata = Structure.get_by_key_name(key)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.loads(dbdata.rows))

    # Insert row list into the structure kind
    def post(self, key):
        data = json.loads(self.request.body)
        s = Structure(key_name = data["key"], rows = json.dumps(data["rows"]))
        s.put()



class Base(webapp2.RequestHandler):
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


class BaseProps(webapp2.RequestHandler):
    # Get rows from the structure kind by specifying a key_name
    def get(self, collection):

        global currentcollection
        currentcollection = collection.lower()
        c = CustomCollection()
        c.kind()
        r = c.all().count()

        m = metadata.get_properties_of_kind(collection)
        arr = {}
        full = []
        count = 0
        for n in m:
            arr[count] = n
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
        global currentcollection
        currentcollection = collection.lower()
        c = CustomCollection()
        c.kind()
        n = c.all()
        b = metadata.get_properties_of_kind(collection.lower())
        arr = []
        for g in n:
            results = {}
            results["id"] = g.key().id()
            for a in b:
                results[a] = getattr(g,a)
            arr.append(results)

        # RESPONSE === BEGIN #
        self.response.out.write("%s(" % urllib2.unquote(self.request.get('callback')))
        self.response.out.write(json.dumps(arr))
        self.response.out.write(")")
        # RESPONSE === END #
    
    # Insert data into a specified collection

    def post(self, collection):
        data=json.loads(self.request.body)
        global currentcollection
        currentcollection = collection.lower()
        c = CustomCollection()
        c.kind()  
        for (x,y) in data["content"].iteritems():
            setattr(c,x,y)
        c.put()

        # RESPONSE === BEGIN #
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write('collection %s : PUT' % collection)
        # RESPONSE === END #



###     Get data from a collection based on an ID value      ###



class ItemData(webapp2.RequestHandler):
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
                arr[a.lower()] = getattr(g, a)

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
    webapp2.Route(r'/structure/', Base),
    webapp2.Route(r'/structure/<collection:\w+>/', BaseProps),
    webapp2.Route(r'/structure/old/<key:\w+>/', Struc),
    webapp2.Route(r'/collection/<collection:\w+>/', Collection),
    webapp2.Route(r'/collection/<collection:\w+>/<item:\w+>/', ItemData)
], debug = True)







