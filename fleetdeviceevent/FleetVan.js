//var GrovePi = require('../libs').GrovePi
var GrovePi = require('./libs').GrovePi; //libs directory is in current diractory
var mqtt    = require('mqtt');
var config = require(./MQTTInfo1.json)
var childProcessor    = require('child_process');
var Commands = GrovePi.commands;
var Board = GrovePi.board;
//var AccelerationI2cSensor = GrovePi.sensors.AccelerationI2C;
//var UltrasonicDigitalSensor = GrovePi.sensors.UltrasonicDigital;
//var AirQualityAnalogSensor = GrovePi.sensors.AirQualityAnalog;
//var DHTDigitalSensor = GrovePi.sensors.DHTDigital;
//var LightAnalogSensor = GrovePi.sensors.LightAnalog;
//var TempAnalogSensor = GrovePi.sensors.TemperatureAnalog;
var TempAnalogSensor = GrovePi.sensors.base.Analog;
var DigitalSensor = GrovePi.sensors.base.Digital;


var isBaton = false;
var valueChanged = false;
var board;
var engine;
var tireSensor;
var tirePressureValue = 31;
var oilLevelSensor;
var oilLevelValue = 0;
var troubleBtn;
var troubleLed;
var troubleStatus=0;
var engineStatus=0;
var troubleButtonStatus=0;
var troubleDTCCode = '';
var flyingJBtn;
var gearBtn;
var gearLed;
var doorLed;
var FlyingJStatus=0;
var gearStatus=0;
var doorStatus=0;
var gearButtonStatus=0;
var FlyingJButtonStatus=0;
var consumerTopic = config.consumerTopic;
var producerTopic = config.producerTopic;
var clientID = config.clientID
var mqttUserName =  config.username
var mqttPassword =  config.password
var playerID = 'xxxxx';

//MQTT Variables
var client;
var alertEventID = config.alertID;
var stateChangeEventID = config.statusEventID;
var deviceId = config.deviceID;


function setupMQTT() {
	client  = mqtt.connect('ssl://mqtt.covapp.io:8883', {
		keepalive: 10, 
        clientId: clientID,
        clean: true,
        protocolId: 'MQTT',
        connectTimeout: 30 * 1000,
        username: mqttUsername,
        password: mqttPassword
	});
	console.log('MQTT Connection attempted. ' + client);

	client.on('connect', function () {
		console.log('MQTT Connection Successful');
		client.subscribe(consumerTopic);
		console.log('MQTT subscription complete');
		//publishMessage(stateChangeEventID, 'Anuj Tyagi');
	});

	client.on('message', function (topic, message) {
		// message is Buffer 
		//console.log(message.toString());
		var jsonCmdObj = JSON.parse(message.toString());
		var decodedPayload = new Buffer(jsonCmdObj.message, 'base64');
		console.log("Command: %s Payload: %s", jsonCmdObj.commandId, decodedPayload.toString());
               //console.log('commandtype='+decodedPayload.toString().commandType)
                var msgObj = JSON.parse(decodedPayload.toString())   
                console.log('commandtype='+msgObj.CommandType)
		if(msgObj.CommandType == "FlyingJ" && msgObj.CommandValue1 =="1") {
			console.log('Process FlyingJ command');
			processFlyingJAcceptCommand(decodedPayload.toString())
		} else if(msgObj.CommandType == "Engine" ) {
			console.log('Process Engine start stop command');
			processEngineCommand(decodedPayload.toString());
		} else if(msgObj.CommandType == "Door" ) {
                        console.log('process door command')
			processDoorCommand(decodedPayload.toString());
		}  else if(msgObj.CommandType == "ONESIGNALDEVICEID" ) {
                        console.log('process playerid  command')
			processplayerIDCommand(decodedPayload.toString());
		} 
		//client.end();
	});
}

var driverKeyMacAddress = 'F3:1B:7B:E8:10:97';
var isDriverNearBy = false;
/*function setupBLEScanner() {
	var n = childProcessor.fork('./ble-device-scaner.js');

	n.on('message', function(msg){
		var command = msg.Command;
		//console.log('Parent: Message Arrived', command);
		if(command === 'DeviceLocated') {
			//console.log('Parent: Device Found with RSSI; %s', msg.RSSI);
			if(msg.RSSI > -75) {
				if(!isDriverNearBy) {
					isDriverNearBy = true;
					console.log('Driver inside!');
					//processDoorCommand('{"Status":1}');
				}
			} else if(isDriverNearBy) {
				isDriverNearBy = false;
				console.log('Driver outside!');
				//processDoorCommand('{"Status":0}');
			}
		}
	});

	n.send({ 'Command': 'InitScanner' });
	n.send({ 'Command': 'DeviceLkup', 'DeviceID':driverKeyMacAddress});
}*/

