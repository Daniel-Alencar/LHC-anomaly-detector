import hls4ml
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model

# 1. Carregar o modelo treinado (COM A CORREÇÃO compile=False)
print("Carregando modelo Keras...")
# compile=False é o segredo aqui. Ignora o erro do 'mse'.
model = load_model('lhc_autoencoder_model.h5', compile=False)

# 2. Criar a configuração do HLS
print("Criando config...")
config = hls4ml.utils.config_from_keras_model(model, granularity='name')

# 3. Ajustar para o seu Hardware (XC7A50T)
print("Configurando parâmetros de FPGA...")

# Definindo precisão fixa (crucial para FPGA)
for layer in config['LayerName'].keys():
    config['LayerName'][layer]['Precision'] = 'ap_fixed<16,6>'
    config['LayerName'][layer]['ReuseFactor'] = 4

# 4. Converter o modelo
print("Convertendo para C++ HLS...")
hls_model = hls4ml.converters.convert_from_keras_model(
    model,
    hls_config=config,
    output_dir='projeto_fpga_hls', 
    part='xc7a50t-csg324-1',      
    backend='Vivado'              
)

# 5. Compilar e Sintetizar
print("Gerando projeto Vivado HLS... (Isso pode demorar uns minutos)")

# Tenta rodar o build se o Vivado estiver no PATH
try:
    hls_model.build(reset=True, csim=False, synth=True, cosim=False, validation=False, export=True)
    print("\n--- SUCESSO! ---")
    print("Relatório de Síntese:")
    hls4ml.report.read_vivado_report('projeto_fpga_hls')
except Exception as e:
    print(f"\n[INFO] O script gerou os arquivos C++, mas não conseguiu chamar o Vivado automaticamente.")
    print(f"Erro técnico: {e}")
    print("\nO QUE FAZER AGORA:")
    print("1. Vá até a pasta 'projeto_fpga_hls'.")
    print("2. Abra o Vivado HLS (ou Vitis HLS) manualmente.")
    print("3. No terminal do HLS, navegue até a pasta e digite: 'vivado_hls -f build_prj.tcl'")
    print("   (Ou crie um novo projeto importando os arquivos cpp/h dessa pasta).")