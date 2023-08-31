
## Table of model results

#### *Use 5b model as the Heterogeneous baseline

| Model Name  | Bit Size | Model BOPS | Train Epochs | Model best MAE | Model best PSNR| 
| ------------- | ------------- | ------------- | ------------- | ------------- | ------------- |
| base7_qkeras_8b | 8 bits | 1.08e+18 | 220 | 4.81 | 30.97 |
| base7_qkeras_7b | 7 bits | 9.22+17 | 220 | 4.84 | 30.91 |
| base7_qkeras_6b | 6 bits | 7.80e+17 | 220| 4.97 | 30.75 |
| **base7_qkeras_5b** | 5 bits | 6.54e+17 | 200| 5.2 | 30.23 |
| **kt_heterogeneous_1** |2-6 bits | 6.52e+17 | 200| 5.19 | 30.22 |
| base7_qkeras_4b | 4 bits | 5.44e+17 | 220| 5.41 | 29.83 |
| **kt_heterogeneous_2** |2-5 bits | 5.28e+17 | 200| 5.23| 30.01 |
| base7_qkeras_3b | 3 bits | 4.50e+17 | 220| 6.45 | 27.48 |
| base7_qkeras_2b | 2 bits | 3.73e+17 | 220| 5.85 | 29.02 |