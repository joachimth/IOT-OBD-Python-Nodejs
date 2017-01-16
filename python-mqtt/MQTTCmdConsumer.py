#!/usr/bin/env python

from Beacon import Beacon
import BLEScanner
import bluetooth._bluetooth as bluez

import paho.mqtt.client as mqtt
#import RPi.GPIO as GPIO
import json
import ssl
import os
import time
import threading
import datetime
import grovepi
from grovepi import *

currentWorkingDirectory = os.getcwd()
# Connectivity information for Device's Stream
mqttBrokerHost = ""
mqttBrokerPort = 0

mqttBrokerUserName = ""
mqttBrokerPassword = ""
mqttClientId = ""
consumerTopic = "" # is the topic where remote commands are hosted for this device 

# Driver Smart key fob device info
dev_id = 0
isDriverNearby=0
isDriverInAccessZone=0
driverDeviceAddress='E3:0B:27:06:90:94'

#Potentiometer connected to port A2 and A1
oilLvlSensor = 1  #min:0 max:1022
tireSensor = 2  #min:0 max:1022

# Our Pi will have an LED on Pin 7 and 8
troubleLed = 5
gearLed = 6
doorLed = 7
engineLed = 8

troubleButton   = 3		#Port for troubleButton
gearButton      = 4		#Port for gearButton

pinMode(troubleLed,"OUTPUT")
pinMode(gearLed,"OUTPUT")
pinMode(doorLed,"OUTPUT")
pinMode(engineLed,"OUTPUT")
pinMode(gearButton,"INPUT")	# Assign mode for gearButton as input
pinMode(troubleButton,"INPUT")	# Assign mode for troubleButton as input

tireValue = 0
oilLevelValue = 0
gearStatus=0
troubleStatus = 0
doorStatus=0
engineStatus = 0

gearButtonStatus = 0
troubleButtonStatus = 0

valueChanged = 0
gearPressTimer = 0
troublePressTimer = 0

digitalWrite(doorLed,0)
digitalWrite(engineLed,0)

def loadMqttPref():
    global mqttBrokerHost
    global mqttBrokerPort
    global mqttBrokerUserName
    global mqttBrokerPassword
    global mqttClientId
    global consumerTopic
    mqttFileData = readFile("MQTTInfo.txt")
    jsonFileConent = json.loads(str(mqttFileData))
    mqttBrokerHost = jsonFileConent['host']
    mqttBrokerPort = jsonFileConent['port']
    mqttBrokerUserName = jsonFileConent['username']
    mqttBrokerPassword = jsonFileConent['password']
    mqttClientId = jsonFileConent['clientID']
    consumerTopic = jsonFileConent['consumerTopic']

def printMqttPref():
    print 'mqttBrokerHost: ' + mqttBrokerHost
    print 'mqttBrokerPort: ' + str(mqttBrokerPort)
    print 'mqttBrokerUserName: ' + mqttBrokerUserName
    print 'mqttBrokerPassword: ' + mqttBrokerPassword
    print 'mqttClientId: ' + mqttClientId
    print 'consumerTopic: ' + consumerTopic
    
def writeFile(doorSt, engineSt, troubleSt, gearSt, tireSt, oilSt):
        target=open(currentWorkingDirectory+"/CmdStatus.txt", 'w')
        target.truncate()
        target.write('{"Door":"'+doorSt+'","Engine":"'+engineSt+'","Trouble":"'+troubleSt+'","Gear":"'+gearSt+'","Tire":"'+tireSt+'","Oil":"'+oilSt+'"}')
        target.close()

def readFile(fileName):
        print("Read the file and load content")
        target=open(currentWorkingDirectory+"/"+fileName, 'r')
        return target.read()

loadMqttPref()
printMqttPref()
    
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    print "subscribing to " + consumerTopic
    client.subscribe(str(consumerTopic))
    print "Subscription successful."

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
        fileContent = readFile("CmdStatus.txt")
#        print fileContent
        jsonFileConent = json.loads(str(fileContent))
        doorValue = jsonFileConent['Door']
        engineValue = jsonFileConent['Engine']
        gearValue = jsonFileConent['Gear']
        troubleValue = jsonFileConent['Trouble']
        
	commandMsg = json.loads(str(msg.payload))
#	print "Encrypted message: " + str(commandMsg)
#	print "Encrypted message: " + str(commandMsg['message'])
	decodedCommandMessage = json.loads(commandMsg['message'].decode('base64')) 
	print "got a message -> " + str(decodedCommandMessage) + " @ " + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
#	print decodedCommandMessage['Door']
#	print decodedCommandMessage['Engine']

        gearCmd="2"
        troubleCmd="2"
        honkCmd="2"
        flashCmd="2"
        getStatusCmd="2"

        try:
            gearCmd = decodedCommandMessage['Gear']
        except:
            print "Gear cmd input error"

        try:
            troubleCmd = decodedCommandMessage['Trouble']
        except:
            print "Trouble cmd input error"

        try:
            honkCmd = decodedCommandMessage['Honk']
        except:
            print "Honk cmd input error"

        try:
            flashCmd = decodedCommandMessage['Flash']
        except:
            print "Flash cmd input error"

        try:
            getStatusCmd = decodedCommandMessage['GetStatus']
        except:
            print "GetStatus cmd input error"

	audioFilePath='None'

	#indicating that the program will be using the global value for these variables
        global gearStatus
        global troubleStatus
        global doorStatus
        global engineStatus
        global tireValue
        global oilLevelValue