function publishMessage(eventID, msgToPublish){
       console.log('Publishing message: ' + msgToPublish);
	var encodedMsg = (new Buffer(msgToPublish)).toString('base64');	
	var sendEventMessageObj = '{"messageId":"MSG12345","deviceId":"'+deviceId+'","eventTemplateId":"' + eventID + '","message":"' + encodedMsg + '","encodingType":"BASE64"}';
	client.publish(producerTopic, sendEventMessageObj);
	console.log('Message published: ' + sendEventMessageObj);
	console.log('Message published!!!');
}

function start() {
	console.log('starting')

	board = new Board({
		debug: true,
		onError: function(err) {
			console.log('TEST ERROR')
			console.log(err)
		},
		onInit: function(res) {
			if (res) {
				// Analog input
				oilLevelSensor = new TempAnalogSensor(1);
				tireSensor = new TempAnalogSensor(2);
				// Digital input/output
				engine = new DigitalSensor(8);
				troubleBtn = new DigitalSensor(3);
                                gearBtn = new DigitalSensor(4);
				flyingJBtn = new DigitalSensor(2);
				troubleLed = new DigitalSensor(5);
			        gearLed = new DigitalSensor(6);
				doorLed = new DigitalSensor(7);
				engine.write(0);
				troubleLed.write(0);
				gearLed.write(0);
				doorLed.write(0);

				console.log('GrovePi Version :: ' + board.version())
				// Vibration Sensor
				console.log('Analog(1) Vibration Sensor (start watch)')
				oilLevelSensor.on('change', function(res) {
					var _tempLevel = res/11
					//console.log('_tempLevel: ' + _tempLevel + ' oilLevelValue: ' + oilLevelValue)
					if(_tempLevel!=0 && (_tempLevel>oilLevelValue+2 || _tempLevel<oilLevelValue-2)) {
						oilLevelValue = Math.round(_tempLevel)
						//console.log('New oil value: ' + oilLevelValue)
						var oilLevelStatusStr = '{"AnalogName4":"OilLevel","AnalogValue4":"'+oilLevelValue+'","AnalogName6":"Tirepressure","AnalogValue6":"'+tirePressureValue+'"}' ;
						publishMessage(stateChangeEventID,oilLevelStatusStr);
					}		
				})
				oilLevelSensor.watch()

				// Temp Sensor
				console.log('Analog(2) Sensor (start watch)')
				tireSensor.on('change', function(res) {
					var _tempLevel = res/10
					if(_tempLevel!=0 && (_tempLevel>tirePressureValue+2 || _tempLevel<tirePressureValue-2)) {
						tirePressureValue = Math.round(_tempLevel)
						//console.log('New tire value: ' + tirePressureValue)
						var tirePressureStr = '{"AnalogName6":"Tirepressure","AnalogValue6": "'+tirePressureValue+'","AnalogName4":"OilLevel","AnalogValue4":"'+oilLevelValue+'"}' ;
						publishMessage(stateChangeEventID,tirePressureStr);
					}
				})
				tireSensor.watch()

				// trouble button Sensor
				console.log('Digital(3) trouble  Sensor (start watch)')
				troubleBtn.on('change', function(res) {
					var bytes = res	//this.board.readBytes()
					/*console.log('Bytes received: ' + bytes.length)
	  	console.log('Digital(3) onChange value=' + bytes[0])*/
                                    //console.log('troublebytes='+bytes[0])
					evaluateTroubleStatus(bytes[0])
				})
				troubleBtn.watch()

				// flyingj button Sensor
				console.log('Digital(2) Sensor (start watch)')
				flyingJBtn.on('change', function(res) {
					var bytes = res	//this.board.readBytes()
					/*console.log('Bytes received: ' + bytes.length)
	  	console.log('Digital(4) onChange value=' + bytes[0])*/
					evaluateFlyingJStatus(bytes[0])
				})
				flyingJBtn.watch()
                                
                                console.log('Digital(4) Sensor (start watch)')
                                gearBtn.on('change', function(res) {
                                        var bytes = res //this.board.readBytes()
                                        /*console.log('Bytes received: ' + bytes.length)
                console.log('Digital(4) onChange value=' + bytes[0])*/
                                        evaluateGearStatus(bytes[0])
                                })
                                gearBtn.watch()                               

				//engine.write(1)
                                //doorLed.write(1)

			} else {
				console.log('TEST CANNOT START')
			}
		}
	})
	board.init()
}

