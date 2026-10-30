# Roteiro de demonstração — até 4 minutos

Guilherme Yamada Dantas, RM rm568506. Roteiro de referência. A apresentação final tem 3min07s: https://youtu.be/uBMAaqeuFoI .

| Tempo | Tela e fala sugerida |
|---|---|
| 0:00–0:20 | Identificação, objetivo CardioIA, dados sintéticos e ausência de uso clínico. |
| 0:20–1:00 | Circuito Wokwi: ESP32, DHT22, MPU6050 e potenciômetro BPM. Mostrar coleta e limites de cada grandeza. |
| 1:00–1:35 | Serial: comando 0, novas amostras na fila; comando 1, reenvio se broker responder. Explicar 2.000 registros, descarte do mais antigo, RAM volátil e QoS 0. Se nuvem falhar, mostrar a falha e a evidência host separadamente. |
| 1:35–2:05 | Node-RED: gráfico BPM, gauge temperatura e alerta. Alterar estímulo e comprovar recepção; mostrar estado sem dados recentes. |
| 2:05–2:30 | REST: executar cliente, POST/GET e abrir .eml. Dizer explicitamente que não houve envio real. |
| 2:30–3:25 | Notebook: 1.200 séries, split 720/240/240, logística vs banco LIF com readout; F1 0,8509 vs 0,7595. Mostrar matriz de confusão, reconhecer menor desempenho LIF. |
| 3:25–3:45 | Limitações: sintético, uma semente, sem validação clínica/energia; apontar repositório e relatórios. |

Vídeo publicado como **não listado**, com link no README. A edição final reúne os trechos acima com legendas na tela.
