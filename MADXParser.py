# MADXParser.py
#
# Implementation of an interface to MADX-formatted lattice descriptions.
# Provides input (in development) and output tools.
# M Wallbank, Fermilab <wallbank@fnal.gov>
# July 2023

from LatticeParser import LatticeParser
from LatticeData import *
from datetime import datetime

# ---------------------------------------------------------------------------
class MADXParser(LatticeParser):
    def __init__(self, **kwargs):
        LatticeParser.__init__(self)

    def ParseInput(self):
        pass

    def WriteLattice(self, **kwargs):

        if 'outputFile' in kwargs and kwargs.get('outputFile') is not None:
            outputFile = kwargs.get('outputFile')
        else:
            outputFile = "{}.seq".format(self.Lattice.Name)

        print('''
-----------------------------------------------------
Writing lattice in MAD-X format to\n{}
'''.format(outputFile))

        outFile = open(outputFile, 'w')
        outFile.write('''
! Written by LatticeConvert. \n! {}\n
'''.format(datetime.now()))

        # Write drifts
        outFile.write('! Drifts\n')
        for drift in self.Lattice.Drifts:
            self.Lattice.Drifts[drift].WriteMADX(outFile)
        outFile.write('\n')

        # Write dipoles
        outFile.write('! Dipoles\n')
        for dipole in self.Lattice.Dipoles:
            self.Lattice.Dipoles[dipole].WriteMADX(outFile)
        outFile.write('\n')

        # Write quads
        outFile.write('! Quads\n')
        for quad in self.Lattice.Quads:
            self.Lattice.Quads[quad].WriteMADX(outFile)
        outFile.write('\n')

        # Write skew quads
        outFile.write('! Skew quads\n')
        for squad in self.Lattice.SkewQuads:
            self.Lattice.SkewQuads[squad].WriteMADX(outFile)
        outFile.write('\n')

        # Write sextupoles
        outFile.write('! Sextupoles\n')
        for sext in self.Lattice.Sexts:
            self.Lattice.Sexts[sext].WriteMADX(outFile)
        outFile.write('\n')
            
        # Write octupoles
        outFile.write('! Octupoles\n')
        for octu in self.Lattice.Octus:
            self.Lattice.Octus[octu].WriteMADX(outFile)
        outFile.write('\n')

        # Write RF
        outFile.write('! RF\n')
        for rf in self.Lattice.RF:
            self.Lattice.RF[rf].WriteMADX(outFile)
        outFile.write('\n')

        # Write lattice
        outFile.write('! Lines\n')
        outFile.write("MACHINE: SEQUENCE, L={}, REFER=ENTRY;\n".format(self.Lattice.Length))
        for i,element in enumerate(self.Lattice.Sequence):
            if element in self.Lattice.DipoleEdges:
                continue
            location = self.Lattice.Locations[element][self.Lattice.Sequence[:i].count(element)]
            if element in self.Lattice.Dipoles:
                outFile.write("IN{}, AT={};\n{}, AT={};\nOUT{}, AT={};\n"
                              .format(element, location, element, location, element, location+self.Lattice.Dipoles[element].Length))
            else:
                outFile.write("{}, AT={};\n".format(element, location))
        outFile.write("ENDSEQUENCE;")

        outFile.close()
        print('''
Completed.
-----------------------------------------------------
''')
