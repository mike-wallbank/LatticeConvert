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

    args = parser.parse_args()

    converter = LatticeConverter(verbose=args.verbose);
    if args.input_format in ['madx']:
        print("ERROR (convert-lattice.py): LatticeConvert is not yet able to input MAD-X lattices.")
        exit()
    if not args.input_filename or not os.path.isfile(args.input_filename):
        print("ERROR (convert-lattice.py): Unable to open input file {}.".format(args.input_filename))
        exit()
    if args.input_format == "elegant":
        converter.LoadElegant(inputFile=args.input_filename)
    elif args.input_format == "madx":
        converter.LoadMADX(inputFile=args.input_filename)
    elif args.input_format == "6dsim":
        converter.Load6DSim(inputFile=args.input_filename)
    if args.output_format in ['6dsim']:
        print("ERROR (convert-lattice.py): LatticeConvert is not yet able to output 6DSim lattices.")
    if args.output_format == "elegant":
        converter.WriteElegant(outputFile=args.output_filename)
    elif args.output_format == "madx":
        converter.WriteMADX(outputFile=args.output_filename)
    elif args.output_format == "6dsim":
        converter.WriteSixDSim(outputFile=args.output_filename)

if __name__ == "__main__":
    main();