#       processing logic for incoming commands
        if troubleCmd == "1":
                #digitalWrite(troubleLed,1)
                troubleValue="1"
                troubleStatus=1
        if troubleCmd == "0":
                #digitalWrite(troubleLed,0)
                troubleValue="0"
                troubleStatus=0
        if gearCmd == "1":
                #digitalWrite(gearLed,1)
                gearValue="1"
                gearStatus=1
        if gearCmd == "0":
                #digitalWrite(gearLed,0)
                gearValue="0"
                gearStatus=0
        if decodedCommandMessage['Door'] == "1":
                digitalWrite(doorLed,1)
                doorValue="1"
                doorStatus=1
                audioFilePath="Unlock32k3sec.mp3"
        if decodedCommandMessage['Door'] == "0":
                digitalWrite(doorLed,0)
                doorValue="0"
                doorStatus=0
                audioFilePath="Lock32k3sec.mp3"
        if decodedCommandMessage['Engine'] == "0":
                digitalWrite(engineLed,0)
                engineValue="0"
                engineStatus=0
        if decodedCommandMessage['Engine'] == "1":
                digitalWrite(engineLed,1)
                engineValue="1"
                engineStatus=1
                audioFilePath="Start32k6sec.mp3"
        if honkCmd == "1":
                # Just play the honk sound for Honk command
                audioFilePath="Horn32k4sec.mp3"
        if flashCmd == "1":
                # Flash the engine&door leds
                processFlashCmd(doorValue, engineValue)
        if getStatusCmd == "1":
            oilLevelValue = oilLevelValue-1
        writeFile(doorValue, engineValue, troubleValue, gearValue, str(tireValue), str(oilLevelValue))
        background=AsyncAidioPlayer(audioFilePath)
        background.start()
        #threading.Thread(target=playCorrectSound(audioFilePath)).start() # start the audio in a new thread so that the other message can be processes immediately
        #playCorrectSound(audioFilePath)
        print "Gear Status:" + str(gearStatus) + " Trouble Status:" + str(troubleStatus)
        
class AsyncAidioPlayer(threading.Thread):
    def __init__(self, filePath):
        threading.Thread.__init__(self)
        self.audioFilePath=filePath
    def run(self):
        if self.audioFilePath!='None':
            print "Starting player -> " + self.audioFilePath
            os.system('omxplayer ' + self.audioFilePath)
            print "Play sound done!!!"

def processFlashCmd(doorValue, engineValue):
    print "   Process Flash Command. Initial doorValue:"+doorValue+" ,engineValue:"+engineValue
    counter = 0
    while counter<3:
        try:
            digitalWrite(doorLed,1)
            digitalWrite(engineLed,1)
            time.sleep(.5)  #Sleep for half second
            digitalWrite(doorLed,0)
            digitalWrite(engineLed,0)
            time.sleep(.5)
        except IOError:
            print "Cought Flash Error. Handled Gracefully!"
        counter += 1
    #Reset the Led status to its original value
    digitalWrite(doorLed,int(doorValue))
    digitalWrite(engineLed,int(engineValue))
    print "   Done flash command!"

def processDriverWelcome():
    print "Start driver welcome process: " + getTimestamp()
    fileContent = readFile("CmdStatus.txt")
    #print fileContent
    jsonFileConent = json.loads(str(fileContent))
    doorValue = jsonFileConent['Door']
    engineValue = jsonFileConent['Engine']
    processFlashCmd(doorValue, engineValue)
    print "Done driver welcome!"

def performPEPSLockUnlock(doorValue):
    global gearStatus
    global troubleStatus
    global doorStatus
    global engineStatus
    global tireValue
    global oilLevelValue
    print "Start PEPS lock/unlock operation: " + getTimestamp()
    digitalWrite(doorLed, doorValue)
    writeFile(str(doorValue), str(engineStatus), str(troubleStatus), str(gearStatus), str(tireValue), str(oilLevelValue))
    print "Lock/Unlock Operation finished!"

def getTimestamp():
    return " @ " + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

client = mqtt.Client(mqttClientId)
print ("mqtt Client")
#Set userid and password
client.username_pw_set(mqttBrokerUserName, mqttBrokerPassword)
print ("mqtt Broker")
client.tls_set("/home/pi/ConnectedVehicle/chained_prod_cert_covapp_io.pem.cer", certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1, ciphers=None)
client.on_connect = on_connect
print ("on connect")
client.on_message = on_message
print ("on message")
client.connect(mqttBrokerHost, mqttBrokerPort, 30)
print ("broker connect")
# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
#client.loop_forever()
client.loop_start()
print ("past loop")

