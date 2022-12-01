# Using hls4ml's extensions API for the SR_Mobile_Quantization model

This example shows how to use the extensions API to parse the SR_Mobile_Quantization model using hls4ml's extensions API. Look specifically at [parse_model.py](parse_model.py). The input file might need editing. It should point to [best_status](https://github.com/fastmachinelearning/SR_Mobile_Quantization/tree/sandbox/experiment/base7_D4C28_bs16ps64_lr1e-3/best_status).

The precisions should be tuned. In particular, to add the final clip, one should define the output to be `ap_ufixed<8, 8, AP_RND, AP_SAT>`.

The HLS code for the lambda layers is provided in [nnet_upsample_stream.h](nnet_upsample_stream.h) and [nnet_depthtospace_stream.h](nnet_depthtospace_stream.h).
