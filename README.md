# Using hls4ml's extensions API for the SR_Mobile_Quantization model

This example shows how to use the hls4ml's **extensions API** to parse the `SR_Mobile_Quantization`.

Look specifically at [parse_model.py](parse_model.py). The path to the model might need editing (`MODEL`) and should point to a local copy of [best_status](https://github.com/fastmachinelearning/SR_Mobile_Quantization/tree/sandbox/experiment/base7_D4C28_bs16ps64_lr1e-3/best_status).

To run:
```
make run
```

## Lambda layer implementation

The HLS code for the lambda layers _UpSample_ and _DepthToSpace_ is provided
- [lambda_cpp/nnet_upsample_stream.h](lambda_cpp/nnet_upsample_stream.h)
- [lambda_cpp/nnet_depthtospace_stream.h](lambda_cpp/nnet_depthtospace_stream.h).

The third lambda layer of the model, i.e. _Clip_, is implemented via fixed-point precision tuning: the output is `ap_ufixed<8, 8, AP_RND, AP_SAT>`.


