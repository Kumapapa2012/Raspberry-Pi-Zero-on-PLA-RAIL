#!/usr/bin/env python3
###############################################################################
#
# Speech recognition
# based on oxford sample
# https://dev.projectoxford.ai/docs/services/54ef13cc3d8a4b06cc921a4a/operations/5518fde849c3f71a94aaf9d9
#
import http.client, urllib.request, urllib.parse, urllib.error
import base64, json, datetime, pyinotify
import logging, logging.handlers
import re, km_8830utils
import websocket
import time


###############################################################################
# These are from Azure portal
azure_key1 = '<Your Key1>'
azure_key2 = '<Your Key2>'

# Subscription(authentication) key
sbsckey_token=""
sbsckey_token_expireon=datetime.datetime.today()




###############################################################################
## Auth-key retrieval
##
## Header/Body to retrieve auth key

sbsckey_headers = {
    # Request headers
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': azure_key1
}

sbsckey_body = json.dumps({
	# grant_type=client_credentials&client_id=<AzureOffer>&client_secret=<Secret>&scope=https://speech.platform.bing.com
	'grant_type':'client_credentials',
	'client_id':azure_key1,
	'client_secret':azure_key2,
	'scope':'https://speech.platform.bing.com'
	})

## Function to retrieve token
def retrieve_token():
	# based on oxford sample
	try:
	    conn = http.client.HTTPSConnection('api.projectoxford.ai')
	    conn.request("POST", "/speech/v0/internalIssueToken", sbsckey_body, sbsckey_headers)
	    response = conn.getresponse()
	    data = response.read()
	    conn.close()
	    return json.loads(data.decode('utf-8'))
	except Exception as e:
	    logger.error("[Errno {0}] {1}".format(e.errno, e.strerror))


###############################################################################
## Speech Recognition
##
## Header/Query Params to retrieve auth key
stt_headers = {
    # Request headers
    'Content-Type': 'audio/wav;samplerate=16000',
    'Authorization': "",
    'X-Search-AppId': 'D4D5267291D74C748AD842B1D98141A5',
    'X-Search-ClientID': '1ECFAE91408841A480F00935DC390960',
    'maxnbest': '3',
    'User-Agent': 'KMORI_OXFORD_TEST'
}

stt_params = urllib.parse.urlencode({
	# from
	# https://www.microsoft.com/cognitive-services/en-us/speech-api/documentation/api-reference-rest/bingvoicerecognition
	'Version':'3.0', # Required
	'requestid': 'b2c95ede97eb4c8881e480f32d6aee54', # Copy but should be OK.
	'appID': 'D4D5267291D74C748AD842B1D98141A5', # Required
	'format': 'json', # Required
	'locale': 'ja-JP',
	'device.os': 'Linux 4.1.19+ #853 armv6l GNU/Linux',
	'scenarios': 'ulm',
	'instanceid': 'b2c95ede97eb4c8881e480f32d6a0ee5'
})

## Function to do stt
def do_speechToText(sndFile):
	global sbsckey_token_expireon, sbsckey_token
	try:
		if datetime.datetime.today()>=sbsckey_token_expireon:
			sbsckey_data=retrieve_token()
			sbsckey_token=sbsckey_data["access_token"]
			logger.debug(sbsckey_token)
			sbsckey_token_expireon=datetime.datetime.today()+datetime.timedelta(seconds=int(sbsckey_data["expires_in"]))
			logger.debug(sbsckey_token_expireon)
		
		logger.debug(sndFile)
		f = open(sndFile,'br')
		stt_body=f.read()
		f.close()

		stt_headers["Authorization"]=sbsckey_token
		
		conn = http.client.HTTPSConnection('speech.platform.bing.com')
		conn.request("POST", "/recognize/query?%s" % stt_params, stt_body, stt_headers)
		response = conn.getresponse()
		data = response.read()
		conn.close()
		return json.loads(data.decode('utf-8'))
	except KeyError as e:
		logger.debug("KeyError when trying to get subscription key.")
		logger.debug("Check if azure_key1/azure_key2 have valid values")
		return json.loads('{}')
	except Exception as e:
		logger.debug("[Errno {0}] {1}"% e.errno, e.strerror)
		return json.loads('{}')

