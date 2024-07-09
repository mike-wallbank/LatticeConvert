#!/usr/bin/env python3

# convert-lattice.py
#
# Basic lattice conversion utility, using the ConvertLattice package.
# Note: the framework is more flexible than this script, and complex
# macros can be developed for more complicated use-cases.
# M Wallbank, Fermilab <wallbank@fnal.gov>
# July 2023

import os
import argparse
from LatticeConvert import LatticeConverter

def main():
    parser = argparse.ArgumentParser(prog = "convert-lattice",
                                     description = "Simple lattice conversion between different formats.")

    parser.add_argument('-i', '--input_format', choices=['elegant','madx','6dsim'])
    parser.add_argument('-s', '--input_filename')
    parser.add_argument('-o', '--output_format', choices=['elegant','madx','6dsim'])
    parser.add_argument('-f', '--output_filename')
    parser.add_argument('-v', '--verbose', action='store_true')
    config = parser.parse_args()

    converter = LatticeConverter(verbose=config.verbose);
    if config.input_format in ['madx']:
        raise RuntimeError("LatticeConvert is not yet able to input MAD-X lattices.")
    if not config.input_filename or not os.path.isfile(config.input_filename):
        raise RuntimeError("Unable to open input file {}.".format(config.input_filename))
    if config.input_format == "elegant":
        converter.LoadElegant(inputFile=config.input_filename)
    elif config.input_format == "madx":
        converter.LoadMADX(inputFile=config.input_filename)
    elif config.input_format == "6dsim":
        converter.Load6DSim(inputFile=config.input_filename)
    if config.output_format == "elegant":
        converter.WriteElegant(outputFile=config.output_filename)
    elif config.output_format == "madx":
        converter.WriteMADX(outputFile=config.output_filename)
    elif config.output_format == "6dsim":
        converter.Write6DSim(outputFile=config.output_filename)

if __name__ == "__main__":
    main();
