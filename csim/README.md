# Quick Start

Export Vivado toolchain, for example:
```
source /tools/Xilinx/Vivado/2019.1/settings64.sh
```

Compile and run the C++ application outside of Vivado HLS:
```
make run
```

The application produces a `output.dat` file that is the classical output of hls4ml csim. You can convert it to an image and show it with [EyeOfGnome](https://wiki.gnome.org/Apps/EyeOfGnome):
```
make show-image
```

Or just run
```
make generate-image
```
and open the `output.jpg` with the tool you prefer.