try:
    sock = bluez.hci_open_dev(dev_id)
    print ("ble thread started")
except Exception, err:
    print ("Error accessing bluetooth device on PI.", err)
    sys.exit(1)

BLEScanner.hci_le_set_scan_parameters(sock)
BLEScanner.hci_enable_le_scan(sock)

while True:
    print "\n-------------"
    try:
        # Logic to figure out if the Driver is in Welcome/Access Zone of the vehicle.
        returnedList = BLEScanner.parse_events(sock, 10) #return 10 items everytime
        isDriverBLEFound=0

        for Beacon in returnedList:
            if Beacon.macAddr.upper()==driverDeviceAddress.upper():
                print ("Driver Near: " + str(isDriverNearby) + " Beacon: " + Beacon.macAddr.upper() + "        " + str(Beacon.rssi[0]))
                if Beacon.rssi[0]>-75: #Driver in Welcome Zone
                    if isDriverNearby==0 or isDriverInAccessZone==0:
                        if Beacon.rssi[0]>-50:
                            print "Driver in ACCESS Zone: " + getTimestamp()
                            performPEPSLockUnlock(1) # Perform UnLock
                            doorStatus=1
                            valueChanged=1
                            isDriverInAccessZone=1
                        elif isDriverNearby==0:
                            print "Driver in WELCOME Zone: " + getTimestamp()
                            processDriverWelcome()
                            isDriverInAccessZone=0
                        #valueChanged=1
                        isDriverNearby=1
                    isDriverBLEFound=1
                    deviceDisconnectTimer=time.time() # reset the disconnect timer

        if isDriverBLEFound == 0 and isDriverNearby==1:
            if time.time() > deviceDisconnectTimer+10: # consider disconnected only if the BLE beacon is away for straight 5 seconds
                print ("\t\t Driver went away from vehicle: " + getTimestamp())
                valueChanged=1
                isDriverNearby=0
                isDriverInAccessZone=0
                doorStatus=0
                performPEPSLockUnlock(0) # Perform Lock
        
        _tirePressure = analogRead(tireSensor)
        _oilLevel = analogRead(oilLvlSensor)

        _tirePressure = _tirePressure/15
        _oilLevel = _oilLevel/11

        if _tirePressure<=75 and (_tirePressure>tireValue+1 or _tirePressure<tireValue-1):
                tireValue = _tirePressure
                valueChanged = 1

        if _oilLevel<=100 and _oilLevel>oilLevelValue+1 or _oilLevel<oilLevelValue-1:
                oilLevelValue = _oilLevel
                valueChanged = 1
        
        if gearStatus == 0:
            digitalWrite(gearLed,0)						
        else:
            digitalWrite(gearLed,1)

        if troubleStatus == 0:
            digitalWrite(troubleLed,0)						
        else:
            digitalWrite(troubleLed,1)

        gearButton_status= digitalRead(gearButton)	        #Read the gearButton status
        troubleButton_status= digitalRead(troubleButton)	#Read the troubleButton status

        if gearButton_status:	#gearButton is in HIGH position
            print "gearButton"
            if gearButtonStatus == 0:
                #Consider the button press only if the we read 2 consecutive reads
                gearPressTimer += 1
                
                print "gearButton clicked->" + str(gearPressTimer)
                if gearPressTimer>1:
                    valueChanged = 1
                    if gearStatus == 0:
                        gearStatus = 1						
                    else:
                        gearStatus = 0
                    gearButtonStatus = 1
        else:		#gearButton is in Off position
            gearButtonStatus = 0
            gearPressTimer = 0

        if troubleButton_status:	#troubleButton is in HIGH position
            print "troubleButton"
            if troubleButtonStatus == 0:
                #Consider the button press only if the we read 2 consecutive reads
                troublePressTimer += 1
                print "troubleButton clicked->" + str(troublePressTimer)
                if troublePressTimer>1:
                    valueChanged = 1
                    if troubleStatus == 0:
                        troubleStatus = 1						
                    else:
                        troubleStatus = 0
                    troubleButtonStatus = 1
        else:		#gearButton is in Off position
            troubleButtonStatus = 0
            troublePressTimer = 0

    except KeyboardInterrupt:
        # Stop the buzzer before stopping
        digitalWrite(gearLed,0)
        digitalWrite(troubleLed,0)
        client.loop_stop()
        break

    except (IOError,TypeError) as e:
        print "IO or Type Error"

    if valueChanged == 1:
        print "Value changed: " + '{"tire:"' + str(tireValue) +'","oilLevel":"' + str(oilLevelValue) +'",Door":"'+str(doorStatus)+'","Engine":"'+str(engineStatus)+'","Trouble":"'+str(troubleStatus)+'","Gear":"'+str(gearStatus)+'"}'
        writeFile(str(doorStatus), str(engineStatus), str(troubleStatus), str(gearStatus), str(tireValue), str(oilLevelValue))
        valueChanged = 0
        
