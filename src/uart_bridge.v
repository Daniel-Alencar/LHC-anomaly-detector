`timescale 1ns / 1ps

module uart_bridge (
    input  wire clk_25mhz,
    input  wire rst_n,     // Botão L4 da Colorlight
    input  wire rx,
    output wire tx
);

    localparam OVERSAMPLING = 217;

    wire rx_ready;
    wire rx_valid;
    wire [7:0] rx_data;

    uart_rx #(
        .DATA_BITS(8),
        .STOP_BITS(1),
        .OVERSAMPLING(OVERSAMPLING)
    ) rx_inst (
        .clk_in(clk_25mhz),
        .n_rst(rst_n),
        .rx(rx),
        .ready_out(rx_ready),
        .valid_out(rx_valid),
        .data_out(rx_data)
    );

    wire tx_ready;
    wire tx_valid;
    reg  tx_en;
    reg  [7:0] tx_data_reg;

    uart_tx #(
        .DATA_BITS(8),
        .STOP_BITS(1),
        .OVERSAMPLING(OVERSAMPLING)
    ) tx_inst (
        .clk_in(clk_25mhz),
        .n_rst(rst_n),
        .uart_en(tx_en),
        .data_in(tx_data_reg),
        .ready_out(tx_ready),
        .valid_out(tx_valid),
        .tx(tx)
    );

    reg  ap_start;
    wire ap_done;
    wire ap_idle;
    wire ap_ready;
    reg  input_layer_ap_vld;
    
    wire [127:0] nn_output;
    wire [15:0] out_0, out_1, out_2, out_3, out_4, out_5, out_6, out_7;
    assign nn_output = {out_7, out_6, out_5, out_4, out_3, out_2, out_1, out_0};

    myproject nn_inst (
        .ap_clk(clk_25mhz),
        .ap_rst(~rst_n),
        .ap_start(ap_start),
        .ap_done(ap_done),
        .ap_idle(ap_idle),
        .ap_ready(ap_ready),
        .input_layer(rx_buffer),
        .input_layer_ap_vld(input_layer_ap_vld),
        .layer8_out_0(out_0), .layer8_out_0_ap_vld(),
        .layer8_out_1(out_1), .layer8_out_1_ap_vld(),
        .layer8_out_2(out_2), .layer8_out_2_ap_vld(),
        .layer8_out_3(out_3), .layer8_out_3_ap_vld(),
        .layer8_out_4(out_4), .layer8_out_4_ap_vld(),
        .layer8_out_5(out_5), .layer8_out_5_ap_vld(),
        .layer8_out_6(out_6), .layer8_out_6_ap_vld(),
        .layer8_out_7(out_7), .layer8_out_7_ap_vld()
    );

    // ==========================================
    // MÁQUINA DE ESTADOS (Corrigida)
    // ==========================================
    localparam S_IDLE         = 3'd0;
    localparam S_RX_GATHER    = 3'd1;
    localparam S_NN_START     = 3'd2;
    localparam S_NN_WAIT      = 3'd3;
    localparam S_TX_SCATTER   = 3'd4;
    localparam S_TX_WAIT_FALL = 3'd5; // Estado novo: Espera o TX assumir o dado
    localparam S_TX_WAIT_RISE = 3'd6; // Estado novo: Espera o TX terminar fisicamente

    reg [2:0] state;
    reg [4:0] byte_cnt;
    reg [127:0] rx_buffer;
    reg [127:0] tx_buffer;

    always @(posedge clk_25mhz or negedge rst_n) begin
        if (!rst_n) begin
            state <= S_IDLE;
            byte_cnt <= 0;
            rx_buffer <= 0;
            tx_buffer <= 0;
            ap_start <= 0;
            input_layer_ap_vld <= 0;
            tx_en <= 0;
            tx_data_reg <= 0;
        end else begin
            ap_start <= 0;
            input_layer_ap_vld <= 0;
            tx_en <= 0;

            case (state)
                S_IDLE: begin
                    byte_cnt <= 0;
                    if (rx_valid) begin
                        rx_buffer <= {rx_data, rx_buffer[127:8]};
                        state <= S_RX_GATHER;
                        byte_cnt <= 1;
                    end
                end

                S_RX_GATHER: begin
                    if (rx_valid) begin
                        rx_buffer <= {rx_data, rx_buffer[127:8]};
                        byte_cnt <= byte_cnt + 1;
                        if (byte_cnt == 5'd15) begin
                            state <= S_NN_START;
                        end
                    end
                end

                S_NN_START: begin
                    ap_start <= 1;
                    input_layer_ap_vld <= 1;
                    state <= S_NN_WAIT;
                end

                S_NN_WAIT: begin
                    if (ap_done) begin
                        tx_buffer <= nn_output;
                        byte_cnt <= 0;
                        if (tx_ready) state <= S_TX_SCATTER;
                    end
                end

                S_TX_SCATTER: begin
                    tx_en <= 1; // Pulsa o envio
                    tx_data_reg <= tx_buffer[7:0];
                    tx_buffer <= {8'h00, tx_buffer[127:8]};
                    state <= S_TX_WAIT_FALL; // Vai aguardar a resposta física
                end

                S_TX_WAIT_FALL: begin
                    // O tx_ready demora 1 ciclo para cair a zero. Esperamos aqui.
                    if (!tx_ready) begin
                        state <= S_TX_WAIT_RISE;
                    end
                end

                S_TX_WAIT_RISE: begin
                    // Fica preso aqui até o byte terminar de sair pelo fio
                    if (tx_ready) begin
                        byte_cnt <= byte_cnt + 1;
                        if (byte_cnt == 5'd15) begin // Terminou os 16 bytes?
                            state <= S_IDLE;
                        end else begin
                            state <= S_TX_SCATTER; // Envia o próximo
                        end
                    end
                end

                default: state <= S_IDLE;
            endcase
        end
    end

endmodule