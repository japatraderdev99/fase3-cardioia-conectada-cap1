# ESP32 / Wokwi

Todos os sinais são **sintéticos**. Autoria acadêmica: Guilherme Yamada Dantas, rm568506.

## Compilar

A partir da raiz do repositório:

```sh
python3 -m venv firmware/.venv
firmware/.venv/bin/pip install platformio==6.2.0
firmware/.venv/bin/pio run -d firmware
```

A primeira compilação baixa plataforma e bibliotecas. Os artefatos ficam em `firmware/.pio/build/esp32/`. `platformio.ini` fixa as dependências diretas. O firmware usa DHT22, MPU6050 e potenciômetro (controle de BPM sintético).

## Abrir no Wokwi

Crie um projeto ESP32 e copie `sketch.ino`, `RingBuffer.h`, `diagram.json` e `libraries.txt` para arquivos com esses nomes. Alternativamente, use a extensão Wokwi do VS Code com o binário compilado e `wokwi.toml`. O acesso ao simulador/extensão pode exigir configuração de conta; este repositório não contém uma URL Wokwi inventada.

1. Inicie a simulação e observe `COLLECT` a cada cinco segundos.
2. Altere temperatura/umidade no DHT22, aceleração no MPU6050 e BPM no potenciômetro.
3. No Serial a 115200, envie `0`; observe a fila crescer por ao menos três coletas.
4. Envie `1`; confirme `PUBLISH_QOS0` para as sequências retidas e fila reduzindo.
5. No Node-RED conectado ao mesmo tópico, observe gráfico de BPM, gauge de temperatura e alerta com BPM >120 ou temperatura >38.
6. Salve o projeto e registre URL real, prints e Serial. Reinicie e demonstre que a RAM não persiste.

Broker de demonstração: `broker.hivemq.com:1883`, tópico `cardioia/rm568506/telemetry`. Não coloque dados reais nesse broker público. Para um broker local acessível pelo simulador, configure a rede/gateway e altere `BROKER`; `localhost` no ESP32 não é seu computador.

Payload: `device_id`, `session_id`, `synthetic=true`, `seq`, `uptime_ms`, `age_ms` (idade da amostra em ms no envio), `temperature` (°C), `humidity` (%), `bpm` (sintético), `acceleration` (m/s²), `sensor_error`, `queued` e `dropped`. Campos de sensores inválidos são `null`. `queued` é o tamanho antes da remoção, não a quantidade restante depois do envio.

## Teste do buffer no host

```sh
clang++ -std=c++11 -Wall -Wextra -Werror firmware/tests/test_ring.cpp -o firmware/evidence/test_ring
firmware/evidence/test_ring
```

O teste não substitui execução ESP32/Wokwi. Fila 2.000 amostras em RAM, descarte da mais antiga, QoS 0 sem confirmação do broker. Consulte `docs/edge/relatorio-edge.md`.

`age_ms` usa subtração unsigned do relógio monotônico: indica tempo entre aquisição e tentativa de publicação, permitindo identificar backlog. Não inclui atraso posterior de rede ou de processamento. O consumidor deve considerar essa idade antes de mostrar a leitura como atual.

## Projeto Wokwi salvo

https://wokwi.com/projects/479273729983469569 — criado e salvo em 30/10/2026. A versão Web incorpora RingBuffer.h no sketch (mesmo conteúdo lógico), para importação simples. Evidências da execução em ../evidence/wokwi-*.
