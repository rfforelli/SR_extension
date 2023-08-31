import sys
import argparse
import tensorflow as tf
sys.path.append('../')

import solvers.networks.base7

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='PB to HDF5')
    parser.add_argument('--pb_dir', required=True, type=str)
    parser.add_argument('--hdf5_file', required=True, type=str)
    args = parser.parse_args()

    print('INFO: Load PB', args.pb_dir)
    loaded_model = tf.keras.models.load_model(args.pb_dir)
    print('INFO: Save HDF5', args.hdf5_file)
    tf.keras.models.save_model(loaded_model, args.hdf5_file)




