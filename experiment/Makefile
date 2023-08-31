PB_DIR=base7_D4C28_bs16ps64_lr1e-3/best_status
HDF5_FILE=base7_D4C28_bs16ps64_lr1e-3/best_status.h5

help:
	@echo "INFO: make <tab> for targets"
.PHONY: help

convert:
	TF_CPP_MIN_LOG_LEVEL=3 TF_XLA_FLAGS=--tf_xla_enable_xla_devices \
	python convert_pb_to_hdf5.py \
		--pb_dir ${PB_DIR} \
		--hdf5_file ${HDF5_FILE}
.PHONY: convert

show:
	netron ${HDF5_FILE}
.PHONY: show
