# ElegantParser.py
#
# Implementation of an interface to ELEGANT-formatted lattice descriptions.
# Provides input and output tools.
# M Wallbank, Fermilab <wallbank@fnal.gov>
# July 2023

import os
from LatticeParser import LatticeParser
from LatticeData import *
from datetime import datetime

# ---------------------------------------------------------------------------
class ElegantParser(LatticeParser):
    def __init__(self, **kwargs):
        LatticeParser.__init__(self)

    # ---------------------------------------------------------------------------
    def ParseInput(self, **kwargs):
        inputFile = kwargs.get('inputFile')
        print('''
-----------------------------------------------------
Importing lattice in ELEGANT format from\n{}
'''.format(inputFile))

        self.Lattice.Name = os.path.basename(inputFile).strip('.lte')

        elements = {}
        line_buffer = ''

        for line in open(inputFile, 'r'):
            lte_line = line.strip()
            if not lte_line or lte_line.startswith('!'): continue
            if lte_line.endswith('&'):
                line_buffer += lte_line.strip('&')
                continue
            if line_buffer:
                lte_line = line_buffer + lte_line
                line_buffer = ''

            if lte_line.startswith("USE") or lte_line.startswith("RETURN"):
                continue

            line_split = lte_line.split(':')
            element_name = line_split[0].strip().strip('\"')
            element_variables = line_split[1].strip()
            if element_variables.startswith("LINE"):
                element_type = element_variables.split('=')[0].strip()
                element_params = element_variables.split('=')[1]
            else:
                element_type = element_variables.split(',')[0].strip()
                element_params = element_variables.split(',')[1:]
                element_params = [e.strip() for e in element_params]

            if element_type == "DRIF":
                length = self.ElementParameter(element_params, 'L')
                drift = Drift(element_name, length)
                elements[element_name] = drift

            elif element_type == "CSBEND":
                length = self.ElementParameter(element_params, 'L')
                angle = self.ElementParameter(element_params, 'ANGLE')
                k1 = self.ElementParameter(element_params, 'K1')
                gap = self.ElementParameter(element_params, 'HGAP')
                fint = self.ElementParameter(element_params, 'FINT')
                if fint is None: fint = 0.5
                dipole = Dipole(element_name, length, angle, None, k1, gap, fint)
                elements[element_name] = dipole

            elif element_type == "KQUAD":
                length = self.ElementParameter(element_params, 'L')
                k1 = self.ElementParameter(element_params, 'K1')
                tilt = self.ElementParameter(element_params, 'TILT')
                if tilt is None:
                    quad = Quad(element_name, length, k1)
                    elements[element_name] = quad
                else:
                    squad = SQuad(element_name, length, k1, tilt)
                    elements[element_name] = squad

            elif element_type == "KSEXT":
                length = self.ElementParameter(element_params, 'L')
                k2 = self.ElementParameter(element_params, 'K2')
                sext = Sext(element_name, length, k2)
                elements[element_name] = sext

            elif element_type == "KOCT":
                length = self.ElementParameter(element_params, 'L')
                k3 = self.ElementParameter(element_params, 'K3')
                octu = Octu(element_name, length, k3)
                elements[element_name] = octu

            elif element_type == "RFCA":
                length = self.ElementParameter(element_params, 'L')
                rf = RF(element_name, length, None, None)
                elements[element_name] = rf

            elif element_type == "LINE":
                lattice_elements = element_params.strip().strip('(').strip(')').split(',')
                for lattice_element in lattice_elements:
                    lattice_element = lattice_element.strip()
                    if lattice_element in elements:
                        self.Lattice.AddElement(elements[lattice_element])
                    else:
                        self.IgnoredElements.append(lattice_element)

            else:
                if element_type not in self.IgnoredElementTypes:
                    self.IgnoredElementTypes.append(element_type)

        if kwargs.get('verbose'):
            self.ReportParseErrors()

        print("Total lattice length {}m.".format(self.Lattice.Length))

        print('''
Completed.
-----------------------------------------------------
''')

    # ---------------------------------------------------------------------------
    def ElementParameter(self, elements, parameter):
        value = None
        for element in elements:
            if element.startswith(parameter):
                value = float(element.split('=')[1].strip().strip(','))
        return value

    # ---------------------------------------------------------------------------
    def WriteLattice(self, **kwargs):

        if 'outputFile' in kwargs and kwargs.get('outputFile') is not None:
            outputFile = kwargs.get('outputFile')
        else:
            outputFile = "{}.lte".format(self.Lattice.Name)

        print('''
-----------------------------------------------------
Writing lattice in ELEGANT format to\n{}
'''.format(outputFile))

        outFile = open(outputFile, 'w')
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

    # ---------------------------------------------------------------------------
    def WriteMiscElements(self, outFile):
        outFile.write('! Misc\n')
        outFile.write('rc: RECIRC\n')
