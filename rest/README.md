# Ir Além 1 - REST e automação de e-mail simulado

Python 3.10+; apenas biblioteca padrão. Sem instalação, SMTP ou serviços externos.
Execute a partir da raiz do repositório:

```sh
python3 rest/server.py
# Em outro terminal:
python3 rest/client.py
python3 -m unittest discover -s rest -p 'test_*.py' -v
# Demo integrada que encerra o servidor e preserva evidências:
python3 rest/run_evidence.py
```

Servidor ligado exclusivamente a `127.0.0.1:8000`; `--port` e `--data-dir`
permitem mudar porta/pasta. `Ctrl+C` encerra. Cliente aceita `--base` apenas loopback.
A demonstração cria duas amostras, normal e alerta, e consulta cada uma por GET.
SQLite guarda amostras em `rest/runtime/`; alertas geram arquivos em `rest/runtime/outbox/`.
A demo integrada grava em uma nova pasta datada em `docs/rest/evidence/`.

## Contrato

- `GET /health`: status 200 e modo de simulação.
- `POST /samples`: JSON, até 4096 bytes, criação 201.
- Repetição do mesmo `sample_id` e conteúdo: 200 sem e-mail duplicado.
- Mesmo ID com conteúdo diferente: 409.
- `GET /samples/{sample_id}`: 200 ou 404.
- `GET /samples`: até 100 registros mais recentes; explicita limite e ordem.
- Erros: 400 para dados inválidos; 413 corpo fora do limite; 415 tipo de mídia.

```json
{"sample_id":"sintetico-001","synthetic":true,"timestamp":"2026-10-30T00:00:00-03:00","bpm":135,"temperature_c":39}
```

Os cinco campos são obrigatórios; campos extras são rejeitados. `sample_id` aceita
1-64 letras ASCII, números, `_` ou `-`; timestamp ISO 8601 exige fuso.
Valores finitos: bpm 0-250, temperatura -40 a 80 °C. São limites de entrada do
experimento, não faixas clínicas. Valores booleanos não são aceitos como números.

Regras demonstrativas: bpm **>120** e temperatura **>38 °C**. Nos limites exatos não
há alerta. A temperatura pode vir de DHT22 ambiental; não representa medição de
febre. Não há regra de ausência de movimento porque o contrato não mede movimento.

## Segurança e limites

O protótipo aceita apenas `synthetic: true`, mas não verifica a procedência real dos
valores; o operador deve usar apenas amostras inventadas. Não há autenticação/TLS
ou validação clínica. Não expor o servidor à rede. Endereços de e-mail usam `.invalid`.
A mensagem MIME é construída com `email` e salva em disco: não existe chamada SMTP.
O projeto original de aula foi consultado sem copiar credenciais ou executar envio.

Uma transação SQLite armazena amostra, resultado e conteúdo do e-mail antes de
materializar o `.eml`. Repetição/reinício reconstitui um arquivo faltante. Isso cobre
interrupção entre commit e escrita, mas não falha de disco permanente. O servidor
é sequencial e educativo, sem filas distribuídas, paginação completa, retenção
automática ou dimensionamento produtivo. Dados não são enviados ao MQTT por este
módulo: a integração demonstrada aqui é cliente Python → REST → regras → arquivo.
