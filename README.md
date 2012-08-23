Chanarchive
===========

This is a small project I've been working on that takes 4chan pages and archives them. It stores ALL the data (including images, which is inadvisable) in MongoDB.

It's currently configured to run on Heroku and as such, should be able to run just about anywhere. 

Disclaimer: It looks like crap.

Requirements
============

Heroku
------

If you're deploying to Heroku, the main things you need are:

- The Mongolab addon (or you can use another MongoDB provider (yourself) and set the MONGOLAB\_URI variable. I'm working on fixing that eventually.)
- The New Relic addon. This is mainly a development thing but I haven't fixed the code to support not having it yet. That will be coming soon.

Then all you (should) need to do is clone it, run 
  
  ```heroku create <You app name here>
  git push heroku master```

and Heroku should take care of all the rest ^.^ You may need to run ```heroku ps:scale web=1``` to get it running actually...

Elsewhere
---------

If you're deploying elsewhere you'll need:

- Python 2.7 (I think. It's what I used for this project but it may be compatible with 3)
- Pip
- Virtualenv is always a good idea.
- A MongoDB database to store things in.

Then you'll need to install the Python dependencies (should be a simple matter of ```pip install -r requirements.txt```) and configure the environment variables. (See below)

Configuration
=============

If you can read Python (it's pretty easy) you can just have a look in the Charchive/BServer2.py file to see the configuration. Otherwise, read ahead!

Environment Variables:

- MONGOLAB_URI (this will be renamed later, most likely to MONGO_URI): This is a uri of the form ```mongodb://<username>:<password>@<host>:<port>/<database name>```. It's what the application connects to. At the moment, ALL DATA IS STORED HERE. That includes images. Which are big. Default is ```mongodb://localhost:27017```. Not sure if works...
- HOST: Host to listen on. Default is ```0.0.0.0```
- PORT: Port to listen on. Defaukt is ```5000```
- HOSTNAME: Hostname to use for URLs. At the moment, all URLs are relative so this isn't used at all. Default: ```localhost```
- TEMPLATEDIR: Directory to get templates from (this way themes will eventually be possible). Default: ```Templates```
- CACHEDIR: Directory to cache templates in (not used). Default: ```Cache```
- STATICDIR: Directory for Bottle to serve static files from. Default: ```/app/Static``` (this is an absolute path and this particular directory is standard on Heroku)
