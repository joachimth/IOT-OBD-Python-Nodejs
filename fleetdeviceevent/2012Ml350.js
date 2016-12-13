var mqtt    = require('mqtt');

var client;
var deviceId = 'e82a9878-489e-40d3-8d9c-c5bdcc7bbcdd';
var consumerTopic = '3c8073c9-b07c-4ca2-8322-a884a3c049a4';
var producerTopic = 'cf2ec4c2-de54-4d30-9524-c661e182097a';
var engineEventID = '71a0d3cb-e228-47f6-b446-76a5beab2478';
var appcommandID = 'b57e3426-6b8e-4a75-a826-a0885c014c0d';
var statestatus = '0';
//var strMsg = {Engine Status:statestatus};
var strMsg = '{"Engine Status":"'+statestatus+'"}'

function setupMQTT() {
/*ESTABLISH MQTT CONNECTION*/
client = mqtt.connect('ssl://xx.xxx.xx:8883',
            {
                  keepalive: 10, 
                  clientId: '275DFC8E1Cb248018cf1',
                  clean: true,
                  protocolId: 'MQTT',
                  connectTimeout: 30 * 1000,
                  username: 'ae987bd2-75c2-4453-8c25-bc588fb5a7f6',
                  password: '786420bf-abd5-4ee6-8e15-2dc81b5a3303'            });

client.on('connect', function () {
            console.log('MQTT Connection Successful');
            client.subscribe(consumerTopic);
            console.log('MQTT subscription complete');
            //publishMessage(stateChangeEventID, 'Anuj Tyagi');
      });

client.on('message', function (topic, message) {
            // message is Buffer 
            console.log(message.toString());
            var jsonStatusObj = JSON.parse(message.toString());
            var decodedPayload = new Buffer(jsonStatusObj.message, 'base64');
            console.log("DeviceID: %s Payload: %s", jsonStatusObj.deviceId, decodedPayload.toString());
            

        });  

publishMessage(engineEventID,strMsg);
//console.log("published message complete");        
}


function publishMessage(eventID, msgToPublish){
      console.log('Publishing message: ' + msgToPublish);
      var encodedMsg = (new Buffer(msgToPublish)).toString('base64'); 
      console.log('encoded Publishing message: ' + encodedMsg);  
      var sendEventMessageObj = '{"messageId":"MSG12345","deviceId":"'+deviceId+'","eventTemplateId":"' + eventID + '","message":"' + encodedMsg + '","encodingType":"BASE64"}';
      client.publish(producerTopic, sendEventMessageObj);
      console.log('send event Message published: ' + sendEventMessageObj);
      //console.log('Message published!!!');
}
setupMQTT();