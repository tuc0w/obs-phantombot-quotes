#!/usr/bin/python
"""
@package		phantombot-quotes
@version:		0.0.1-alpha
@description	This script gathers all quotes from PhantomBot and updates a specified text source with a randomly ch0sen one.
@author:		@tuc0w
@twitch:		https://twitch.tv/tuc0w
@twitter:		https://twitter.com/tuc0w
@instagram:		https://instagram.com/tuc0w
"""

import obspython as obs
import websockets
import asyncio
import json
import random

url				= ""
port			= 25004
interval		= 30
source_name		= ""
oauth       	= ""
data			= {}
reveived_data	= False

# ------------------------------------------------------------

async def update_data():
	global url
	global port
	global oauth
	global data

	async with websockets.connect(url + ":" + str(port)) as websocket:
		auth = {"authenticate": oauth}
		getQuotes = {"dbkeys": "quotes_quotes", "query": {"table": "quotes"}}
		await websocket.send(str(auth))
		await websocket.send(str(getQuotes))
		data = await websocket.recv()
		websocket.close()
		# data["results"]
		# [
		#	{'table': 'quotes', 'key': '0', 'value': '["zweikuh","Uff!","1508158957669","South Park: The Stick of Truth"]'},
		#	{'table': 'quotes', 'key': '1', 'value': '["tuc0w","test 1 2 3",1508160694463,"South Park: The Stick of Truth"]'}
		# ]

def update_text():
	global source_name
	global data
	global reveived_data

	source = obs.obs_get_source_by_name(source_name)
	if source is not None:
		try:
			if reveived_data == False:
				asyncio.get_event_loop().run_until_complete(update_data())
			results = json.loads(data)
			choice = random.choice(results['results'])
			quote = choice['value'].split(",")
			text = str(quote[1])
			settings = obs.obs_data_create()
			obs.obs_data_set_string(settings, "text", text)
			obs.obs_source_update(source, settings)
			obs.obs_data_release(settings)

		except:
			obs.script_log(obs.LOG_WARNING, "Error opening " + url + ":" + str(port))
			obs.remove_current_callback()
			pass
		reveived_data = True
		obs.obs_source_release(source)

def refresh_pressed(props, prop):
	update_text()

# ------------------------------------------------------------

def script_description():
	return "Gathers all quotes from PhantomBot and updates a chosen text source with a randomly ch0sen one.\n\nBy tuc0w\nhttps://twitch.tv/tuc0w\nhttps://twitter.com/tuc0w\nhttps://instagram.com/tuc0w"

def script_update(settings):
	global url
	global port
	global interval
	global source_name
	global oauth

	url         = obs.obs_data_get_string(settings, "url")
	port        = obs.obs_data_get_string(settings, "port")
	interval    = obs.obs_data_get_int(settings, "interval")
	source_name = obs.obs_data_get_string(settings, "source")
	oauth       = obs.obs_data_get_string(settings, "oauth")

	obs.timer_remove(update_text)

	if url != "" and source_name != "":
		obs.timer_add(update_text, interval * 1000)

def script_defaults(settings):
	obs.obs_data_set_default_int(settings, "interval", 30)

def script_properties():
	props = obs.obs_properties_create()

	obs.obs_properties_add_text(props, "url", "URL", obs.OBS_TEXT_DEFAULT)
	obs.obs_properties_add_text(props, "port", "Port", obs.OBS_TEXT_DEFAULT)
	obs.obs_properties_add_text(props, "oauth", "OAuth", obs.OBS_TEXT_DEFAULT)
	obs.obs_properties_add_int(props, "interval", "Update Interval (seconds)", 5, 3600, 1)

	p = obs.obs_properties_add_list(props, "source", "Text Source", obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
	sources = obs.obs_enum_sources()
	if sources is not None:
		for source in sources:
			source_id = obs.obs_source_get_id(source)
			if source_id == "text_gdiplus" or source_id == "text_ft2_source":
				name = obs.obs_source_get_name(source)
				obs.obs_property_list_add_string(p, name, name)

		obs.source_list_release(sources)

	obs.obs_properties_add_button(props, "button", "Refresh", refresh_pressed)
	return props
