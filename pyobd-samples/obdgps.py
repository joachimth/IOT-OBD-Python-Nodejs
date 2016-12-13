import paho.mqtt.client as mqtt
import json
import ssl
import time
import random
import base64
import obd
import time
import os
import serial

ser = serial.Serial('/dev/ttyUSB0', 4800, timeout = 5)


# Connectivity information for Device's Stream
mqttBrokerHost = "mqtt.covapp.io"
mqttBrokerPort = 8883
mqttBrokerUserName = "2203ee82-2ab3-4d6e-9084-13092e84ccb9"
mqttBrokerPassword = "5cbd7256-a0c8-4d44-a07c-d5c62ce9420d"
mqttClientId = "97dF9ED7468e4a9b9743"
client = mqtt.Client(mqttClientId)
currentWorkingDirectory = os.getcwd()

# Message processing information
consumerTopic = "9f0d78b0-1d8f-4d75-8ad9-eb54fef8a234" # is the topic where remote commands are hosted for this device
producerTopic = "9da9a847-db38-4a93-b4b7-e44a262dce77" # will be the topic that device events should be published to
Qos=0
def latDD(x):
  D = int(x[1:3])
  M = int(x[3:5])
  S = float(x[5:])
  DD = D + float(M)/60 + float(S)/3600
  return DD
def longDD(x):
  D = int(x[1:4])
  M = int(x[4:6])
  S = float(x[6:])
  DD = D + float(M)/60 + float(S)/3600
  return DD

def random_message_id():
        """This method is used to generate a random message id for the device for audit purpose.

        :rtype: string messageid

        """
        _constantString = 'MQTTRPQA'
        _randomNumber = random.randrange(1, 1000000000) # At present range is kept 1 Billion numbers
        _messageId = _constantString+str(_randomNumber)
        return _messageId

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc):
    print("Connected with result code "+str(rc))


def queryobdandsendtocloud():
   r = connection.query(obd.commands.RPM)
   print "engine rpm="+str(r)
   r2 = connection.query(obd.commands.FUEL_PRESSURE)
   print "fuel pressure="+str(r2)
   r3 = connection.query(obd.commands.GET_DTC)
   print "dtccod="+str(r3)
   r4 = connection.query(obd.commands.FUEL_LEVEL)
   print "fuel leve="+str(r4)
   r5= connection.query(obd.commands.COOLANT_TEMP)
   print "engine coolant tem="+str(r5)
   r6=connection.query(obd.commands.SPEED)
   # r6 ="40 KPH"
   # r="1200"
   # r5="48.5c"
   # r2="130KP"
   # r4="70%"
   # r3="p0108"
   print "vehicle spped="+str(r6)
   line = ser.readline()
   splitline = line.split(',')
   if splitline[0] == '$GPGGA':
         latsub=""
         longsub="" 
         latitude = splitline[3]+ splitline[2]
         latDirec = splitline[3]
         if latDirec == "S":
            latsub = "-"
         # print "latitude="+str(latitude)
         latdec = latsub+str(latDD(latitude))
         print latdec
         longitude = splitline[5]+ splitline[4]
         #longdec = longDD(longitude)
         #print longdec
         #print "longitude="+longitude
         longDirect = splitline[5]
         if longDirect == "W":
            longsub = "-"
         #print "longitude direction="+longDirect
         longdec = longsub+str(longDD(longitude))
         print longdec
         f = open("test.txt","a") #opens file with name of "test.txt"
         f.write(latdec)
         f.write(longdec)
         print line
 
   _eventMessage =  "{\"Speed\":\""+str(r6)+"\",\"EngineRpm\":\""+str(r)+"\",\"EngineTemp\":\"" + str(r5)+"\",\"FuelPressure\":\"" + str(r2)+"\",\"FuelLevel\":\"" + str(r4)+"\",\"GETDTC\":\"" + str(r3)+"\"}"
   print ("eventmsg >> " + str(_eventMessage))
   encodedMsg = base64.b64encode(str(_eventMessage).encode())
   _randomMessageId = random_message_id()   
   sendEventMessageObj = "{\"messageId\":\"" + str(_randomMessageId) + "\",\"deviceId\":\"95de7ed5-6669-4142-9842-ac63a03bfae3\",\"eventTemplateId\":\"605ed280-82b5-4c3d-8057-71712394f0a6\",\"message\":\"" + str(encodedMsg) + "\",\"encodingType\":\"base64\"}"
   print ("wholepayload >> " + str(sendEventMessageObj))
   client.publish(producerTopic, str(sendEventMessageObj), Qos, retain=False)



#obd.logger.setLevel(obd.logging.DEBUG)
connection = obd.OBD(portstr='/dev/ttyUSB1', baudrate=38400, protocol=None, fast=True)
#print connection.protocol_name()
#print connection.status()


#Set userid and password
client.username_pw_set(mqttBrokerUserName, mqttBrokerPassword)
#print(currentWorkingDirectory)
certFilePath = str(currentWorkingDirectory) + "/chained_prod_cert_covapp_io.pem.cer"
#print(certFilePath)

client.tls_set(certFilePath, certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1, ciphers=None)
client.on_connect = on_connect
client.connect(mqttBrokerHost, mqttBrokerPort, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_start()
#queryobdandsendtocloud()
while True:
   try:
      queryobdandsendtocloud()
      print ("about to sleep for 5 sec \n")
      time.sleep(5)
   except KeyboardInterrupt:
      client.loop_stop()
      break
