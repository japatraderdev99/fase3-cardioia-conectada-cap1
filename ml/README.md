# Ir Além 2 — comparação em séries temporais sintéticas

Responsável: Guilherme Yamada Dantas, rm568506.

Este é um experimento independente do firmware. Não utiliza pacientes reais, dados do ESP32 ou registros clínicos. O rótulo é um cenário latente do gerador, sem significado diagnóstico.

## Reproduzir

Na raiz do repositório:

```sh
python3 -m venv ml/.venv
ml/.venv/bin/pip install -r ml/requirements.txt
ml/.venv/bin/python ml/experiment.py
ml/.venv/bin/python -m unittest discover -s ml -v
ml/.venv/bin/jupyter nbconvert --to notebook --execute --inplace ml/comparacao_logistica_lif.ipynb
```

O notebook já contém saídas de uma execução local real. Executá-lo novamente sobrescreve os resultados reproduzíveis e atualiza tempos, que variam com o ambiente. Preserve a versão anterior via Git antes de uma nova execução.

## Arquivos e interpretação

- `experiment.py`: geração determinística, split por indivíduo, banco LIF e avaliação.
- `comparacao_logistica_lif.ipynb`: método comentado, execução, figuras, análise crítica e testes.
- `results/metrics.json`: métricas, versões, IDs de treino/validação/teste e SHA-256 do dataset.
- `results/predictions.csv`: probabilidade, classe prevista e alvo de cada indivíduo de teste.
- `results/synthetic_series.npz`: arrays `bpm`, `labels` e `synthetic_ids`; 1.200 × 180 amostras.
- `tests.log`: execução dos quatro testes unitários.
- `../docs/ia/relatorio-comparativo.md`: fonte paginada do relatório comparativo.

O modelo LIF é um banco fixo de 24 neurônios com readout logístico treinável. Não se afirma treinamento neuromórfico ponta a ponta. A logística usa oito resumos e o banco LIF 72 taxas segmentadas, portanto a comparação avalia pipelines diferentes. O treino do readout não é STDP.

Resultado de teste: F1 0,8509 na logística; F1 0,7595 em LIF + readout. O segundo método teve desempenho inferior nesta única distribuição e semente. Não se mediu energia nem executou em hardware neuromórfico. Vídeo e URL pública continuam dependentes da entrega geral.
