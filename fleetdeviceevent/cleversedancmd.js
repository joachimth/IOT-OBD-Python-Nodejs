var mqtt    = require('mqtt');

var client;
var deviceId = "42ba1baf-d13c-4efc-9668-7558c51b9a81";
var consumerTopic = '02ff4736-3b2d-4452-b2cc-da2ee38db366';
var producerTopic = '84142a4a-b376-4e71-bda8-0c7e89f1c891';
var appcommandID = '039e88d7-1026-4121-a928-d171d90bae72';
var statestatus = '1';
var strMsg = {State:statestatus};

function setupMQTT() {
/*ESTABLISH MQTT CONNECTION*/
client = mqtt.connect('ssl://mqtt.covapp.io:8883',
            {
                  keepalive: 10, 
                  clientId: '8515a5D4889D40059E12',
                  clean: true,
                  protocolId: 'MQTT',
                  connectTimeout: 30 * 1000,
                  username: '757f7257-993f-4fc0-81ad-b6d8df3c23b9',
                  password: '062bed4c-711f-4f01-95c7-f0641c40352f'            });

client.on('connect', function () {
            console.log('MQTT Connection Successful');
            client.subscribe(consumerTopic);
            console.log('MQTT subscription complete');
            //publishMessage(stateChangeEventID, 'Anuj Tyagi');
      });

client.on('message', function (topic, message) {
            // message is Buffer 
            //console.log(message.toString());
            var jsonStatusObj = JSON.parse(message.toString());
            var decodedPayload = new Buffer(jsonStatusObj.message, 'base64');
            //console.log("DeviceID: %s Payload: %s", jsonStatusObj.deviceId, decodedPayload.toString());
            

        });  

publishMessage(JSON.stringify(strMsg));
console.log("Continous Gulcose Moniotor");        
}


function publishMessage(msgToPublish){
      //console.log('Publishing message: ' + msgToPublish);
      var encodedMsg = (new Buffer(msgToPublish)).toString('base64');   
      var sendCommandObj = '{"messageId":"MSGxyz","deviceId":"'+deviceId+'","commandId":"'+appcommandID+'","message":"' + encodedMsg + '","encodingType":"BASE64"}';
      client.publish(producerTopic, sendCommandObj);
      console.log('Message published: ' + sendCommandObj);
      //console.log('Message published!!!');
}
setupMQTT();