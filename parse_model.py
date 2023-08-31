#!/usr/bin/env python
import numpy as np
import tensorflow as tf
import hls4ml
from pathlib import Path

from qkeras.utils import _add_supported_quantized_objects

test_root_path = Path(__file__).parent

import solvers.networks.base7

BITS = "8b"

MODEL = f"./experiment/base7_qkeras_{BITS}_D4C28_bs16ps64_lr1e-3/best_status"


# DEPTH_TO_SPACE

class DepthToSpace(hls4ml.model.layers.Layer):
    ''' hls4ml implementation of DepthToSpace '''

    def initialize(self):
        inp = self.get_input_variable()
        shape = list(inp.shape)
        bs = self.get_attr('block_size')
        shape[-1] //= bs**2
        shape[-2] *= bs
        shape[-3] *= bs
        dims = ['OUT_HEIGHT_{}'.format(self.index), 'OUT_WIDTH_{}'.format(self.index), 'N_FILT_{}'.format(self.index)]
        self.add_output_variable(shape, dims)

# HLS Templates
depthtospace_config_template = """struct config{index} : nnet::depth_to_space_config {{
    static const unsigned height = {height};
    static const unsigned width = {width};
    static const unsigned n_chan = {n_chan};
    static const unsigned block_size = {block_size};
}};\n"""

depthtospace_function_template = 'nnet::depth_to_space<{input_t}, {output_t}, {config}>({input}, {output});'
depthtospace_include_list = ['nnet_utils/nnet_depthtospace_stream.h']

class DepthToSpaceConfigTemplate(hls4ml.backends.template.LayerConfigTemplate):
    def __init__(self):
        super().__init__(DepthToSpace)
        self.template = depthtospace_config_template

    def format(self, node):
        params = self._default_config_params(node)
        return self.template.format(**params)

class DepthToSpaceFunctionTemplate(hls4ml.backends.template.FunctionCallTemplate):
    def __init__(self):
        super().__init__(DepthToSpace, include_header=depthtospace_include_list)
        self.template = depthtospace_function_template

    def format(self, node):
        params = self._default_function_params(node)
        return self.template.format(**params)


##### UPSAMPLE

class Upsample(hls4ml.model.layers.Layer):
    ''' hls4ml implementation of Upsample '''

    def initialize(self):
        inp = self.get_input_variable()
        shape = list(inp.shape)
        shape[-1] *= self.get_attr('scale2')
        dims = ['OUT_HEIGHT_{}'.format(self.index), 'OUT_WIDTH_{}'.format(self.index), 'N_FILT_{}'.format(self.index)]
        self.add_output_variable(shape, dims)

# HLS Templates
upsample_config_template = """struct config{index} : nnet::upsample_channels_config {{
    static const unsigned height = {height};
    static const unsigned width = {width};
}};\n"""

upsample_function_template = 'nnet::upsample_channels<{input_t}, {output_t}, {config}>({input}, {output});'
upsample_include_list = ['nnet_utils/nnet_upsample_stream.h']


class UpsampleConfigTemplate(hls4ml.backends.template.LayerConfigTemplate):
    def __init__(self):
        super().__init__(Upsample)
        self.template = upsample_config_template

    def format(self, node):
        params = self._default_config_params(node)
        return self.template.format(**params)

class UpsampleFunctionTemplate(hls4ml.backends.template.FunctionCallTemplate):
    def __init__(self):
        super().__init__(Upsample, include_header=upsample_include_list)
        self.template = upsample_function_template

    def format(self, node):
        params = self._default_function_params(node)
        return self.template.format(**params)