# 
# sample stt result
#
# 	{
#	"version":"3.0",
#	"header":
#		{
#		"status":"success",
#		"scenario":"ulm",
#		"name":"こまれ",
#		"lexical":"こ ま れ",
#		"properties":
#			{
#			"requestid":"c2057d98-191c-4c0c-8b6a-f71f502c9c91",
#			"HIGHCONF":"1"
#			}
#		},
#	"results":
#		[
#			{
#			"scenario":"ulm",
#			"name":"こまれ",
#			"lexical":"こ ま れ",
#			"confidence":"0.6773676",
#			"properties":
#				{
#				"HIGHCONF":"1"
#				}
#			}
#		]
#	}
#


def controlTrain(result):
	# Stt Matching 
	stt_run= {"走","発車","はし"}
	stt_stop= {"止","停車","とま"}
	if ("results" in result):
		for res in result["results"]:
			if ("name" in res):
				recText=str(res["name"])
				logger.debug(recText)
				for key_run in stt_run:
					try:
						recText.index(key_run)
						r_motor=km_8830utils.Set8830Status(1.6,"Forward")
						logger.debug(r_motor)
					except:
						# do nothing
						trainCmd=""
						
				for key_stop in stt_stop:
					try:
						recText.index(key_stop)
						r_motor=km_8830utils.Set8830Status(0.0,"Brake")
						logger.debug(r_motor)
					except:
						# do nothing
						trainCmd=""
			else:
				logger.debug("Faulty JSON message")
				logger.debug(res)
				
# 電車のコントロールに Web Socket 10502 を使用するように変更
#          ws.send(
#            JSON.stringify({
#            type: 'change',
#            value: msg --> 0-100 までの整数
#            })
#
#  "{\"type\":\"change\",\"value\":82}"
#
def controlTrain2(result):
	global ws
	# Stt Matching 
	stt_run= {"走","発車","はし"}
	stt_stop= {"止","停車","とま"}
	if ("results" in result):
		for res in result["results"]:
			if ("name" in res):
				recText=str(res["name"])
				logger.debug(recText)
				for key_run in stt_run:
					try:
						# 加速は２段階,最高 80%
						recText.index(key_run) 
						ws.send("{\"type\":\"change\",\"value\":50}")
						time.sleep(0.3)
						ws.send("{\"type\":\"change\",\"value\":80}")

					except BrokenPipeError:
						ws = websocket.create_connection("ws://localhost:10502")
						ws.send("{\"type\":\"change\",\"value\":0}")
					except ValueError:
						logger.debug("No match")
					except Exception as e:
						logger.debug(str(type(e)))
						logger.debug(e.message)
						
				for key_stop in stt_stop:
					try:
						recText.index(key_stop)
						ws.send("{\"type\":\"change\",\"value\":0}")

					except BrokenPipeError:
						ws = websocket.create_connection("ws://localhost:10502")
						ws.send("{\"type\":\"change\",\"value\":0}")
					except ValueError:
						logger.debug("No match")
					except Exception as e:
						logger.debug(str(type(e)))
						logger.debug(e.message)
			else:
				logger.debug("Faulty JSON message")
				logger.debug(res)
				
		
#
# Main
#

## initializing logging
# Setting logging level
#
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

#出力のフォーマットを定義
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

#ログファイルを容量でローテーションするハンドラーを定義
rfh = logging.handlers.RotatingFileHandler(
    filename='/home/pi/logs/stt_log.txt',
    maxBytes=10240000, # 10MB
    backupCount=3
)

rfh.setLevel(logging.DEBUG)
rfh.setFormatter(formatter)

#rootロガーにハンドラーを登録する
logger.addHandler(rfh)

wm = pyinotify.WatchManager()  # Watch Manager
mask = pyinotify.IN_CREATE | pyinotify.IN_CLOSE_WRITE # watched events
watch_dir = '/home/pi/sox_temp'

# 電車のコントロールに Web Socket 10502 を使用するように変更
#          ws.send(
#            JSON.stringify({
#            type: 'change',
#            value: msg --> 0-100 までの整数
#            })
#
#  "{\"type\":\"change\",\"value\":82}"

websocket.enableTrace(True)
ws = websocket.create_connection("ws://localhost:10502")

class EventHandler(pyinotify.ProcessEvent):
	def process_IN_CLOSE_WRITE(self, event):
		logger.debug("Wrote and Closed %s"%event.pathname)
		result=do_speechToText(event.pathname)
		logger.debug(result)
		# Here, call action(s)
#		controlTrain(result)
		controlTrain2(result)

notifier = pyinotify.Notifier(wm, EventHandler())
wdd = wm.add_watch(watch_dir, mask, rec=False)
notifier.loop()

