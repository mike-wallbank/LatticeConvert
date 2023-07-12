# ElegantParser.py
#
# Implementation of an interface to ELEGANT-formatted lattice descriptions.
# Provides input (in development) and output tools.
# M Wallbank, Fermilab <wallbank@fnal.gov>
# July 2023

from LatticeParser import LatticeParser
from LatticeData import *
from datetime import datetime

class ElegantParser(LatticeParser):
    def __init__(self, **kwargs):
        self.Lattice = Lattice()

    def LoadLattice(self, lattice):
        self.Lattice = lattice

    def WriteLattice(self, **kwargs):
        print('''
-----------------------------------------------------
Writing lattice in ELEGANT format to\n{}
'''.format(kwargs.get('outputFile')))

        outFile = open(kwargs.get('outputFile'), 'w')
        outFile.write('''
! Written by LatticeConvert. \n! {}\n
'''.format(datetime.now()))

        # Write drifts
        outFile.write('! Drifts\n')
        for drift in self.Lattice.Drifts:
            self.Lattice.Drifts[drift].WriteElegant(outFile)
        outFile.write('\n')

        # Write dipoles
        outFile.write('! Dipoles\n')
        for dipole in self.Lattice.Dipoles:
            self.Lattice.Dipoles[dipole].WriteElegant(outFile)
        outFile.write('\n')

        # Write quads
        outFile.write('! Quads\n')
        for quad in self.Lattice.Quads:
            self.Lattice.Quads[quad].WriteElegant(outFile)
        outFile.write('\n')

        # Write skew quads
        outFile.write('! Skew quads\n')
        for squad in self.Lattice.SkewQuads:
            self.Lattice.SkewQuads[squad].WriteElegant(outFile)
        outFile.write('\n')

        # Write sextupoles
        outFile.write('! Sextupoles\n')
        for sext in self.Lattice.Sexts:
            self.Lattice.Sexts[sext].WriteElegant(outFile)
        outFile.write('\n')
            
        # Write octupoles
        outFile.write('! Octupoles\n')
        for octu in self.Lattice.Octus:
            self.Lattice.Octus[octu].WriteElegant(outFile)
        outFile.write('\n')

        # Write RF
        outFile.write('! RF\n')
        for rf in self.Lattice.RF:
            self.Lattice.RF[rf].WriteElegant(outFile)
        outFile.write('\n')

        # Write misc
        self.WriteMiscElements(outFile)
        outFile.write('\n')

        # Write lattice
        outFile.write('! Lines\n')
        outFile.write("MACHINE: LINE = (rc, ")
        for element in self.Lattice.Sequence:
            if element in self.Lattice.DipoleEdges:
                continue
            if self.Lattice.Sequence.index(element) != 0:
                outFile.write(", ")
            outFile.write("{}".format(element))
        outFile.write(")\n")

        outFile.close()
        print('''
Completed.
-----------------------------------------------------
''')

    def WriteMiscElements(self, outFile):
        outFile.write('! Misc\n')
        outFile.write('rc: RECIRC\n')
