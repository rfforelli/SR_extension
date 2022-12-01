#!/usr/bin/env python
import numpy as np
import tensorflow as tf
import hls4ml
from pathlib import Path

test_root_path = Path(__file__).parent

import solvers.networks.base7

MODEL = "../SR_Mobile_Quantization/experiment/base7_D4C28_bs16ps64_lr1e-3/best_status"



class Lambda(hls4ml.model.layers.Layer):
    ''' hls4ml implementation of a Lambda Layer (only special cases supported) '''

    def initialize(self):
        inp = self.get_input_variable()
        shape = inp.shape
        dims = inp.dim_names
        self.add_output_variable(shape, dims)


def parse_lambda_layer(keras_layer, input_names, input_shapes, data_reader, config):
    layer = {}
    layer['class_name'] = 'Lambda'
    layer['name'] = keras_layer['config']['name']
    layer['n_in'] = input_shapes[0][1]
    
    if input_names is not None:
        layer['inputs'] = input_names

    return layer, [shape for shape in input_shapes[0]]

# HLS Templates - No specific pragmas used; generic enough for both Intel and Vivado

rev_config_template = """struct config{index} : nnet::reverse_config {{
    static const unsigned n_in = {n_in};
}};\n"""

lambda_function_template = 'nnet::lambda<{input_t}, {config}>({input}, {output});'
lambda_include_list = ['nnet_utils/nnet_lambda.h']

class LambdaConfigTemplate(hls4ml.backends.template.LayerConfigTemplate):
    def __init__(self):
        super().__init__(Lambda)
        self.template = rev_config_template
    
    def format(self, node):
        params = self._default_config_params(node)        
        return self.template.format(**params)

class LambdaFunctionTemplate(hls4ml.backends.template.FunctionCallTemplate):
    def __init__(self):
        super().__init__(Lambda, include_header=lambda_include_list)
        self.template = lambda_function_template
    
    def format(self, node):
        params = self._default_function_params(node)
        return self.template.format(**params)


def regsister_lambda_layer():
    # Register the converter for custom Keras layer
    hls4ml.converters.register_keras_layer_handler('Lambda', parse_lambda_layer)

    # Register the hls4ml's IR layer
    hls4ml.model.layers.register_layer('Lambda', Lambda)

    backend = hls4ml.backends.get_backend("Vivado")

    # Register template passes for the given backend
    backend.register_template(LambdaConfigTemplate)
    backend.register_template(LambdaFunctionTemplate)

    backend.register_source(test_root_path / "nnet_lambda.h")

def parse_model():
    regsister_lambda_layer()

    model = tf.keras.models.load_model(MODEL)
    model.summary()


    config = hls4ml.utils.config_from_keras_model (model,
                                                   default_precision = 'ap_fixed<16,10>',
                                                   granularity = 'name')

    print(config)

    hls_model = hls4ml.converters.convert_from_keras_model(model,
                                                           hls_config = config,
                                                           io_type = 'io_stream',
                                                            output_dir = 'test_model'
                                                           )

if __name__ == "__main__":
    parse_model()