def parse_lambda_layer(keras_layer, input_names, input_shapes, data_reader):
    layer = {}
    layer['name'] = keras_layer['config']['name']
    layer['n_in'] = input_shapes[0][1]
    if layer['name'] == 'lambda':
        # this is the Upsample. should maybe see if there's a better way to tell
        layer['class_name'] = 'Upsample'
        layer['inputs'] = [input_names[0]]   # the original code strangely duplicates everything
        layer['scale2'] = len(input_names)
        inp0 = input_shapes[0]
        layer['width'] = inp0[-2]
        layer['height'] = inp0[-3]
        outshape = [shape for shape in input_shapes[0]]
        outshape[-1] *= layer['scale2']
    elif layer['name'] == 'lambda_1':
        # this is the depth to space
        layer['class_name'] = 'DepthToSpace'
        layer['inputs'] = input_names
        inp0 = input_shapes[0]
        bs = 3
        layer['block_size'] = bs
        layer['n_chan'] = inp0[-1]
        layer['width'] = inp0[-2]
        layer['height'] = inp0[-3]
        outshape = [shape for shape in input_shapes[0]]
        outshape[-1] //= bs**2
        outshape[-2] *= bs
        outshape[-3] *= bs

    else:
        layer['class_name'] = 'Activation'
        layer['activation'] = 'linear'
        if input_names is not None:
            layer['inputs'] = input_names
        outshape = [shape for shape in input_shapes[0]]
    return layer, outshape

def register_lambda_layer():
    # Register the converter for custom Keras layer
    hls4ml.converters.register_keras_layer_handler('Lambda', parse_lambda_layer)

    # Register the hls4ml's IR layer
    hls4ml.model.layers.register_layer('Upsample', Upsample)
    hls4ml.model.layers.register_layer('DepthToSpace', DepthToSpace)

    backend = hls4ml.backends.get_backend("Vivado")

    # Register template passes for the given backend
    backend.register_template(UpsampleConfigTemplate)
    backend.register_template(UpsampleFunctionTemplate)
    backend.register_template(DepthToSpaceConfigTemplate)
    backend.register_template(DepthToSpaceFunctionTemplate)

    backend.register_source(test_root_path / "lambda_cpp/nnet_depthtospace_stream.h")
    backend.register_source(test_root_path / "lambda_cpp/nnet_upsample_stream.h")
    print(test_root_path)

def parse_model():
    register_lambda_layer()

    co = {}
    _add_supported_quantized_objects(co)

    model = tf.keras.models.load_model(MODEL, custom_objects=co)
    model.summary()

    config = hls4ml.utils.config_from_keras_model (model,
                                                   default_precision = 'ap_fixed<16,10>',
                                                   granularity = 'name')

    #strategy = "Latency"
    strategy = "Resource"
    rf = 256

    config["Model"]['BramFactor'] = 0
    config["Model"]["Strategy"] = "Resource"
    for layer in config["LayerName"]:
        config["LayerName"][layer]['ReuseFactor'] = rf
        config["LayerName"][layer]["Strategy"] = strategy
    config["LayerName"]["input_1"]["Precision"] = 'ap_uint<8>'
    config["LayerName"]["clone_input_1"] = {}
    config["LayerName"]["clone_input_1"]["Precision"] = 'ap_uint<8>'
    config["LayerName"]["lambda_2"]["Precision"] = 'ap_ufixed<8,8,AP_RND_CONV, AP_SAT>'
    # config['Flows'] = ['vivado:fifo_depth_optimization']

    print(config)

    # hls4ml.model.optimizer.get_optimizer('output_rounding_saturation_mode').configure(layers=activations,
    #     rounding_mode='AP_RND_CONV', saturation_mode='AP_SAT')

    hls_model = hls4ml.converters.convert_from_keras_model(model,
                                                           hls_config = config,
                                                           io_type = 'io_stream',
                                                           output_dir = f'test_model_{BITS}_{strategy}_rf{rf}_nofifo_test',
                                                           input_data_tb=str(test_root_path / "csim/tb_data/tb_input_features.dat"),
                                                           output_data_tb=str(test_root_path / "csim/tb_data/tb_output_predictions.dat"),
                                                           part='xcvu9p-flgc2104-2L-e'
                                                           )


    hls_model.compile()
    hls_model.build(csim=False, synth=True, cosim=False, validation=False, vsynth=False, export=False)

if __name__ == "__main__":
    parse_model()