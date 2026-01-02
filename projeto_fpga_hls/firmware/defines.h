#ifndef DEFINES_H_
#define DEFINES_H_

#include "ap_fixed.h"
#include "ap_int.h"
#include "nnet_utils/nnet_types.h"
#include <array>
#include <cstddef>
#include <cstdio>
#include <tuple>
#include <tuple>


// hls-fpga-machine-learning insert numbers

// hls-fpga-machine-learning insert layer-precision
typedef ap_fixed<16,6> input_t;
typedef ap_fixed<16,6> encoder_1_accum_t;
typedef ap_fixed<16,6> layer2_t;
typedef ap_fixed<16,6> encoder_1_weight_t;
typedef ap_fixed<16,6> encoder_1_bias_t;
typedef ap_uint<1> layer2_index;
typedef ap_fixed<16,6> layer3_t;
typedef ap_fixed<18,8> encoder_1_relu_table_t;
typedef ap_fixed<16,6> bottleneck_accum_t;
typedef ap_fixed<16,6> layer4_t;
typedef ap_fixed<16,6> bottleneck_weight_t;
typedef ap_fixed<16,6> bottleneck_bias_t;
typedef ap_uint<1> layer4_index;
typedef ap_fixed<16,6> layer5_t;
typedef ap_fixed<18,8> bottleneck_relu_table_t;
typedef ap_fixed<16,6> decoder_1_accum_t;
typedef ap_fixed<16,6> layer6_t;
typedef ap_fixed<16,6> decoder_1_weight_t;
typedef ap_fixed<16,6> decoder_1_bias_t;
typedef ap_uint<1> layer6_index;
typedef ap_fixed<16,6> layer7_t;
typedef ap_fixed<18,8> decoder_1_relu_table_t;
typedef ap_fixed<16,6> output_layer_accum_t;
typedef ap_fixed<16,6> result_t;
typedef ap_fixed<16,6> output_layer_weight_t;
typedef ap_fixed<16,6> output_layer_bias_t;
typedef ap_uint<1> layer8_index;

// hls-fpga-machine-learning insert emulator-defines


#endif
