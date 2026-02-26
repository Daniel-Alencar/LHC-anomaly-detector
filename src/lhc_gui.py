#! /usr/bin/python3

import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports
import time

class LHCAnomalyDetectorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LHC Beam Anomaly Detector - FPGA Interface")
        self.root.geometry("650x550")
        self.root.resizable(False, False)
        
        self.serial_port = None
        
        self.create_widgets()
        self.refresh_ports()

    def create_widgets(self):
        # --- Frame de Conexão ---
        conn_frame = ttk.LabelFrame(self.root, text=" [ Conexao Serial (FPGA) ] ")
        conn_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(conn_frame, text="Porta:").grid(row=0, column=0, padx=5, pady=5)
        self.cb_ports = ttk.Combobox(conn_frame, width=15)
        self.cb_ports.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(conn_frame, text="Atualizar", command=self.refresh_ports).grid(row=0, column=2, padx=5, pady=5)
        
        self.btn_connect = ttk.Button(conn_frame, text="Conectar", command=self.toggle_connection)
        self.btn_connect.grid(row=0, column=3, padx=5, pady=5)
        
        self.lbl_status = ttk.Label(conn_frame, text="Desconectado", foreground="red")
        self.lbl_status.grid(row=0, column=4, padx=10, pady=5)

        # --- Frame de Injeção de Sinais ---
        inj_frame = ttk.LabelFrame(self.root, text=" [ Injecao de Sinais (128-bits / 16 bytes) ] ")
        inj_frame.pack(padx=10, pady=5, fill="x")

        # Nominal (Tudo Zero) -> 0.0
        ttk.Button(inj_frame, text="[ NOMINAL ] Feixe Estavel", width=30, 
                   command=lambda: self.send_data(bytes([0x00, 0x00] * 8))).grid(row=0, column=0, padx=10, pady=5)
        
        # Anomalia Suave -> Ruído de meio de escala (ex: 0x0A00 = 2560)
        ttk.Button(inj_frame, text="[ WARNING ] Ruido no Feixe", width=30, 
                   command=lambda: self.send_data(bytes([0x00, 0x0A] * 8))).grid(row=0, column=1, padx=10, pady=5)
        
        # Falha de Sensor (Saturação Positiva Máxima -> 0x7FFF = 32767)
        ttk.Button(inj_frame, text="[ CRITICAL ] Saturacao de Sensor", width=30, 
                   command=lambda: self.send_data(bytes([0xFF, 0x7F] * 8))).grid(row=1, column=0, columnspan=2, padx=10, pady=5)

        # --- Frame Customizado ---
        custom_frame = ttk.Frame(inj_frame)
        custom_frame.grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Label(custom_frame, text="Custom Hex (32 chars):").pack(side="left", padx=5)
        self.ent_custom = ttk.Entry(custom_frame, width=35, font=("Courier", 10))
        self.ent_custom.insert(0, "00" * 16)
        self.ent_custom.pack(side="left", padx=5)
        ttk.Button(custom_frame, text="Enviar Custom", command=self.send_custom).pack(side="left", padx=5)

        # --- Frame de Resultados ---
        res_frame = ttk.LabelFrame(self.root, text=" [ Resposta do Hardware (Edge AI) ] ")
        res_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Enviado
        ttk.Label(res_frame, text="Sinal Enviado:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.lbl_sent = ttk.Label(res_frame, text="-", font=("Courier", 11))
        self.lbl_sent.grid(row=0, column=1, sticky="w", padx=10, pady=5)

        # Recebido
        ttk.Label(res_frame, text="Reconstrucao (FPGA):").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.lbl_recv = ttk.Label(res_frame, text="-", font=("Courier", 11, "bold"))
        self.lbl_recv.grid(row=1, column=1, sticky="w", padx=10, pady=5)

        # Latência
        ttk.Label(res_frame, text="Latencia (Round-trip):").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.lbl_time = ttk.Label(res_frame, text="- ms", font=("Helvetica", 11))
        self.lbl_time.grid(row=2, column=1, sticky="w", padx=10, pady=5)

        # Erro (Anomaly Score)
        ttk.Label(res_frame, text="Nivel de Anomalia (Erro):").grid(row=3, column=0, sticky="w", padx=10, pady=10)
        self.lbl_error = ttk.Label(res_frame, text="-", font=("Helvetica", 12, "bold"))
        self.lbl_error.grid(row=3, column=1, sticky="w", padx=10, pady=10)

        # Barra de Progresso do Erro
        self.progress = ttk.Progressbar(res_frame, orient="horizontal", length=400, mode="determinate")
        self.progress.grid(row=4, column=0, columnspan=2, padx=10, pady=10)
    def refresh_ports(self):
        ports = serial.tools.list_ports.comports()
        self.cb_ports['values'] = [port.device for port in ports]
        if self.cb_ports['values']:
            self.cb_ports.current(0)

    def toggle_connection(self):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            self.btn_connect.config(text="Conectar")
            self.lbl_status.config(text="Desconectado", foreground="red")
        else:
            port = self.cb_ports.get()
            if not port:
                messagebox.showwarning("Aviso", "Selecione uma porta serial.")
                return
            try:
                self.serial_port = serial.Serial(port, 115200, timeout=1)
                self.btn_connect.config(text="Desconectar")
                self.lbl_status.config(text="Conectado", foreground="green")
            except Exception as e:
                messagebox.showerror("Erro de Conexão", f"Não foi possível abrir {port}.\nErro: {e}")

    def send_custom(self):
        hex_str = self.ent_custom.get().strip()
        if len(hex_str) != 32:
            messagebox.showwarning("Formato Inválido", "A string hexadecimal deve ter exatamente 32 caracteres (16 bytes).")
            return
        try:
            data_bytes = bytes.fromhex(hex_str)
            self.send_data(data_bytes)
        except ValueError:
            messagebox.showerror("Erro", "Caracteres hexadecimais inválidos.")

    def send_data(self, data_bytes):
        import struct # Adicione isso no topo do arquivo se preferir

        if not self.serial_port or not self.serial_port.is_open:
            messagebox.showwarning("Aviso", "Conecte-se a placa primeiro!")
            return

        self.serial_port.reset_input_buffer()
        
        sent_hex = data_bytes.hex().upper()
        self.lbl_sent.config(text=' '.join(sent_hex[i:i+2] for i in range(0, len(sent_hex), 2)))
        self.root.update()

        # Medição de tempo real
        t_start = time.perf_counter()
        self.serial_port.write(data_bytes)
        response = self.serial_port.read(16)
        t_end = time.perf_counter()

        if len(response) == 16:
            recv_hex = response.hex().upper()
            self.lbl_recv.config(text=' '.join(recv_hex[i:i+2] for i in range(0, len(recv_hex), 2)))
            
            dt_ms = (t_end - t_start) * 1000
            self.lbl_time.config(text=f"{dt_ms:.2f} ms")

            # ====================================================
            # A MÁGICA CORRIGIDA: Desempacotando como C++ (int16_t)
            # "<8h" significa: Little-Endian (<), 8 números do tipo short int (h)
            # ====================================================
            input_vals = struct.unpack("<8h", data_bytes)
            output_vals = struct.unpack("<8h", response)
            
            # Soma das diferenças absolutas (agora com a matemática certa!)
            error_score = sum(abs(i - o) for i, o in zip(input_vals, output_vals))
            
            # Formata os arrays para visualizarmos no terminal
            print(f"[{time.strftime('%H:%M:%S')}]")
            print(f"Valores Enviados: {input_vals}")
            print(f"Valores Recebidos: {output_vals}")
            print(f"Erro Real Calculado: {error_score}\n")
            
            self.lbl_error.config(text=f"Erro MAE: {error_score}")
            
            # Ajuste a escala máxima da barra de erro (Saturação costuma dar erro > 100.000)
            max_expected_error = 150000 
            error_pct = min((error_score / max_expected_error) * 100, 100)
            self.progress['value'] = error_pct
            
            if error_pct < 10:
                self.lbl_error.config(foreground="green")
            elif error_pct < 40:
                self.lbl_error.config(foreground="orange")
            else:
                self.lbl_error.config(foreground="red")
        else:
            self.lbl_recv.config(text="TIMEOUT")
            self.lbl_time.config(text="-")
            self.lbl_error.config(text="-", foreground="black")
            self.progress['value'] = 0

if __name__ == "__main__":
    root = tk.Tk()
    app = LHCAnomalyDetectorGUI(root)
    root.mainloop()