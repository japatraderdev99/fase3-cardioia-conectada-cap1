import mqtt from 'mqtt';
import assert from 'node:assert/strict';
import {writeFileSync} from 'node:fs';

// Execute em ambiente isolado: outros publishers alteram o snapshot compartilhado.
const url=process.env.MQTT_URL||'mqtt://127.0.0.1:18883';
const stateUrl=process.env.STATE_URL||'http://127.0.0.1:1887/api/state';
const timeoutMs=Number(process.env.QA_TIMEOUT_MS||15000);
assert.ok(Number.isFinite(timeoutMs)&&timeoutMs>=1000,'QA_TIMEOUT_MS deve ser >=1000');
const wait=ms=>new Promise(resolve=>setTimeout(resolve,ms));
async function bounded(promise,ms,label) {
  let timer;
  try { return await Promise.race([promise,new Promise((_,reject)=>{timer=setTimeout(()=>reject(new Error(`Timeout: ${label}`)),ms);})]); }
  finally {clearTimeout(timer);}
}
async function state() {
  const response=await fetch(stateUrl,{signal:AbortSignal.timeout(3000)});
  assert.equal(response.status,200,'endpoint de estado deve responder 200');
  return response.json();
}
async function poll(predicate,label,timeout=timeoutMs) {
  const deadline=Date.now()+timeout;
  let snapshot;
  do {
    snapshot=await state();
    if(predicate(snapshot))return snapshot;
    await wait(100);
  }while(Date.now()<deadline);
  throw new Error(`Timeout esperando ${label}; snapshot=${JSON.stringify(snapshot)}`);
}
const topic='cardioia/rm568506/telemetry';
const session_id='host-qa-'+Date.now();
const payload={synthetic:true,session_id,device_id:'host-qa',seq:0,
  temperature:36.5,humidity:55,bpm:75,acceleration:9.81,uptime_ms:0,
  age_ms:0,sensor_error:false};
const identityMatches=(snapshot,p)=>snapshot.latest?.device_id===p.device_id
  &&snapshot.latest?.session_id===p.session_id&&snapshot.latest?.seq===p.seq;
let client;
try {
  client=await mqtt.connectAsync(url,{connectTimeout:10000,reconnectPeriod:0});
  const publish=async p=>bounded(client.publishAsync(topic,JSON.stringify(p),{qos:0}),timeoutMs,'publicação MQTT');
  let acceptedCount=0;
  const before=await state();
  async function accepted(p) {
    await publish(p);
    const snapshot=await poll(s=>identityMatches(s,p),`recepção ${p.device_id}/${p.session_id}/${p.seq}`);
    acceptedCount++;
    assert.equal(snapshot.accepted,before.accepted+acceptedCount,'Use serviço isolado: contador inclui todos os publishers');
    return snapshot;
  }
  async function rejected(p,label) {
    const snapshot=await state();
    await publish(p);
    // QoS 0 não fornece ACK de consumo. Janela observacional explícita de 2 s.
    // O teste comprova ausência de aceitação nessa janela, não ausência eterna.
    const deadline=Date.now()+2000;
    do {
      const current=await state();
      assert.equal(current.accepted,snapshot.accepted,`${label}: mensagem indevidamente aceita`);
      assert.deepEqual(current.latest,snapshot.latest,`${label}: alterou latest`);
      await wait(100);
    }while(Date.now()<deadline);
  }
  for(let i=0;i<12;i++)await accepted({...payload,seq:i,bpm:75+i*6,uptime_ms:i*5000});
  const normal=await state();assert.equal(normal.latest.bpm,141);assert.equal(normal.latest.alert,true);
  const boundary=await accepted({...payload,seq:12,bpm:120,temperature:38,uptime_ms:60000});
  assert.equal(boundary.latest.alert,false);
  const alertSample={...payload,seq:13,bpm:130,temperature:39.2,uptime_ms:65000};
  const alert=await accepted(alertSample);assert.equal(alert.latest.alert,true);assert.match(alert.latest.status,/temperatura/);
  await rejected(alertSample,'duplicata');
  await rejected({...payload,seq:12},'regressão de sequência');
  await rejected({...payload,seq:14,synthetic:false},'synthetic=false');
  await rejected({...payload,seq:15,bpm:'150'},'BPM string');
  await rejected({...payload,seq:16,temperature:null,sensor_error:true},'sensor nulo');
  await rejected({...payload,seq:18,sensor_error:true},'falha de sensor');
  await rejected({...payload,seq:19,acceleration:null},'aceleração nula');
  await rejected({...payload,seq:20,uptime_ms:'bad'},'uptime inválido');
  await rejected({...payload,seq:21,sensor_error:undefined},'sensor_error obrigatório');
  await rejected({...payload,seq:22,device_id:undefined},'device_id obrigatório');
  await rejected({...payload,seq:23,age_ms:-1},'idade inválida');
  const stale=await poll(s=>s.stale===true,'estado desatualizado',20000);
  const recovered=await accepted({...payload,seq:24,bpm:135,temperature:39.2,uptime_ms:120000});
  assert.equal(recovered.stale,false);
  // Mesmo session_id/seq, mas identidade de dispositivo diferente, deve ser aceito.
  const otherDevice=await accepted({...payload,device_id:'host-qa-secondary',seq:24});
  const backlog=await accepted({...payload,seq:25,uptime_ms:125000,age_ms:60000});
  assert.match(backlog.latest.status,/BACKLOG/i,'amostra antiga exige indicação explícita');
  const fresh=await accepted({...payload,seq:26,uptime_ms:130000});
  assert.doesNotMatch(fresh.latest.status,/BACKLOG/i);
  assert.equal(fresh.stale,false);
  assert.equal(acceptedCount,18);
  const evidence={timestamp:new Date().toISOString(),source:'Host Node.js publisher, NOT ESP32/Wokwi',
    broker:url,state_url:stateUrl,negative_observation_window_ms:2000,accepted_messages:acceptedCount,
    checks:['MQTT recebido pelo fluxo Node-RED e correlacionado por dispositivo/sessão/sequência',
      'limiares estritos','alerta','deduplicação por identidade','rejeição de regressão de sequência',
      'validação de contrato e sensor_error','estado obsoleto','recuperação','indicação BACKLOG'],
    scope:'Snapshot do fluxo; este teste não verifica renderização do gráfico/gauge no navegador.',
    boundary,alert,stale,recovered,otherDevice,backlog,fresh,result:'PASS'};
  const path=url.includes('127.0.0.1')?'evidence/mqtt-local.json':'evidence/mqtt-public.json';
  writeFileSync(path,JSON.stringify(evidence,null,2)+'\n');
  console.log(JSON.stringify({result:'PASS',path,checks:evidence.checks},null,2));
}finally {
  if(client)await client.endAsync(true);
}
