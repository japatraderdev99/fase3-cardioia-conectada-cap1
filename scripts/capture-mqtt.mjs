import mqtt from 'mqtt';
import {appendFileSync} from 'node:fs';
const client=await mqtt.connectAsync('mqtt://broker.hivemq.com:1883');
await client.subscribeAsync('cardioia/rm568506/telemetry');
client.on('message',(_,data)=>{try {const payload=JSON.parse(data);if(payload.device_id==='cardioia-rm568506')appendFileSync('evidence/wokwi-final-mqtt.jsonl',JSON.stringify({received_at:new Date().toISOString(),payload})+'\n');}catch{}});
process.on('SIGINT',()=>client.end(true,()=>process.exit(0)));
console.log('Captura assinante MQTT iniciada; apenas device_id acadêmico. Ctrl+C encerra.');
