import json
from pathlib import Path
nodes=[]
def add(id,type,**kw):
 n=dict(id=id,type=type,**kw);nodes.append(n);return n
add('tab','tab',label='CardioIA • dados sintéticos')
add('broker','mqtt-broker',name='Broker didático configurável',broker='${MQTT_HOST}',port='${MQTT_PORT}',clientid='',autoConnect=True,usetls=False,protocolVersion='4',keepalive='60',cleansession=True,autoUnsubscribe=True)
add('base','ui-base',name='CardioIA',path='/dashboard',includeClientData=True,acceptsClientConfig=['ui-control','ui-notification'],showPathInSidebar=False,headerContent='page',navigationStyle='default',titleBarStyle='default')
add('theme','ui-theme',name='CardioIA',colors={'surface':'#ffffff','primary':'#a41452','bgPage':'#f3f5f7','groupBg':'#ffffff','groupOutline':'#dce2e8'},sizes={'density':'default','pagePadding':'16px','groupGap':'16px','groupBorderRadius':'8px','widgetGap':'12px'})
add('page','ui-page',name='CardioIA • Monitoramento didático',ui='base',path='/cardioia',icon='favorite',layout='grid',theme='theme',order=1,className='',visible=True,disabled=False,breakpoints=[{'name':'Default','px':'0','cols':'3'},{'name':'Tablet','px':'576','cols':'6'},{'name':'Desktop','px':'1024','cols':'12'}])
add('group','ui-group',name='Sinais simulados • sem uso clínico',page='page',width='12',height='1',order=1,showTitle=True,className='',visible=True,disabled=False,groupType='default')
def flow(id,type,**kw):return add(id,type,z='tab',**kw)
flow('mqtt','mqtt in',name='Telemetria sintética',topic='cardioia/rm568506/telemetry',qos='0',datatype='auto-detect',broker='broker',nl=False,rap=True,rh=0,x=150,y=100,wires=[['validate']])
validation='''let p=msg.payload;
try { if (typeof p === "string" || Buffer.isBuffer(p)) p=JSON.parse(p.toString()); } catch(e) { return null; }
if (!p || p.sensor_error !== false || typeof p.device_id !== 'string' || !/^[A-Za-z0-9_-]{1,64}$/.test(p.device_id) || !Number.isFinite(p.acceleration) || p.acceleration<0 || p.acceleration>200 || !Number.isInteger(p.uptime_ms) || p.uptime_ms<0 || p.uptime_ms>4294967295 || !Number.isInteger(p.age_ms) || p.age_ms<0 || p.age_ms>4294967295 || p.synthetic !== true || !Number.isFinite(p.bpm) || p.bpm<0 || p.bpm>250 || !Number.isFinite(p.temperature) || p.temperature < -40 || p.temperature > 80 || !Number.isFinite(p.humidity) || p.humidity<0 || p.humidity>100 || !Number.isInteger(p.seq) || p.seq<0 || typeof p.session_id !== 'string' || p.session_id.length>80) { node.warn('telemetria inválida rejeitada'); return null; }
// Deduplicação limitada em memória; não autentica a origem no broker público.
const stream=p.device_id+':'+p.session_id; const key=stream+':'+p.seq; let seen=context.get('seen')||[];
let streams=context.get('streams')||{};if(streams[stream]!==undefined && p.seq<=streams[stream])return null;
streams[stream]=p.seq;const keys=Object.keys(streams);if(keys.length>2000)delete streams[keys[0]];context.set('streams',streams);
if (seen.includes(key)) return null; seen.push(key); if(seen.length>2000) seen.shift();context.set('seen',seen);
const alerts=[];if(p.bpm>120)alerts.push('BPM > 120');if(p.temperature>38)alerts.push('temperatura > 38 °C');
const status=(p.age_ms>15000?'BACKLOG — amostra antiga, não representa estado atual | ':'')+(alerts.length ? 'ALERTA DIDÁTICO: '+alerts.join(' | ') : 'Dentro dos limites didáticos');
const record={...p,received_at:new Date().toISOString(),alert:alerts.length>0,backlog:p.age_ms>15000,status};
flow.set('latest',record);flow.set('accepted',(flow.get('accepted')||0)+1);
return [{payload:p.bpm,topic:'BPM sintético'},{payload:p.temperature},{payload:status},{payload:record}];'''
flow('validate','function',name='Validar / deduplicar / classificar',func=validation,outputs=4,timeout=0,noerr=0,initialize='',finalize='',libs=[],x=410,y=100,wires=[['chart'],['gauge'],['alert'],['debug']])
flow('chart','ui-chart',group='group',name='BPM',label='BPM sintético • horário de recepção',order=1,chartType='line',category='topic',categoryType='msg',xAxisProperty='',xAxisPropertyType='timestamp',xAxisType='time',xAxisFormat='',xAxisFormatType='auto',yAxisProperty='payload',yAxisPropertyType='msg',yAxisLabel='bpm',ymin='0',ymax='200',action='append',stackSeries=False,pointShape='circle',pointRadius=2,showLegend=True,removeOlder=1,removeOlderUnit='3600',removeOlderPoints='720',colors=['#a41452'],textColor=['#666666'],textColorDefault=True,gridColor=['#e5e5e5'],gridColorDefault=True,width=8,height=6,interpolation='linear',x=730,y=60,wires=[[]])
flow('gauge','ui-gauge',group='group',name='Temperatura ambiental',label='DHT22 • temperatura ambiental',order=2,width=4,height=6,gtype='gauge-half',gstyle='needle',min=-40,max=80,segments=[{'from':-40,'color':'#168f89'},{'from':38,'color':'#e85b63'}],value='payload',valueType='msg',units='°C',sizeThickness=16,sizeGap=4,sizeKeyThickness=8,x=740,y=120,wires=[[]])
flow('alert','ui-text',group='group',name='Alerta',label='Estado',order=3,width=12,height=1,value='payload',valueType='msg',layout='row-spread',style=False,font='',fontSize=16,color='#a41452',wrapText=True,x=740,y=180,wires=[])
flow('note','ui-template',group='group',name='Aviso e origem',order=0,width=12,height=1,format='<template><p><strong>DADOS SINTÉTICOS.</strong> Protótipo acadêmico; DHT22 ambiental e BPM simulado. Reenvios offline aparecem no horário de recepção. Sem telemetria nova por 15s: estado desatualizado.</p></template>',storeOutMessages=True,passthru=False,resendOnRefresh=True,templateScope='local',x=730,y=240,wires=[[]])
flow('tick','inject',name='Verificar ausência de dados',props=[{'p':'payload'}],repeat='5',once=True,onceDelay=1,payload='',payloadType='date',x=160,y=300,wires=[['stale']])
flow('stale','function',name='Estado desatualizado após 15 s',func="const p=flow.get('latest');if(!p || Date.now()-Date.parse(p.received_at)>15000)return {payload:'SEM DADOS RECENTES — não inferir estado normal'};return null;",outputs=1,x=420,y=300,wires=[['alert']])
flow('debug','debug',name='Telemetria validada',active=False,tosidebar=True,console=False,tostatus=False,complete='payload',x=740,y=300,wires=[])
flow('http','http in',name='Estado local para QA',url='/api/state',method='get',upload=False,swaggerDoc='',x=150,y=400,wires=[['state']])
flow('state','function',name='Snapshot somente leitura',func="const latest=flow.get('latest')||null;msg.payload={synthetic:true,accepted:flow.get('accepted')||0,latest,stale:!latest||Date.now()-Date.parse(latest.received_at)>15000};return msg;",outputs=1,x=420,y=400,wires=[['response']])
flow('response','http response',name='',statusCode='',headers={},x=740,y=400,wires=[])
ids={a['id'] for a in nodes}
for n in nodes:
 for k in ('id','z','ui','page','theme','group','broker'):
  if k in n and n[k] in ids: n[k]='cardio-'+n[k]
 if 'wires' in n: n['wires']=[['cardio-'+v for v in w] for w in n['wires']]
Path('dashboard/flows.json').write_text(json.dumps(nodes,ensure_ascii=False,indent=2)+'\n')
