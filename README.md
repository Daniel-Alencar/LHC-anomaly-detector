# LHC Beam Anomaly Detector on FPGA

Este projeto implementa um sistema de detecção de anomalias em tempo real para sinais de Instrumentação de Feixe (Beam Instrumentation) do Large Hadron Collider (LHC). Utilizando conceitos de Edge AI, o sistema roda um Autoencoder Quantizado diretamente em hardware (FPGA), garantindo latência determinística na ordem de nanossegundos.

Esta versão do projeto foi inteiramente migrada para um fluxo **Open-Source Hardware (OSHW)**, utilizando as ferramentas do projeto YosysHQ para contornar o uso de IDEs proprietárias e pesadas, provando a viabilidade de ferramentas livres para instrumentação científica de ponta.

## Sobre o Projeto

Em aceleradores de partículas de alta energia como o LHC, a detecção rápida de instabilidades no feixe (ex: *drifts*, perdas de feixe localizadas, oscilações transversais) é crítica para a segurança do equipamento. 

Este projeto propõe uma arquitetura onde sinais simulados de sensores do acelerador (ex: BPMs - *Beam Position Monitors*) são processados por uma Rede Neural Profunda (Autoencoder) embutida na FPGA. O modelo aprende o comportamento "nominal" do feixe e aciona uma *flag* de anomalia caso o erro de reconstrução ultrapasse um limite seguro.

### Principais Características
* **Algoritmo:** Autoencoder (Dense Layers) quantizado para precisão fixa (`ap_fixed<16,6>`).
* **Ferramentas de Síntese:** `hls4ml` (para tradução de Keras para C++/Verilog) e `OSS-CAD-Suite` (Yosys, NextPNR) para Place & Route lógico.
* **Desempenho Alcançado:** Latência de inferência em nanossegundos, operando com o clock nativo de 25 MHz.
* **Interface de Teste:** Barramento UART customizado com Interface Gráfica (GUI) em Python para injeção de falhas e monitoramento de erro de reconstrução em tempo real.

---

## Requisitos

### Hardware
* **Placa:** Colorlight i9+ v7.2 (ou similar).
* **FPGA:** Lattice ECP5 (LFE5U-45F).
* **Conexão:** Porta USB para comunicação serial e programação JTAG.

### Software
* **Machine Learning:** Python 3.10+, TensorFlow/Keras, Scikit-learn, Matplotlib.
* **Interface Gráfica:** `tkinter`, `pyserial`.
* **Síntese High-Level:** `hls4ml` (com pacote de profiling) e `Vitis HLS` (usado apenas como motor de tradução C++ para Verilog em background).
* **EDA Open-Source:** `OSS-CAD-Suite` (contém Yosys, NextPNR e ecppack).
* **Gravação:** `openFPGALoader`.

---

## Passo a Passo de Execução

O fluxo do projeto é dividido em 4 fases principais: desde o treinamento da IA no PC até a validação na placa via interface gráfica.

### Fase 1: Treinamento do Modelo (Python)
Gera os dados sintéticos do feixe, treina o Autoencoder e salva o modelo.

1. Crie um ambiente virtual e instale as dependências:
```bash
pip install tensorflow numpy matplotlib scikit-learn pyserial "hls4ml[profiling]"
```

2. Execute o script de treinamento:

```bash
python3 train_lhc_model.py
```

*Resultado esperado:* O gráfico de distribuição de erros será exibido, comprovando a separação entre dados nominais e anomalias. O arquivo `lhc_autoencoder_model.h5` será gerado.

### Fase 2: Síntese de Alto Nível (HLS)

Converte o modelo Keras `.h5` em código Verilog otimizado usando `hls4ml`.

1. Execute o conversor:

```bash
python3 convert_to_hls.py
```

*(Nota: O script está configurado com `ReuseFactor = 4` para adequar o uso de multiplicadores físicos (DSPs) disponíveis na FPGA Lattice ECP5-45F).*

2. Gere o código Verilog (RTL). No terminal, entre na pasta do projeto HLS e execute:

```bash
cd projeto_fpga_hls
vitis_hls -f build_prj.tcl
```

*Resultado esperado:* O HLS traduzirá a matemática da IA para hardware. Os arquivos `.v` contendo a rede neural ficarão disponíveis na pasta `projeto_fpga_hls/myproject_prj/solution1/syn/verilog/`.

### Fase 3: Integração de Hardware e Compilação (OSS-CAD-Suite)

Substitui o Vivado por ferramentas livres para mapear a lógica da Rede Neural, os controladores Seriais e os Pinos Físicos para dentro do chip Lattice ECP5.

1. Certifique-se de que sua pasta de trabalho (`src/` ou similar) contém:
* O `Makefile` do projeto.
* O arquivo de restrições de pinos `colorlight.lpf`.
* O módulo integrador principal (`uart_bridge.v`).
* Os módulos receptores e transmissores seriais (`uart_rx.v` e `uart_tx.v`).


2. Ative o ambiente do OSS-CAD-Suite no terminal (ajuste o caminho se necessário):

```bash
source ~/oss-cad-suite/environment
```

3. Execute a compilação completa (Síntese, Place & Route, Bitstream):

```bash
make
```

*Resultado esperado:* O `Yosys` inferirá os blocos DSP para as multiplicações, o `NextPNR` fará o roteamento e o `ecppack` gerará o arquivo `lhc_detector.bit`.

### Fase 4: Gravação e Validação na Prática

O painel de controle interativo envia vetores de 128-bits para a placa via cabo USB (UART) e recebe as previsões da Rede Neural.

1. **Gravar na Placa:**
Utilize o `openFPGALoader` para enviar o arquivo gerado para a placa (o comando já está embutido no Makefile):

```bash
make prog
```

*(Se necessário, ajuste a flag de cabo no Makefile para coincidir com o seu programador, ex: `-c ch347` ou `-c cmsisdap`).*

2. **Abrir a Interface Gráfica:**
Inicie o Dashboard em Python desenvolvido para o sistema:

```bash
python3 lhc_gui.py
```

**Passo a Passo da Simulação no GUI:**

* **A) Conexão:** Selecione a porta correspondente à FPGA (ex: `/dev/ttyUSB0`) e clique em *Conectar*. A UART operará a 115200 bps.

* **B) Feixe Nominal (Calibração):**
  * Clique no botão **Nominal**. A interface enviará um vetor nulo (`0x00...`).
  * **O que observar:** Como o modelo opera internamente em `ap_fixed<16,6>`, valores normais são reconstruídos com extrema precisão. O Erro MAE (Mean Absolute Error) mostrado na tela será residual (barra verde), comprovando que o feixe está estável e reconhecido pela rede.


* **C) Anomalia e Falha Crítica:**
  * Clique em **Anomalia Suave** ou **Falha de Sensor**.
  * **O que observar:** Ao enviar valores que saturam o *espaço latente* do Autoencoder (ex: `0xFF...`, lido pelo hardware como valores máximos negativos/positivos em complemento de dois), a Rede Neural não consegue reconstruir o padrão.
  * O sinal devolvido pela FPGA será drasticamente diferente do enviado. A interface calculará o desvio instantaneamente, elevando o Erro MAE a valores alarmantes (barra vermelha). No mundo real do CERN, este pico ativaria o sistema *Interlock* de segurança do LHC.