function evaluateTroubleStatus(troubPressValue) {
        //console.log ('troublpressvalue='+troubPressValue)
	var buttonPressed = false
	if((isBaton && troubPressValue==0)
			|| (!isBaton && troubPressValue==1)) {
		buttonPressed = true
	}

	if(buttonPressed) {
		if(troubleButtonStatus==0) {
			valueChanged = true;
			if (troubleStatus == 0) {
				troubleStatus = 1;
				troubleLed.write(1);
			} else {
				troubleStatus = 0;
				troubleLed.write(0);
			}
			troubleButtonStatus = 1;
			//console.log("Trouble button clicked: " + troubleStatus);
			var troublestatusStr = '{"AlertName1":"Trouble", "AlertValue1": "'+troubleStatus+'","AlertName4":"playerID","AlertValue4":"'+playerID+'"}';
                        if (playerID === 'xxxxx'){
                           troublestatusStr =  '{"AlertName1":"Trouble", "AlertValue1": "'+troubleStatus+'"}';
                        }
			publishMessage(alertEventID,troublestatusStr);
		}
	} else {
		troubleButtonStatus = 0
	}
}

function evaluateFlyingJStatus(FlyingJPressValue) {
	var buttonPressed = false
	if((isBaton && FlyingJPressValue==0)
			|| (!isBaton && FlyingJPressValue==1)) {
		buttonPressed = true
	}

	if(buttonPressed) {
		if(FlyingJButtonStatus==0) {
			valueChanged = true;
			if (FlyingJStatus == 0) {
				FlyingJStatus = 1;
				//FlyingJLed.write(1);
			} else {
				FlyingJStatus = 0;
				//FlyingJLed.write(0);
			}
			FlyingJButtonStatus = 1;
			//console.log("Gear button clicked: " + FlyingJStatus);
			var flyingJStr = '{"AlertName2":"FlyingJ","AlertValue2":"'+FlyingJStatus+'","AlertName4":"playerID","AlertValue4":"'+playerID+'"}' ;
                        if (playerID === 'xxxxx'){
                           flyingJStr =  '{"AlertName2":"FlyingJ", "AlertValue2": "'+FlyingJStatus+'"}';
                        }
			publishMessage(alertEventID,flyingJStr);
		}
	} else {
		FlyingJButtonStatus = 0
	}
}

/*function processStateChange(eventID,messageStr) {
	//console.log('Trouble:%s, ViberationValue:%s, tirePressureValue:%s, Gear:%s', troubleStatus, oilLevelValue, tirePressureValue, FlyingJStatus);
	
         if(troubleStatus==1) {
		troubleDTCCode = 'P0420';
	} else {
		troubleDTCCode = '0';
	}
	//var str = '{"Door":'+doorStatus+',"Tire Pressure":'+tirePressureValue+', "Oil Level":'+oilLevelValue+', "Status":'+FlyingJStatus+', "Trouble Code":"'+troubleDTCCode+'"}'
       //console.log(messageStr);
	publishMessage(eventID, messageStr);

	if(valueChanged && troubleStatus==1) {
		console.log('Generate an SOS event as well.');
		//publishMessage(sosEventID, '{"Trouble": "1"}');
		valueChanged=false;
	}
}*/

function processEngineCommand(requestPayload) {
	console.log('Process engine command: %s', requestPayload);
	var jsonObj = JSON.parse(requestPayload);
	var newEngineStatus = jsonObj.CommandValue1;
        console.log ("new engine status ="+newEngineStatus)
        console.log ("old engine status = "+engineStatus)
	if(engineStatus != newEngineStatus) {
		valueChanged = true;
		engineStatus = newEngineStatus;
                if (engineStatus == 0){
                   engine.write(0);
                } else {
                  engine.write(1);
                }
		var engineStatusStr = '{"DigitalName1":"Engine", "DigitalValue1": "'+newEngineStatus+'"}' ;
		publishMessage(stateChangeEventID,engineStatusStr);
	}
}

