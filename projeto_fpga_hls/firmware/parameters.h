#ifndef PARAMETERS_H_
#define PARAMETERS_H_

#include "ap_fixed.h"
#include "ap_int.h"

#include "nnet_utils/nnet_code_gen.h"
#include "nnet_utils/nnet_helpers.h"
// hls-fpga-machine-learning insert includes
#include "nnet_utils/nnet_activation.h"
#include "nnet_utils/nnet_activation_stream.h"
#include "nnet_utils/nnet_dense.h"
#include "nnet_utils/nnet_dense_compressed.h"
#include "nnet_utils/nnet_dense_stream.h"

// hls-fpga-machine-learning insert weights
#include "weights/w2.h"
#include "weights/b2.h"
#include "weights/w4.h"
#include "weights/b4.h"
#include "weights/w6.h"
#include "weights/b6.h"
#include "weights/w8.h"
#include "weights/b8.h"


// hls-fpga-machine-learning insert layer-config
// encoder_1
struct config2 : nnet::dense_config {
    static const unsigned n_in = 8;
    static const unsigned n_out = 6;
    static const unsigned io_type = nnet::io_parallel;
    static const unsigned strategy = nnet::latency;
    static const unsigned reuse_factor = 4;
    static const unsigned n_zeros = 0;
    static const unsigned n_nonzeros = 48;
    static const unsigned multiplier_limit = DIV_ROUNDUP(n_in * n_out, reuse_factor) - n_zeros / reuse_factor;
    static const bool store_weights_in_bram = false;
    typedef encoder_1_accum_t accum_t;
    typedef encoder_1_bias_t bias_t;
    typedef encoder_1_weight_t weight_t;
    typedef layer2_index index_t;
    template<class data_T, class res_T, class CONFIG_T>
    using kernel = nnet::DenseLatency<data_T, res_T, CONFIG_T>;
    template<class x_T, class y_T>
    using product = nnet::product::mult<x_T, y_T>;
};

// encoder_1_relu
struct relu_config3 : nnet::activ_config {
    static const unsigned n_in = 6;
    static const unsigned table_size = 1024;
    static const unsigned io_type = nnet::io_parallel;
    static const unsigned reuse_factor = 4;
    typedef encoder_1_relu_table_t table_t;
};

// bottleneck
struct config4 : nnet::dense_config {
    static const unsigned n_in = 6;
    static const unsigned n_out = 3;
    static const unsigned io_type = nnet::io_parallel;
    static const unsigned strategy = nnet::latency;
    static const unsigned reuse_factor = 4;
    static const unsigned n_zeros = 0;
    static const unsigned n_nonzeros = 18;
    static const unsigned multiplier_limit = DIV_ROUNDUP(n_in * n_out, reuse_factor) - n_zeros / reuse_factor;
    static const bool store_weights_in_bram = false;
    typedef bottleneck_accum_t accum_t;
    typedef bottleneck_bias_t bias_t;
    typedef bottleneck_weight_t weight_t;
    typedef layer4_index index_t;
    template<class data_T, class res_T, class CONFIG_T>
    using kernel = nnet::DenseLatency<data_T, res_T, CONFIG_T>;
    template<class x_T, class y_T>
    using product = nnet::product::mult<x_T, y_T>;
};

// bottleneck_relu
struct relu_config5 : nnet::activ_config {
    static const unsigned n_in = 3;
    static const unsigned table_size = 1024;
    static const unsigned io_type = nnet::io_parallel;
    static const unsigned reuse_factor = 4;
    typedef bottleneck_relu_table_t table_t;
};

// decoder_1
struct config6 : nnet::dense_config {
    static const unsigned n_in = 3;
    static const unsigned n_out = 6;
    static const unsigned io_type = nnet::io_parallel;
    static const unsigned strategy = nnet::latency;
    static const unsigned reuse_factor = 4;
    static const unsigned n_zeros = 0;
    static const unsigned n_nonzeros = 18;
    static const unsigned multiplier_limit = DIV_ROUNDUP(n_in * n_out, reuse_factor) - n_zeros / reuse_factor;
    static const bool store_weights_in_bram = false;
    typedef decoder_1_accum_t accum_t;
    typedef decoder_1_bias_t bias_t;
    typedef decoder_1_weight_t weight_t;
    typedef layer6_index index_t;
    template<class data_T, class res_T, class CONFIG_T>
    using kernel = nnet::DenseLatency<data_T, res_T, CONFIG_T>;
    template<class x_T, class y_T>
    using product = nnet::product::mult<x_T, y_T>;
};

// decoder_1_relu
struct relu_config7 : nnet::activ_config {
    static const unsigned n_in = 6;
    static const unsigned table_size = 1024;
    static const unsigned io_type = nnet::io_parallel;
    static const unsigned reuse_factor = 4;
    typedef decoder_1_relu_table_t table_t;
};

// output_layer
struct config8 : nnet::dense_config {
    static const unsigned n_in = 6;
    static const unsigned n_out = 8;
    static const unsigned io_type = nnet::io_parallel;
    static const unsigned strategy = nnet::latency;
    static const unsigned reuse_factor = 4;
    static const unsigned n_zeros = 0;
    static const unsigned n_nonzeros = 48;
    static const unsigned multiplier_limit = DIV_ROUNDUP(n_in * n_out, reuse_factor) - n_zeros / reuse_factor;
    static const bool store_weights_in_bram = false;
    typedef output_layer_accum_t accum_t;
    typedef output_layer_bias_t bias_t;
    typedef output_layer_weight_t weight_t;
    typedef layer8_index index_t;
    template<class data_T, class res_T, class CONFIG_T>
    using kernel = nnet::DenseLatency<data_T, res_T, CONFIG_T>;
    template<class x_T, class y_T>
    using product = nnet::product::mult<x_T, y_T>;
};



#endif
