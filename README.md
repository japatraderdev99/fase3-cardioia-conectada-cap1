# FIAP - Faculdade de Informática e Administração Paulista

<p align="center"><img src="docs/logo-fiap.png" alt="FIAP" width="240"></p>

# Fase 3 — CardioIA Conectada
## Graduação ON em Inteligência Artificial

**Responsável acadêmico:** Guilherme Yamada Dantas — RM rm568506.

Protótipo acadêmico de IoT e visualização de dados para saúde digital. **Somente dados sintéticos; sem uso clínico.** O DHT22 mede ambiente e o potenciômetro controla BPM simulado. Não há pacientes reais, termometria clínica ou diagnóstico.

## Sobre esta fase e objetivo

Demonstrar captura → fila limitada no ESP32 → MQTT → dashboard Node-RED → alertas didáticos. Dois sensores distintos (DHT22 e MPU6050) e um controle de BPM compõem o circuito. Os desafios Ir Além acrescentam cliente/API REST com e-mail simulado e comparação de regressão logística versus LIF com readout logístico.

## Estado verificável

| Entrega | Evidência / estado |
|---|---|
| Firmware C++ e circuito Wokwi | [firmware](firmware/README.md); compilação ESP32 e teste do buffer |
| MQTT + Node-RED | [export](dashboard/flows.json), [teste local](evidence/mqtt-local.json), [teste broker público](evidence/mqtt-public.json), [captura real](evidence/dashboard-local.png) |
| Ir Além 1 | [REST](rest/README.md); sete testes HTTP locais; e-mail somente em arquivo |
| Ir Além 2 | [notebook executado](ml/comparacao_logistica_lif.ipynb), [métricas](ml/results/metrics.json); quatro testes |
| Relatórios | [Edge](output/pdf/01-relatorio-edge.pdf), [MQTT](output/pdf/02-relatorio-mqtt.pdf), [REST](output/pdf/03-relatorio-rest.pdf), [IA](output/pdf/04-relatorio-ia.pdf) |
| Link Wokwi | [Projeto público salvo](https://wokwi.com/projects/479273729983469569) — execução registrada separadamente |
| Vídeo YouTube não listado, até 4 minutos | Pendente de gravação/publicação humana; [roteiro](docs/roteiro-demonstracao.md) |
| Revisão humana e envio ao Portal do Aluno | Pendentes |

Os testes MQTT citados usam publisher Node.js no computador; a execução ESP32/Wokwi tem evidências separadas. Consulte a [revisão final](docs/revisao-final.md) para o estado da simulação.

## Tecnologias e conteúdos abordados

ESP32/Arduino C++, FreeRTOS, DHT22, MPU6050, MQTT 3.1.1, Node-RED e FlowFuse Dashboard; Python, HTTP/JSON, SQLite, MIME, NumPy, scikit-learn e LIF. Conceitos: Edge/Fog/Cloud, resiliência limitada, duplicação, validação de telemetria, séries temporais, divisão treino/validação/teste e interpretação responsável de evidências.

## Executar o dashboard

Pré-requisito: Node.js 22 (execução verificada em 22.17.1) e npm. Na raiz:

```sh
npm ci
npm run broker
```

Em outro terminal:

```sh
MQTT_HOST=127.0.0.1 MQTT_PORT=18883 npm run dashboard
```

Abrir http://127.0.0.1:1887/dashboard/cardioia (editor em http://127.0.0.1:1887). Para gerar e testar telemetria local:

```sh
npm run test:mqtt
```

Para receber do Wokwi, encerrar o Node-RED local e iniciá-lo com `MQTT_HOST=broker.hivemq.com MQTT_PORT=1883 npm run dashboard`. O teste equivalente usa `MQTT_URL=mqtt://broker.hivemq.com:1883 npm run test:mqtt`. Não executar publisher de QA ao mesmo tempo que a demonstração ESP32: compartilham o tópico didático.

## Projetos desenvolvidos e estrutura

- [firmware/](firmware/): sketch comentado, circuito, dependências, fila e testes.
- [dashboard/](dashboard/): fluxo importável e configuração somente em loopback.
- [rest/](rest/): API/cliente Python, regras e e-mail simulado.
- [ml/](ml/): séries sintéticas independentes, notebook e métricas.
- [docs/](docs/): [matriz de requisitos](docs/plano-e-requisitos.md), relatórios fonte, roteiro e revisão.
- [evidence/](evidence/): execuções MQTT, captura, auditoria e validação.
- [output/pdf/](output/pdf/): relatórios paginados.
- [scripts/](scripts/): geração do fluxo, teste MQTT e renderização dos relatórios.

Executar REST e IA conforme seus READMEs. O REST e a IA são experimentos independentes: não se afirma que suas amostras vieram do ESP32. O REST usa `temperature_c`; o MQTT usa `temperature`, contratos distintos documentados.

## Resultados e competências

O buffer mantém as últimas 2.000 amostras e contabiliza descarte por saturação. A 5 segundos por coleta, a capacidade equivale a 2h46min40s; reiniciar perde a RAM. QoS 0 não garante entrega fim a fim. O Node-RED mostra BPM, temperatura, alerta e estado sem dados recentes.

Na distribuição sintética de teste (240 indivíduos), a logística obteve F1 0,8509 e o pipeline LIF + readout 0,7595. Não houve vantagem do LIF nesta configuração. Não se mediu energia, precisão clínica ou desempenho embarcado de IA. As competências demonstradas são integração de protocolos, manejo explícito de falhas e avaliação reproduzível, sujeitas à revisão acadêmica do aluno.

## Limitações e entrega

Broker público sem TLS/autenticação: exclusivamente demonstração sintética. Editor local sem exposição pública. Avisos de dependências registrados em [npm-audit.json](evidence/npm-audit.json); não se declara prontidão para produção. Nenhum e-mail real enviado. Não há vídeo, submissão FIAP ou aprovação humana presumidos.

## Histórico e atribuição

30/10/2026: inventário, implementação, testes locais/remotos e relatórios preparados com apoio de agentes de IA coordenados pelo Codex. Guilherme deve revisar e dominar o conteúdo antes de apresentar. Originais acadêmicos preservados fora da publicação.

README adaptado do [template FIAP Fase 3](https://github.com/CaiqueFiap-2026/TEMPLATE-TIAO-2026/blob/53ced5ec91571e06398e0ac9c90e58cb78ed4c02/2TIAO/FASE3/README.md). Modelo Git FIAP e logo: FIAP, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Essa atribuição não relicencia bibliotecas de terceiros nem ebooks. [Proveniência](docs/proveniencia.md).