function processDoorCommand(requestPayload) {
	console.log('Process Door command: %s', requestPayload);
	var jsonObj = JSON.parse(requestPayload);
	var newDoorStatus = jsonObj.CommandValue1;
	console.log("New Door Status: %s", newDoorStatus);
	if(doorStatus != newDoorStatus) {
		valueChanged = true;
		doorStatus = newDoorStatus;
                if (doorStatus == 0){
                      doorLed.write(0);
                }else {
                      doorLed.write(1)
                }
		var doorStatusStr = '{"DigitalName2":"Door", "DigitalValue2": "'+newDoorStatus+'"}' ;
		publishMessage(stateChangeEventID,doorStatusStr);
	}
}

function processFlyingJAcceptCommand(requestPayload){
    console.log('Process flyinJ command: %s', requestPayload);
	var jsonObj = JSON.parse(requestPayload);
	var flyingJRequestStatus = jsonObj.CommandValue1;
	console.log("Flyingj: %s", flyingJRequestStatus);
	if(flyingJRequestStatus == '1') {
		sendFlyingJCouponAlertEvent();
	}

	
}
function processplayerIDCommand(requestPayload){
    console.log('Process playerID command: %s', requestPayload);
	var jsonObj = JSON.parse(requestPayload);
	playerID = jsonObj.CommandValue2;
	console.log("playerID: %s", playerID);
}


/*function sendTroubleEventAlertEvent(){
   var troubleAlertString = '{"AlertName1":"Trouble", "AlertValue1": "1"}' 
	console.log(troubleAlertString);
	publishMessage(alerteventID, troubleAlertString);
}*/

function sendFlyingJCouponAlertEvent(){
	var flyingJCouponStr = '{"AlertName3":"FlyingJCoupon","AlertValue3":"1",'+'"AlertName4":"playerID","AlertValue4":"'+playerID+'"}';
         if(playerID != 'xxxxx'){
             console.log(flyingJCouponStr);
             publishMessage(alertEventID, flyingJCouponStr);
         }else {
           publishMessage(alertEventID, flyingJCouponStr);
          }
                                  
}

function sendstatusEventTimer(){

	var statusStr = '{"AnalogName4":"OilLevel","AnalogValue4":"'+oilLevelValue+'","AnalogName6":"Tirepressure","AnalogValue6":"'+tirePressureValue+'","DigitalName2":"Door","DigitalValue2":'+doorStatus+',"DigitalName1":"Engine","DigitalValue1":'+engineStatus+',"DigitalName3":"Gear","DigitalValue3":'+gearStatus+',"AnalogName5":"playerID","AnalogValue5":"'+playerID+ '"}' ;
        if(playerID === 'xxxxx'){
         statusStr = '{"AnalogName4":"OilLevel","AnalogValue4":"'+oilLevelValue+'","AnalogName6":"Tirepressure","AnalogValue6":"'+tirePressureValue+'","DigitalName2":"Door","DigitalValue2":'+doorStatus+',"DigitalName1":"Engine","DigitalValue1":'+engineStatus+',"DigitalName3":"Gear","DigitalValue3":'+gearStatus+'}' ;
        }
	publishMessage(stateChangeEventID, statusStr);
}
function evaluateGearStatus(gearPressValue) {
        var buttonPressed = false
        if((isBaton && gearPressValue==0)
                        || (!isBaton && gearPressValue==1)) {
                buttonPressed = true
        }

        if(buttonPressed) {
                if(gearButtonStatus==0) {
                        valueChanged = true;
                        if (gearStatus == 0) {
                                gearStatus = 1;
                                gearLed.write(1);
                        } else {
                                gearStatus = 0;
                                gearLed.write(0);
                        }
                        gearButtonStatus = 1;
                        //console.log("Gear button clicked: " + gearStatus);
                        var gearStatusStr = '{"DigitalName3":"Gear", "DigitalValue3": "'+gearStatus+'"}' ;
                        publishMessage(stateChangeEventID,gearStatusStr);
                }
        } else {
                gearButtonStatus = 0
        }
}


function onExit(err) {
	engine.write(0);
	troubleLed.write(0);
        doorLed.write(0);
        gearLed.write(0);
	console.log('ending');
	board.close();
	process.removeAllListeners();
	process.exit();
	if (typeof err != 'undefined')
		console.log(err);
}

setupMQTT()
//setupBLEScanner()
//starts the test
start()
setInterval(function(){
  sendstatusEventTimer();
}, 60000);
//catches ctrl+c event
process.on('SIGINT', onExit)
