import { Aedes } from 'aedes';
import { createServer } from 'node:net';
const broker = await Aedes.createBroker();
const server = createServer(broker.handle);
server.listen(18883, '127.0.0.1', () => console.log('Broker de teste MQTT em 127.0.0.1:18883'));
process.on('SIGINT', () => server.close(() => broker.close()));
