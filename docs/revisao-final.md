# Revisão técnica e estado de entrega

Guilherme Yamada Dantas — rm568506. 30/10/2026.

## Revisões por etapa

1. Requisitos: TXT integral e Cap01 lidos; imagem verificada como mapa mental. Matriz diferencia obrigatório, SPIFFS/Grafana opcionais e Ir Além solicitado.
2. Edge: circuito com dois sensores distintos; fila limitada, política de perdas, mutex e isolamento de rede revisados. Testes C++ exercitam FIFO, wrap, 10.000 inserções/8.000 descartes e proteção de mensagem em trânsito. Compilação ESP32 real aprovada (RAM estática 93.380 bytes, flash 785.065 bytes).
3. MQTT: testes reais no broker local e público, com 18 mensagens aceitas em cada execução final e rejeições verificadas. Dashboard exportado e inspecionado visualmente. Revisão independente encontrou validação incompleta, identidade sem dispositivo, regressão de sequência e teste sensível à latência. Correções: contrato completo, chave device/session/seq, rejeição de regressão, idade da amostra com indicação BACKLOG, polling correlacionado e fechamento do cliente em finally.
4. REST: sete testes HTTP reais, SQLite e arquivos MIME; sem SMTP. Verificadas idempotência, fronteiras, erros e recuperação após reinício. Não há ponte MQTT→REST presumida.
5. IA: notebook executado e quatro testes aprovados. Separação 720/240/240, StandardScaler só no treino, escolha de C na validação e teste reservado. Banco LIF fixo com readout logístico explicitado; não se afirma SNN treinada ponta a ponta. Métricas e limites coerentes com arquivos.
6. Relatórios: quatro relatórios PDF de duas páginas cada, acima dos mínimos exigidos para Edge/MQTT e dentro das faixas dos Ir Além. Revisão visual de todas as páginas, com referências e identificação.

## Evidências Wokwi

Projeto salvo: https://wokwi.com/projects/479273729983469569 . O sketch Web incorpora literalmente o header do buffer; circuito e bibliotecas correspondem ao projeto local. Não é apenas um link de template.

Execução inicial preservada em evidence/wokwi-initial-serial.txt: sessão 51d7ccac, coleta válida, MQTT connect=1; comando 0, fila cresceu a nove registros; comando 1, sequências 7–16 publicadas em ordem e fila drenada. evidence/wokwi-initial-node-red.json confirma recepção no consumidor. Essa execução antecede a adição de age_ms e permanece separada da evidência final.

A execução final (sessão f0da5c87) está nos arquivos evidence/wokwi-final-*: offline nas sequências 8–11, fila de quatro amostras; reenvio com age_ms de 16.040 ms para a mais antiga; BPM alterado de 75 para 180; recepção por assinante MQTT independente e Node-RED, com alerta e screenshot. MQTT público e Wokwi são serviços externos: primeiras tentativas de conexão podem falhar e a aplicação tenta novamente sem suspender a coleta. Nenhuma execução física foi realizada.

## Limitações materiais

- Fila volátil; não sobrevive a reinício. dropped mede descarte por saturação, não todas as perdas MQTT.
- QoS 0 não confirma consumo; broker público sem TLS/autenticação, apenas sintéticos.
- Timestamp do gráfico é recepção; age_ms informa atraso de aquisição no envio, não latência total de transporte.
- Dashboard mostra o último dispositivo recebido no tópico; a demonstração deve usar um produtor por vez. Não é painel multi-paciente.
- Avisos transitivos npm preservados; editor restrito a loopback. Não é implantação de produção.
- REST e IA têm produtores próprios sintéticos e não são alimentados automaticamente pelo firmware.
- IA: uma distribuição e semente, sem evidência clínica, energética ou de implantação embarcada.

## Pendências humanas

Gravar apresentação <=4 minutos, publicar no YouTube como não listado e inserir URL verificada no README; revisar academicamente conteúdo e autoria assistida; realizar submissão no Portal do Aluno. Código e evidências técnicas não substituem essas etapas.

## Fechamento técnico

A checagem de artefatos passou: links internos, JSON, hashes do experimento, notebook sem erros, partições disjuntas, equivalência SHA-256 do sketch Web e origem Wokwi observada. Testes REST (7) e IA (4) repetidos pelo integrador passaram. Uma tentativa no runtime PDF falhou por ausência de sklearn; foi preservada, e o teste foi repetido com o Python 3.12 do experimento. Serviços temporários MQTT/Node-RED foram encerrados ao final.
