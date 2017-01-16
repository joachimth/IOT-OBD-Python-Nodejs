import paho.mqtt.client as mqtt
import json
import ssl
import time
import random
import base64
import math
import os

tireValue = 0
oilLevelValue = 0
engineStatus = 0
doorStatus = 0
gearStatus = 0
troubleStatus = 0
fuelLvl = 0
coolantLvl = 0
currentWorkingDirectory = os.getcwd()
#This variable is used to determine if there is any change in the values.
# the data will be submitted to the MQTT only if there is a change
valueChanged = 0 

currentWorkingDirectory = os.getcwd()
# Connectivity information for Device's Stream
mqttBrokerHost = ""
mqttBrokerPort = 0

mqttBrokerUserName = ""
mqttBrokerPassword = ""
mqttClientId = ""
consumerTopic = "" # is the topic where remote commands are hosted for this device 
producerTopic = "" # will be the topic that device events should be published to
deviceID=""
eventID=""
Qos=0

def loadMqttPref():
    global mqttBrokerHost
    global mqttBrokerPort
    global mqttBrokerUserName
    global mqttBrokerPassword
    global mqttClientId
    global consumerTopic
    global producerTopic
    global deviceID
    global eventID
    global fuelLvl
    global coolantLvl

    mqttFileData = readFile("MQTTInfo.txt")
    jsonFileConent = json.loads(str(mqttFileData))
    mqttBrokerHost = jsonFileConent['host']
    mqttBrokerPort = jsonFileConent['port']
    mqttBrokerUserName = jsonFileConent['username']
    mqttBrokerPassword = jsonFileConent['password']
    mqttClientId = jsonFileConent['clientID']
    consumerTopic = jsonFileConent['consumerTopic']
    producerTopic = jsonFileConent['producerTopic']
    deviceID = jsonFileConent['deviceID']
    eventID = jsonFileConent['eventID']
    fuelLvl = jsonFileConent['fuelLvl']
    coolantLvl = jsonFileConent['coolantLvl']

def printMqttPref():
    print 'mqttBrokerHost: ' + mqttBrokerHost
    print 'mqttBrokerPort: ' + str(mqttBrokerPort)
    print 'mqttBrokerUserName: ' + mqttBrokerUserName
    print 'mqttBrokerPassword: ' + mqttBrokerPassword
    print 'mqttClientId: ' + mqttClientId
    print 'consumerTopic: ' + consumerTopic
    print 'producerTopic: ' + producerTopic
    print 'deviceID: ' + deviceID
    print 'eventID: ' + eventID
    print 'fuelLvl: ' + str(fuelLvl)
    print 'coolantLvl: ' + str(coolantLvl)

def random_message_id():
        _constantString = 'MQTTRPQA'
        _randomNumber = random.randrange(1, 1000000000) # At present range is kept 1 Billion numbers
        _messageId = _constantString+str(_randomNumber)
        return _messageId

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc):
    print("Connected with result code "+str(rc))

def prepare_message():
    _randomMessageId = random_message_id() # Generate Random messageID

    try:
        _eventMessage = "{\"tire\":" + str(tireValue) +",\"oilLevel\":" + str(oilLevelValue) +",\"gear\":" + str(gearStatus) +",\"trouble\":" + str(troubleStatus)+ ",\"Door\":" + str(doorStatus) +",\"Engine\":\"" + str(engineStatus)+ "\",\"FuelLevel\":" + str(fuelLvl) +",\"CoolantLevel\":" + str(coolantLvl)+ "}"
        #print ("Temp: ", temperature, " Humidity:  ", humidity)
        print ("eventmsg >> " + str(_eventMessage))
        encodedMsg = base64.b64encode(str(_eventMessage).encode())
        sendEventMessageObj = "{\"messageId\":\"" + str(_randomMessageId) + "\",\"deviceId\":\""+deviceID+"\",\"eventTemplateId\":\""+eventID+"\",\"message\":\"" + str(encodedMsg) + "\",\"encodingType\":\"base64\"}"
        print ("Whole payload >> " + str(sendEventMessageObj))
        return sendEventMessageObj
    except:
        return ""

def prepare_encodedMsg():
        print("About to send an event to covisint")
        publishMsg = prepare_message()
        #print("Message to be published >> "+str(publishMsg))
        return publishMsg

def readFile(fileName):
        #print("Read the file and load content")
        target=open(currentWorkingDirectory+"/"+fileName, 'r')
        return target.read()

loadMqttPref()
printMqttPref()
client = mqtt.Client(mqttClientId)
#Set userid and password
client.username_pw_set(mqttBrokerUserName, mqttBrokerPassword)
client.tls_set(currentWorkingDirectory+"/chained_prod_cert_covapp_io.pem.cer", certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1, ciphers=None)
client.on_connect = on_connect
client.connect(mqttBrokerHost, mqttBrokerPort, 30)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_start()

while True:
        try:
            fileContent = readFile("CmdStatus.txt")
#            print fileContent

            try:
                    jsonFileConent = json.loads(str(fileContent))
                    fileDoorValue = jsonFileConent['Door']
                    fileEngineValue = jsonFileConent['Engine']
                    fileTroubleValue = jsonFileConent['Trouble']
                    fileGearValue = jsonFileConent['Gear']
                    fileTireValue = jsonFileConent['Tire']
                    fileOilValue = jsonFileConent['Oil']

                    if engineStatus != fileEngineValue:
                            engineStatus = fileEngineValue
                            valueChanged = 1

                    if doorStatus != fileDoorValue:
                            doorStatus = fileDoorValue
                            valueChanged = 1

                    if troubleStatus != fileTroubleValue:
                            troubleStatus = fileTroubleValue
                            valueChanged = 1

                    if gearStatus != fileGearValue:
                            gearStatus = fileGearValue
                            valueChanged = 1

                    if tireValue != fileTireValue:
                            tireValue = fileTireValue
                            valueChanged = 1

                    if oilLevelValue != fileOilValue:
                            oilLevelValue = fileOilValue
                            valueChanged = 1
            except:
                    print "JSON read error. Continue..."

        except KeyboardInterrupt:
            # Stop the buzzer before stopping
            #digitalWrite(gearLed,0)
            #digitalWrite(troubleLed,0)
            client.loop_stop()
            break
        except (IOError,TypeError) as e:
            print "IO or Type Error" + e
            break

        if valueChanged == 1:
                print "Value changed. GearStatus:" + str(gearStatus) + " ,TroubleStatus:" + str(troubleStatus) + " ,TireValue:" + str(tireValue) + " ,OilLevel:" + str(oilLevelValue) + " ,Door:" + str(doorStatus) + " ,Engine:" + str(engineStatus)
                client.publish(producerTopic, str(prepare_encodedMsg()), Qos, retain=False)
                valueChanged = 0

