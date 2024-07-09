# LatticeConvert.py
#
# Interface to the LatticeConvert toolkit, providing high-level functionality.
# M Wallbank, Fermilab <wallbank@fnal.gov>
# July 2023

from LatticeData import Lattice
from SixDSimParser import SixDSimParser
from ElegantParser import ElegantParser
from MADXParser import MADXParser

class LatticeConverter:
    def __init__(self, **kwargs):
        print('''
        -----------------------------------------------------
        Welcome to LatticeConverter.
        -----------------------------------------------------
        ''')
        self.Verbose = kwargs.get('verbose')
        self.Lattice = Lattice()

    def Load6DSim(self, **kwargs):
        parser = SixDSimParser()
        parser.ParseInput(inputFile=kwargs.get('inputFile'),
                          verbose=self.Verbose)
        self.Lattice = parser.Lattice

    def LoadElegant(self, **kwargs):
        parser = ElegantParser()
        parser.ParseInput(inputFile=kwargs.get('inputFile'),
                          verbose=self.Verbose)
        self.Lattice = parser.Lattice

    def LoadMADX(self, **kwargs):
        parser = MADXParser()
        parser.ParseInput(inputFile=kwargs.get('inputFile'),
                          verbose=self.Verbose)
        self.Lattice = parser.Lattice

    def Write6DSim(self, **kwargs):
        parser = SixDSimParser()
        parser.LoadLattice(self.Lattice)
        parser.WriteLattice(**kwargs)

    def WriteElegant(self, **kwargs):
        parser = ElegantParser()
        parser.LoadLattice(self.Lattice)
        parser.WriteLattice(**kwargs)

    def WriteMADX(self, **kwargs):
        parser = MADXParser()
        parser.LoadLattice(self.Lattice)
        parser.WriteLattice(**kwargs)

