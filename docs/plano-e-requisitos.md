# CardioIA Conectada — plano e matriz de requisitos

Responsável acadêmico: Guilherme Yamada Dantas — rm568506. Data: 30/10/2026.

## Inventário e revisão inicial

Enunciado TXT lido integralmente; Cap01 lido integralmente (8 páginas); captura 23.48.40 inspecionada visualmente. A imagem é mapa mental das fases, NÃO tabela de avaliação. A captura posterior de 30/10/2026 às 00.22.18 contém a rubrica: cinco critérios de 2 pontos. A pendência dos pesos foi resolvida com essa fonte. Cap02, Cap03, Cap08 e Cap09 orientam implementação, sem redistribuir ebooks pessoais nem exemplos contendo credenciais.

Repositório público indicado foi inspecionado com gh e git ls-remote e clonado vazio. Diretório exclusivo CardioIAConectadaCap1. EnterpriseChallengeSPRINT1 e QUIZ não são alvos de escrita.

Template consultado: CaiqueFiap-2026/TEMPLATE-TIAO-2026, commit 53ced5ec91571e06398e0ac9c90e58cb78ed4c02, 2TIAO/FASE3/README.md. README adapta identificação, objetivos, conteúdos, tecnologias, projetos, competências e atribuição. Pastas por subsistema evitam duplicar código; índice 2TIAO/FASE3 aponta à raiz.

## Etapas e critérios de passagem

1. Inventário e requisitos: revisão concluída; pesos confirmados pela captura posterior.
2. Firmware: revisar circuito, coleta, limite de fila, falhas e reconexão; compilar e testar buffer.
3. MQTT/Node-RED: importar fluxo, executar broker e publisher de teste, conferir gráfico/gauge/alerta e rejeição de dados inválidos. Teste de host não prova ESP32/Wokwi.
4. Ir Além 1: testar HTTP real local, regras de risco e arquivos de e-mail simulados; nenhum envio real.
5. Ir Além 2: executar notebook, verificar separação dos dados, métricas e interpretação sem extrapolação clínica.
6. Integração: revisar contratos, executar testes, gerar relatórios paginados, inspecionar renders e registrar limitações.
7. Entrega: preparar README, roteiro <=4 min, checklist Wokwi/YouTube e submissão; links somente após existência verificada.

## Matriz rastreável

| ID | Classe | Requisito | Artefato/verificação |
|---|---|---|---|
| P1-01 | obrigatório | ESP32 Wokwi + >=2 sensores, DHT22 obrigatório | firmware; circuito e compilação; execução Wokwi separada |
| P1-02 | opcional | SPIFFS | não adotado; fila RAM volátil documentada |
| P1-03 | obrigatório | booleano online, Serial e sincronização | firmware; comandos e cenários offline |
| P1-04 | obrigatório | resiliência limitada, política e capacidade | fila 2000, testes overflow/FIFO |
| P1-05 | obrigatório | C++ comentado, link Wokwi, relatório >=1p | firmware, relatório Edge; link depende publicação Wokwi |
| P2-01 | obrigatório | MQTT para broker externo | firmware + teste host MQTT; evidências separadas |
| P2-02 | obrigatório | Node-RED gráfico de sinal, gauge e alerta | dashboard/flows.json; testes e captura |
| P2-03 | obrigatório | export/prints e relatório >=2p | dashboard e relatório MQTT |
| P2-04 | opcional | Grafana | fora de escopo, Node-RED adotado |
| A1-01 | Ir Além solicitado | cliente REST POST/GET, riscos, e-mail simulado | rest; testes HTTP/.eml |
| A1-02 | Ir Além solicitado | relatório 1–2p | relatório REST |
| A2-01 | Ir Além solicitado | notebook, logística vs LIF/FHN | ml; notebook executado e métricas |
| A2-02 | Ir Além solicitado | repo público + README | remoto já público; publicação código deve ser verificada |
| A2-03 | Ir Além solicitado | relatório 2p | relatório IA |
| A2-04 | Ir Além solicitado | vídeo <=4min não listado + README | roteiro; gravação humana e URL pendentes |

Ir Além é extensão opcional do enunciado, mas integra o escopo explicitamente solicitado. Dados exclusivamente sintéticos; DHT22 representa temperatura ambiental, não mede temperatura corporal clinicamente. Limiares são regras didáticas, não diagnóstico.

## Rubrica confirmada e evidências

Fonte: captura fornecida pelo usuário em 30/10/2026 às 00.22.18, inventariada por SHA-256. Os pesos abaixo transcrevem a tabela da atividade; o atendimento técnico é uma avaliação interna baseada em evidências, não nota atribuída pela FIAP.

| Critério oficial | Pontos possíveis | Evidências existentes | Revisão técnica |
|---|---:|---|---|
| Leitura de sensores | 2 | `firmware/sketch.ino`, `firmware/diagram.json`, `evidence/wokwi-final-serial.txt` e `evidence/wokwi-final-mqtt.jsonl`: DHT22 e MPU6050 com leituras válidas | Demonstrado em simulação; BPM é controle sintético adicional |
| Implementação de resiliência offline (Edge Computing) | 2 | Serial final: comando 0, coleta das sequências 8–11 e fila de quatro amostras; comando 1 e reenvio. `firmware/evidence/host-buffer-test.txt`: limite de 2.000 e descarte por saturação | Demonstrado; RAM volátil e limite de QoS 0 documentados |
| Envio via MQTT e integração com broker | 2 | `evidence/wokwi-final-mqtt.jsonl`, `evidence/wokwi-final-alert-state.json`, `evidence/mqtt-public.json` | Recepção real via broker público, com evidência Wokwi separada do publisher host |
| Dashboard funcional e alertas automáticos | 2 | `dashboard/flows.json`, `evidence/dashboard-wokwi-final.png`, testes MQTT e snapshots de alerta | Gráfico, gauge e alerta demonstrados |
| Documentação clara (código + relatórios) | 2 | README, código comentado, relatórios Edge/MQTT e `evidence/pdf-qa.json`; documentação dos Ir Além adicional | Artefatos produzidos e revisados tecnicamente; clareza acadêmica sujeita à avaliação humana |
| **Total possível** | **10** | Cobertura documental dos cinco critérios | **Não equivale a nota 10 garantida** |

A rubrica afirma que SPIFFS não será computado devido à limitação dos simuladores; implementá-lo em chip real é considerado ir além. Portanto, a ausência de SPIFFS nesta solução simulada não é uma lacuna dessa pontuação. Os desafios REST/e-mail e IA continuam como extensões solicitadas; não há peso adicional indicado nessa tabela e não se presume bônus.

A rubrica complementa o enunciado e não elimina seus entregáveis: link Wokwi, códigos, export/prints e relatórios. O vídeo não listado de até quatro minutos permanece pendente no Ir Além 2, junto com revisão humana e submissão.
