# Plus.io - GAE API

Plus.io Restful Interface for Google App Engine (This code is still in Beta)


## Collections ##


Using App Engine you are able to store the data from your mobile application on Google Datastore.


The following routes allow you to interact with data from the collections.  
  
  


**Specify a Collection**

    https://(app engine url)/collections/(collection name)
  

The server will respond with a list of all of the data within the specified collection.
  


**Insert into a Collection**

    https://(app engine url)/collections/(collection name)
  

You can post to the same url that you use to get the data from a collection. Each request should have a timestamp in the time key. If the collection you want to post into doesn't exsist it will be created for you. 

    {
    	"Column" : "Value",
    	"Time" : "1371614094"
    }



## Items ##





