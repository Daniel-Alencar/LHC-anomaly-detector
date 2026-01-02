import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense
from tensorflow.keras.optimizers import Adam
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

# ==========================================
# 1. Configurações do "Simulador LHC"
# ==========================================
# Vamos simular 8 sensores (ex: 4 BPMs Horizontais e 4 Verticais)
NUM_SENSORS = 8 
NUM_SAMPLES = 10000 

# Semente para reprodutibilidade
np.random.seed(42)

print("--- 1. Gerando Dados Sintéticos do Feixe ---")

# --- Geração de Dados NORMAIS (Beam Stable) ---
# O feixe ideal tem ruído gaussiano em torno de zero (orbit correction)
# Adicionamos uma leve correlação entre sensores vizinhos (física real)
X_normal = np.random.normal(loc=0.0, scale=0.5, size=(NUM_SAMPLES, NUM_SENSORS))

# --- Geração de Dados ANÔMALOS (Para teste apenas) ---
# Tipo 1: Drift (O feixe começa a desviar lentamente)
X_drift = np.random.normal(loc=2.0, scale=0.5, size=(100, NUM_SENSORS))

# Tipo 2: Spike (Instabilidade súbita, ex: falha de ímã)
X_spike = np.random.normal(loc=0.0, scale=0.5, size=(100, NUM_SENSORS))
X_spike[:, 0] = 5.0  # O primeiro sensor lê um valor absurdo

# Juntamos tudo para teste, mas treinamos APENAS com X_normal
X_test_anomalies = np.vstack([X_drift, X_spike])

# Divisão Treino/Validação (Usamos apenas dados normais para treino!)
X_train, X_test = train_test_split(X_normal, test_size=0.2, random_state=42)

print(f"Dados de Treino: {X_train.shape}")
print(f"Dados de Teste (Normais): {X_test.shape}")
print(f"Dados de Teste (Anomalias): {X_test_anomalies.shape}")

# ==========================================
# 2. Definição do Autoencoder (Otimizado para FPGA)
# ==========================================
# Arquitetura pequena para caber fácil no XC7A50T e ter baixa latência
# Input(8) -> Enc(6) -> Bottleneck(3) -> Dec(6) -> Output(8)

input_dim = X_train.shape[1]

# Encoder
input_layer = Input(shape=(input_dim,), name='input_layer')
encoder = Dense(6, activation='relu', name='encoder_1')(input_layer)
bottleneck = Dense(3, activation='relu', name='bottleneck')(encoder) # Latent space

# Decoder
decoder = Dense(6, activation='relu', name='decoder_1')(bottleneck)
output_layer = Dense(input_dim, activation='linear', name='output_layer')(decoder)

# Modelo Completo
autoencoder = Model(inputs=input_layer, outputs=output_layer)

# Compilação
# MSE (Mean Squared Error) é excelente para detecção de anomalias
autoencoder.compile(optimizer=Adam(learning_rate=0.001), loss='mse')

autoencoder.summary()

# ==========================================
# 3. Treinamento
# ==========================================
print("\n--- 2. Iniciando Treinamento ---")
history = autoencoder.fit(
    X_train, X_train, # Autoencoder: entrada == saída desejada
    epochs=50,
    batch_size=32,
    validation_data=(X_test, X_test),
    shuffle=True,
    verbose=0 # Mude para 1 se quiser ver o progresso linha a linha
)
print("Treinamento concluído.")

# ==========================================
# 4. Validação e Salvamento
# ==========================================
print("\n--- 3. Validando Detecção de Anomalias ---")

# Função para calcular erro de reconstrução (MSE)
def get_mse(data):
    reconstructions = autoencoder.predict(data)
    mse = np.mean(np.power(data - reconstructions, 2), axis=1)
    return mse

mse_normal = get_mse(X_test)
mse_anomalies = get_mse(X_test_anomalies)

print(f"Erro Médio (Normal): {np.mean(mse_normal):.4f}")
print(f"Erro Médio (Anomalia): {np.mean(mse_anomalies):.4f}")

# Definindo um Threshold simples
threshold = np.max(mse_normal)
detected = sum(mse_anomalies > threshold)
print(f"Detectou {detected} de {len(mse_anomalies)} anomalias injetadas.")

# Plotagem dos resultados
plt.figure(figsize=(10,6))
plt.hist(mse_normal, bins=50, alpha=0.7, label='Normal (Treino)', color='blue')
plt.hist(mse_anomalies, bins=50, alpha=0.7, label='Anomalias (Injetadas)', color='red')
plt.axvline(threshold, color='k', linestyle='dashed', linewidth=2, label=f'Threshold: {threshold:.2f}')
plt.xlabel('Erro de Reconstrução (MSE)')
plt.ylabel('Quantidade de Amostras')
plt.title('Detecção de Anomalias: Normal vs Anômalo')
plt.legend()
plt.show()

# ==========================================
# 5. Exportar para hls4ml
# ==========================================
# Salvamos no formato Keras (.h5) que o hls4ml lê facilmente
model_filename = "lhc_autoencoder_model.h5"
autoencoder.save(model_filename)
print(f"\nModelo salvo como '{model_filename}'. Pronto para a Fase 2!")