# Ir Além 2 — IA em séries temporais de saúde

**Guilherme Yamada Dantas | rm568506 | CardioIA Conectada**

## Página 1 — objetivo, dados e método

O experimento compara regressão logística com uma rede neuromórfica simples baseada em Leaky Integrate-and-Fire (LIF). A finalidade é educacional: reconhecer cenários sintéticos de elevação de frequência cardíaca. Nenhum dado pertence a um paciente, e os rótulos não representam diagnósticos. As séries não foram capturadas no Wokwi ou em ESP32; foram geradas em Python, em um experimento independente.

Foram produzidas 1.200 séries independentes de 180 amostras de BPM, a 1 Hz, com semente 568506. Cada série representa um indivíduo fictício distinto. O gerador combina frequência basal, ruído autocorrelacionado, oscilação e episódios de elevação. A classe 1 recebe episódios geralmente mais longos/intensos; a classe 0 também pode conter elevações, criando sobreposição. Há 600 exemplos por classe. O alvo é o cenário gerador, e não uma regra médica de taquicardia.

A divisão estratificada é de 720 indivíduos para treino, 240 para validação e 240 para teste. Nenhum indivíduo cruza partições. A normalização StandardScaler é ajustada exclusivamente no treino, dentro de um pipeline. A regularização C é escolhida entre 0,1, 1 e 10 pelo F1 de validação; o limiar de classificação permanece em 0,5. O modelo escolhido é avaliado no teste sem retreino e sem escolher parâmetros usando suas respostas. Os IDs das partições ficam registrados em metrics.json.

A regressão logística utiliza oito atributos fixos: média, desvio-padrão, mínimo, máximo, percentil 90, fração acima de 120 BPM, variação absoluta média entre amostras e diferença de média entre os últimos e primeiros 30 segundos. A fração acima de 120 é apenas um atributo didático, sem interpretação clínica validada.

A rede simples possui um banco de 24 neurônios LIF: três canais de entrada, quatro ganhos e duas constantes de integração. Em cada passo, aplica-se v = v + (-v + I)/tau; ao atingir 1, emite-se um spike e reinicia-se v em zero. O passo é normalizado por amostra; não equivale a um milissegundo biológico. A entrada usa nível de BPM e variação temporal. Taxas de disparo em três segmentos geram 72 atributos. Um readout logístico aprende a classificação. O banco LIF tem pesos fixos: esta é uma arquitetura híbrida, sem STDP ou treinamento ponta a ponta.

<!-- PAGEBREAK -->

## Página 2 — resultados reais, discussão e evidências

A avaliação local executada produziu os resultados abaixo, no mesmo teste de 240 indivíduos (120 por classe). Ambos selecionaram C = 10 na validação.

| Medida de teste | Logística | LIF + readout logístico |
|---|---:|---:|
| Acurácia | 0,8583 | 0,7625 |
| Precisão, classe 1 | 0,8981 | 0,7692 |
| Recall, classe 1 | 0,8083 | 0,7500 |
| F1, classe 1 | 0,8509 | 0,7595 |
| ROC-AUC | 0,9429 | 0,8225 |
| TN / FP / FN / TP | 109 / 11 / 23 / 97 | 93 / 27 / 30 / 90 |

A logística apresentou maior F1 e menor número de falsos negativos: 23 versus 30. O LIF não trouxe vantagem preditiva nesta configuração. A comparação envolve representações com capacidades diferentes; não isola causalmente o efeito de usar spikes. Os parâmetros do banco foram fixados no código e não foi feita busca extensa de arquiteturas.

O tempo mediano de transformação e inferência em lote de 240 janelas, em sete repetições locais, foi aproximadamente 0,496 ms para a logística e 7,116 ms para LIF + readout. Estes valores não incluem aquisição de 180 segundos de sinal, transmissão MQTT ou execução embarcada. São observações de CPU no computador local, variáveis entre execuções. Não houve medição de potência, energia ou consumo de bateria. O Cap03, seções 3.1–3.3, motiva justamente distinguir o algoritmo da arquitetura de execução.

A evidência é composta por notebook executado, métricas JSON, previsões CSV, dataset NPZ com SHA-256 e figuras de séries e spikes. Quatro testes verificaram reprodutibilidade e balanceamento do gerador, resposta silenciosa/ativa do LIF, independência de estado entre indivíduos e finitude dos atributos. Todos passaram. A versão executada usa Python 3.12, NumPy 2.5.3 e scikit-learn 1.6.0; versões detalhadas estão registradas no artefato de métricas.

O desempenho descreve uma distribuição artificial com uma única semente. Não demonstra detecção de arritmia, generalização clínica, eficiência energética ou implantação no ESP32. Uma próxima etapa deve repetir sementes, estudar calibração/erros, avaliar dados externos consentidos e medir hardware real.

**Referências:** FIAP, Cap03, *Cérebros de Silício na Era dos Chips Neuromórficos*, seções 3.1–3.3; Gerstner et al., *Neuronal Dynamics*, seção 1.3, https://neuronaldynamics.epfl.ch/online/Ch1.S3.html; documentação LogisticRegression, https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html.
