var mqtt = require('mqtt')

var client  = mqtt.connect("mqtt://broker.hivemq.com",{clientId:"mqttjs01"});
client.on("connect",function(){	
console.log("connected");
client.publish("test", "test message")
})