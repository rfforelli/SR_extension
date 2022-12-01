#ifndef NNET_UPSAMPLE_STREAM_H_
#define NNET_UPSAMPLE_STREAM_H_

#include "nnet_common.h"
#include "hls_stream.h"

namespace nnet {
    
struct upsample_channels_config
{
    static const unsigned height = 1;
    static const unsigned width = 1;
};


template<class datain_T, class dataout_T, typename CONFIG_T>
void upsample_channels(
    hls::stream<datain_T> &image,
    hls::stream<dataout_T> &resized
) {
	assert(dataout_T::size % datain_T::size == 0);
	constexpr unsigned ratio = dataout_T::size / datain_T::size;
    constexpr unsigned HtimesW = CONFIG_T::height * CONFIG_T::width;

    IterElements: for (unsigned i = 0; i < HtimesW; i++) {
		#pragma HLS PIPELINE
	    datain_T  in_data = image.read();
        dataout_T out_data;

        Upsample: for (unsigned r = 0; r < ratio; r++) {
            #pragma HLS UNROLL
            const unsigned outbase = r * datain_T::size;

            ChanIter: for (unsigned c = 0; c < datain_T::size; c++) {
                #pragma HLS UNROLL
                const unsigned outidx = outbase + c;
                out_data[outidx] = in_data[c];
            }
        }
        resized.write(out_data);
    }
}

}

#endif
