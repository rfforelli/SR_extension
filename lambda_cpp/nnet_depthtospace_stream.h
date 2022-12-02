#ifndef NNET_DEPTHTOSPACE_STREAM_H_
#define NNET_DEPTHTOSPACE_STREAM_H_

#include "nnet_common.h"
#include "hls_stream.h"

namespace nnet {

// Useful description on how to implement
// https://github.com/seetaresearch/dragon/blob/master/tensorflow/core/ops/array_ops.py#L106-L142

struct depth_to_space_config
{
    static const unsigned height = 10;
    static const unsigned width = 10;
    static const unsigned n_chan = 1;
    static const unsigned block_size = 1;
};

template<class datain_T, class dataout_T, typename CONFIG_T>
void depth_to_space(
    hls::stream<datain_T> &image,
    hls::stream<dataout_T> &resized
) {
    constexpr unsigned bssq = CONFIG_T::block_size * CONFIG_T::block_size;
	assert(datain_T::size % bssq == 0);
    constexpr unsigned n_rest = CONFIG_T::n_chan / CONFIG_T::block_size;

	ImageHeight: for (unsigned h = 0; h < CONFIG_T::height; h++) {
	
		datain_T data_in_row[CONFIG_T::width];
		
		ImageWidth: for (unsigned w = 0; w < CONFIG_T::width; w++) {
			//#pragma HLS UNROLL
			
			datain_T  in_data = image.read();
			
			ImageChan: for (unsigned c = 0; c < CONFIG_T::n_chan; c++) {
				#pragma HLS UNROLL
				
				data_in_row[w][c] = in_data[c];
			}
		}

        typename dataout_T::value_type transposed_row[CONFIG_T::width*CONFIG_T::n_chan];
        #pragma HLS ARRAY_PARTITION variable=transposed_row cyclic factor=n_rest dim=0

        // trying to do np.transpose(y, (0, 1, 3, 2, 4, 5)), given 0, 1
        TransposeLoop: for (unsigned bh = 0; bh < CONFIG_T::block_size; bh++) {
            for (unsigned w = 0; w < CONFIG_T::width; w++) {
                #pragma HLS PIPELINE
                // loop over the rest (4 and 5 in transpose)
                for (unsigned r = 0; r < n_rest; r++) {
                    const unsigned idx = r + n_rest * (w + CONFIG_T::width * bh);
                    transposed_row[idx] = data_in_row[w][r + n_rest * bh];
                }
            }
        }

        // now write out
        WriteLoop: for (unsigned i = 0; i < CONFIG_T::width*CONFIG_T::n_chan/dataout_T::size; i++) {
            #pragma HLS PIPELINE
            dataout_T out_data;
            for (unsigned newchan = 0; newchan < dataout_T::size; newchan++) {
                out_data[newchan] = transposed_row[newchan + dataout_T::size * i];
            }
            resized.write(out_data);
        }
    }
}

}

#endif
