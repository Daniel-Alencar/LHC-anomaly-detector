# --- Configurações do Projeto ---
PROJ       = lhc_detector
TOP_ENTITY = uart_bridge

# Usa a função wildcard para pegar todos os .v da pasta atual 
# E TODOS os .v gerados pelo HLS na subpasta especificada
VERILOG_FILES = $(wildcard *.v) $(wildcard ../projeto_fpga_hls/myproject_prj/solution1/syn/verilog/*.v)

# Configurações da Placa (Colorlight i9+ lattice ECP5-45)
PIN_DEF    = colorlight.lpf
DEVICE     = 45k
PACKAGE    = CABGA381
SPEED      = 6

# --- Comandos ---
all: prog

# 1. Análise e Síntese (Yosys nativo para Verilog)
$(PROJ).json: $(VERILOG_FILES)
	yosys -p "synth_ecp5 -top $(TOP_ENTITY) -json $@" $(VERILOG_FILES)

# 2. Place & Route (NextPNR)
$(PROJ).config: $(PROJ).json $(PIN_DEF)
	nextpnr-ecp5 --$(DEVICE) --package $(PACKAGE) --speed $(SPEED) --lpf $(PIN_DEF) --textcfg $@ --json $<

# 3. Empacotamento (Project Trellis)
$(PROJ).bit: $(PROJ).config
	ecppack $< $@

# 4. Gravação (openFPGALoader)
prog: $(PROJ).bit
	openFPGALoader -c cmsisdap $(PROJ).bit

# Limpeza de arquivos gerados
clean:
	rm -f *.json *.config *.bit