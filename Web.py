#Author: Lucas Cooper
#Creation date: 01/06/2011
#Function: Runs the server in the Server module and handles configuration.
#Changelog:

#01/06/2011: Added this comment block.
#19/06/2011: Added a full screen gallery based on Galleria.
#20/06/2011: Migrated everything into modules for easier extension/interface.

import Charchive.BServer2 as BServer2
import os

relickey = os.getenv('NEW_RELIC_LICENSE_KEY', 0)

if relickey:
    import newrelic.agent

#server = Server({'cherryPyConf':'/home/lucas/Dev/Python/Chanarchive/Config/CherryPy.cfg'})
#BServer2.start()
application = BServer2.app

if relickey:
    application = newrelic.agent.wsgi_application()(application)
