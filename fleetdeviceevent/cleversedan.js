var mqtt    = require('mqtt');
var config = require('./MQTTInfo2.json');

var client;
var deviceId = "42ba1baf-d13c-4efc-9668-7558c51b9a81";
console.log(deviceId);
var consumerTopic = '7c056739-b5fd-4463-a6b5-ce9d27fe756d';
var producerTopic = 'b7054366-0bf3-47dd-8adf-edac2f663033';
var clientID = 'a2778e03E1a24903B41a';
var mqttUserName =  '45d6e8fc-28f2-473c-8daf-2267326b5b79';
var mqttPassword =  '559815dd-a318-4848-ab6d-721df45653ed';
var alertID = config.alertID;;
var statusID = config.statusEventID;
//var appcommandID = '039e88d7-1026-4121-a928-d171d90bae72';
// var statestatus = '1';
//var strMsg = {Engine Status:statestatus};
// var strMsg = '{"DigitalName6":"'+statestatus+'"}';
var statusStr = '{"AnalogName6":"Tirepressure", "AnalogValue6": "42", "AnalogName5": "playerID","AnalogValue5":"da0a2e09-aa7f-47dd-aaa2-430d0b0b5e8f"}' ;

function setupMQTT() {
/*ESTABLISH MQTT CONNECTION*/
client = mqtt.connect('ssl://mqtt.covapp.io:8883',
            {
                  keepalive: 10, 
                  clientId: clientID,
                  clean: true,
                  protocolId: 'MQTT',
                  connectTimeout: 30 * 1000,
                  username: mqttUserName,
                  password: mqttPassword            });

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
            //if (jsonStatusObj.deviceId != "2e497bd8-d172-425f-ae43-047ae0c036cd"){
            console.log("DeviceID: %s Payload: %s", jsonStatusObj.deviceId, decodedPayload.toString());
            //}
            //statusStr = '{"DigitalName6":"engine", "DigitalValue6":"1","DigitalName2":"door", "DigitalValue2": "0", "DigitalName3":"honk", "DigitalValue3": "0", "DigitalName4":".", "DigitalValue4": "0","DigitalName5":"beacon", "DigitalValue5": "1"}';
            //publishMessage(statusID,statusStr);  

        });  

//publishMessage(statusID,statusStr);
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
