Chanarchive
===========

This is a small project I've been working on that takes 4chan pages and archives them. It stores ALL the data (including images, which is inadvisable) in MongoDB.

It's currently configured to run on Heroku and as such, should be able to run just about anywhere. 

Disclaimer: It looks like crap.

Requirements
============

If you're deploying to Heroku, the main things you need are:

- The Mongolab addon (or you can use another MongoDB provider (yourself) and set the MONGOLAB\_URI variable. I'm working on fixing that eventually.)
- The New Relic addon. This is mainly a development thing but I haven't fixed the code to support not having it yet. That will be coming soon.

Then all you (should) need to do is clone it, run 
  
  heroku create <You app name here>
  git push heroku master

and Heroku should take care of all the rest ^.^ You may need to run

  heroku ps:scale web=1

to get it running actually...

