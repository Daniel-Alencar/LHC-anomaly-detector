# LHC Beam Anomaly Detector on FPGA

Este projeto implementa um sistema de detecção de anomalias em tempo real para sinais de Instrumentação de Feixe (Beam Instrumentation) do Large Hadron Collider (LHC). Utilizando conceitos de Edge AI, o sistema roda um Autoencoder Quantizado diretamente em hardware (FPGA), garantindo latência determinística na ordem de nanossegundos.

## Sobre o Projeto

Em aceleradores de partículas de alta energia como o LHC, a detecção rápida de instabilidades no feixe (ex: *drifts*, perdas de feixe localizadas, oscilações transversais) é crítica para a segurança do equipamento. 

Este projeto propõe uma arquitetura onde sinais simulados de sensores do acelerador (ex: BPMs - *Beam Position Monitors*) são processados por uma Rede Neural Profunda (Autoencoder) embutida na FPGA. O modelo aprende o comportamento "nominal" do feixe e aciona uma *flag* de anomalia caso o erro de reconstrução ultrapasse um limite seguro.

### Principais Características
* **Algoritmo:** Autoencoder (Dense Layers) quantizado para precisão fixa (`ap_fixed<16,6>`).
* **Ferramentas de Síntese:** `hls4ml` para tradução de Keras/TensorFlow para C++ HLS.
* **Desempenho Alcançado:** Latência de ~28 ciclos de clock (~140 ns a 100 MHz).
* **Interface de Teste:** Vivado VIO (Virtual Input/Output) para injeção de falhas em tempo real via JTAG.

---

## Requisitos

### Hardware
* **Placa:** Colorlight i9+ (ou placa de desenvolvimento similar).
* **FPGA:** Xilinx Artix-7 (XC7A50T).
* **Programador:** Interface JTAG via CH347 (ou cabo Xilinx oficial).

### Software
* **Machine Learning:** Python 3.10+, TensorFlow/Keras, Scikit-learn, Matplotlib.
* **Síntese High-Level:** `hls4ml` (com pacote de profiling).
* **EDA Xilinx:** Vitis HLS 2023.2 e Vivado 2023.2.
* **Gravação:** `openFPGALoader` (essencial para programação via CH347 no Linux).

---

## Passo a Passo de Execução

O fluxo do projeto é dividido em 4 fases principais: desde o treinamento da IA no PC até a implementação na FPGA.

### Fase 1: Treinamento do Modelo (Python)
Gera os dados sintéticos do feixe, treina o Autoencoder e salva o modelo.

1. Crie um ambiente virtual e instale as dependências:

```bash
pip install tensorflow numpy matplotlib scikit-learn "hls4ml[profiling]"
```

2. Execute o script de treinamento:
```bash
python3 train_lhc_model.py

```

*Resultado esperado:* O gráfico de distribuição de erros será exibido, comprovando a separação entre dados nominais e anomalias. O arquivo `lhc_autoencoder_model.h5` será gerado.

### Fase 2: Síntese de Alto Nível (HLS)

Converte o modelo Keras `.h5` em um IP Core de hardware otimizado usando `hls4ml`.

1. Execute o conversor:
```bash
python3 convert_to_hls.py

```


*(Nota: O script está configurado com `ReuseFactor = 4` para equilibrar o uso de DSPs da placa).*

2. Empacote o IP Core no Vitis HLS. Entre na pasta gerada e execute o script de empacotamento:
```bash
cd projeto_fpga_hls
vitis_hls -f build_prj.tcl

```

Se aparecer "command not found", então execute este comando dentro do terminal do Vitis Unified IDE (entrando com `cd` na pasta "projeto_fpga_hls" e executando `vitis_hls -f build_prj.tcl` logo em seguida).

Após isso, no mesmo terminal, execute:

```bash
echo "open_project myproject_prj" > package.tcl
echo "open_solution solution1" >> package.tcl
echo "export_design -format ip_catalog" >> package.tcl
echo "exit" >> package.tcl

```

```bash
vitis_hls -f package.tcl

```

*Resultado esperado:* Um arquivo `.zip` será criado em `myproject_prj/solution1/impl/ip/`.

Ou seja, agora temos o IP Core (o bloco de hardware) disponível para ser usado no programa Vivado.

Também temos os códigos Verilog e VHDL gerados. O caminho exato é:

```Plaintext
projeto_fpga_hls/myproject_prj/solution1/syn/

```
Dentro dessa pasta syn, você verá duas subpastas:

- `verilog/` (Contém todos os arquivos .v)
- `vhdl/` (Contém todos os arquivos .vhd)

### Fase 3: Integração de Hardware (Vivado)

Monta o sistema completo (Rede Neural + Gerenciador de Clock + Painel de Controle).

1. Abra o Vivado e crie um novo projeto RTL selecionando o chip **XC7A50T**.
2. Adicione o repositório do IP: `Settings -> IP -> Repository` e aponte para a pasta `ip` gerada na Fase 2.
3. Crie um **Block Design** e adicione os seguintes blocos:
* **myproject:** Seu Autoencoder.
* **Clocking Wizard:** Configurado para entrada de 25 MHz e saída de 100 MHz.
* **VIO (Virtual Input/Output):** Configurado com 9 `probe_in` (saídas da rede) e 3 `probe_out` (vetor de 128 bits de entrada, reset e start).


4. Conecte os sinais no diagrama (Clock  IP/VIO, VIO  IP) de acordo com o arquivo `design.png`.
5. Gere o **HDL Wrapper** do block design.
6. Adicione o arquivo de *Constraints* (`.xdc`) mapeando o clock de entrada para o pino correto da Colorlight (ex: pino `K4`).
7. Clique em **Generate Bitstream** e aguarde a compilação.

### Fase 4: Gravação e Validação na Prática

Devido a particularidades de drivers de conversores USB-JTAG genéricos (como o CH347) no Linux, a gravação é feita via terminal, e a validação via Vivado.

1. **Gravar na Placa:**
Localize o arquivo `.bit` gerado pelo Vivado (em `.../impl_1/` do projeto) e utilize o `openFPGALoader` para gravar o arquivo na placa:
```bash
openFPGALoader -b colorlight-i9 <arquivo_bitstream>.bit

```
*(Ou você utilizará este comando ou um similar a este. Recomendo pesquisar na internet o comando correto).*

*(A placa indicará configuração bem-sucedida).*

2. **Testar com VIO (Vivado Hardware Manager):**
* Abra o Vivado, vá em **Open Hardware Manager** e clique em **Auto Connect**.
* A aba do painel VIO (`hw_vio_1`) será aberta.
* **Operação normal:** Coloque o sinal de `Reset` em 1 e depois 0. Coloque `Start` em 1.
* **Calibração:** Insira `00000000...` no vetor de entrada (representando os sensores nominais). As saídas devem tender a valores residuais baixos.
* **Injeção de Anomalia:** Altere parte da entrada para valores altos (ex: `FFFF`). Observe a saída da rede neural distorcer em tempo real na interface, indicando a detecção da falha no feixe simulado!
