#include <iostream>

#include "myproject.h"
#include "parameters.h"


void myproject(
    input_t input_layer[8],
    result_t layer8_out[8]
) {

    // hls-fpga-machine-learning insert IO
    #pragma HLS ARRAY_RESHAPE variable=input_layer complete dim=0
    #pragma HLS ARRAY_PARTITION variable=layer8_out complete dim=0
    #pragma HLS INTERFACE ap_vld port=input_layer,layer8_out 
    #pragma HLS PIPELINE

    // hls-fpga-machine-learning insert load weights
#ifndef __SYNTHESIS__
    static bool loaded_weights = false;
    if (!loaded_weights) {
        nnet::load_weights_from_txt<encoder_1_weight_t, 48>(w2, "w2.txt");
        nnet::load_weights_from_txt<encoder_1_bias_t, 6>(b2, "b2.txt");
        nnet::load_weights_from_txt<bottleneck_weight_t, 18>(w4, "w4.txt");
        nnet::load_weights_from_txt<bottleneck_bias_t, 3>(b4, "b4.txt");
        nnet::load_weights_from_txt<decoder_1_weight_t, 18>(w6, "w6.txt");
        nnet::load_weights_from_txt<decoder_1_bias_t, 6>(b6, "b6.txt");
        nnet::load_weights_from_txt<output_layer_weight_t, 48>(w8, "w8.txt");
        nnet::load_weights_from_txt<output_layer_bias_t, 8>(b8, "b8.txt");
        loaded_weights = true;    }
#endif
    // ****************************************
    // NETWORK INSTANTIATION
    // ****************************************

    // hls-fpga-machine-learning insert layers

    layer2_t layer2_out[6];
    #pragma HLS ARRAY_PARTITION variable=layer2_out complete dim=0

    layer3_t layer3_out[6];
    #pragma HLS ARRAY_PARTITION variable=layer3_out complete dim=0

    layer4_t layer4_out[3];
    #pragma HLS ARRAY_PARTITION variable=layer4_out complete dim=0

    layer5_t layer5_out[3];
    #pragma HLS ARRAY_PARTITION variable=layer5_out complete dim=0

    layer6_t layer6_out[6];
    #pragma HLS ARRAY_PARTITION variable=layer6_out complete dim=0

    layer7_t layer7_out[6];
    #pragma HLS ARRAY_PARTITION variable=layer7_out complete dim=0

    nnet::dense<input_t, layer2_t, config2>(input_layer, layer2_out, w2, b2); // encoder_1

    nnet::relu<layer2_t, layer3_t, relu_config3>(layer2_out, layer3_out); // encoder_1_relu

    nnet::dense<layer3_t, layer4_t, config4>(layer3_out, layer4_out, w4, b4); // bottleneck

    nnet::relu<layer4_t, layer5_t, relu_config5>(layer4_out, layer5_out); // bottleneck_relu

    nnet::dense<layer5_t, layer6_t, config6>(layer5_out, layer6_out, w6, b6); // decoder_1

    nnet::relu<layer6_t, layer7_t, relu_config7>(layer6_out, layer7_out); // decoder_1_relu

    nnet::dense<layer7_t, result_t, config8>(layer7_out, layer8_out, w8, b8); // output_layer

}

