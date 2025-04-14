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
    def AddBeamline(self, elements, beamlines, line):
        for line_element in beamlines[line]:
            if line_element in beamlines:
                self.AddBeamline(elements, beamlines, line_element)
            elif line_element in elements:
                self.Lattice.AddElement(elements[line_element])
            else:
                self.IgnoredElements.append(line_element)

    # ---------------------------------------------------------------------------
    def ParseInput(self, **kwargs):
        inputFile = kwargs.get('inputFile')
        beamline = kwargs.get('beamline')
        print('''
-----------------------------------------------------
Importing lattice in ELEGANT format from\n{}
'''.format(inputFile))

        self.Lattice.Name = os.path.basename(inputFile).strip('.lte')

        elements = {}
        beamlines = {}
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

            if element_type == "DRIF" or element_type == "EDRIFT":
                length = self.ElementParameter(element_params, 'L', default=0.)
                drift = Drift(element_name, length=length)
                elements[element_name] = drift

            elif element_type == "CSBEND":
                length = self.ElementParameter(element_params, 'L')
                angle = self.ElementParameter(element_params, 'ANGLE')
                k1 = self.ElementParameter(element_params, 'K1', default=0.)
                e1 = self.ElementParameter(element_params, 'E1', default=0.)
                e2 = self.ElementParameter(element_params, 'E2', default=0.)
                gap = self.ElementParameter(element_params, 'HGAP', default=0.)
                fint = self.ElementParameter(element_params, 'FINT', default=0.5)
                dipole = Dipole(element_name, length=length, angle=angle, k1=k1,
                                e1=e1, e2=e2, gap=gap, fringek=fint)
                elements[element_name] = dipole

            elif element_type == "KQUAD":
                length = self.ElementParameter(element_params, 'L')
                k1 = self.ElementParameter(element_params, 'K1', default=0.)
                tilt = self.ElementParameter(element_params, 'TILT')
                if tilt is None:
                    quad = Quad(element_name, length=length, k1=k1)
                    elements[element_name] = quad
                else:
                    squad = SQuad(element_name, length=length, k1=k1, tilt=tilt)
                    elements[element_name] = squad

            elif element_type == "KSEXT":
                length = self.ElementParameter(element_params, 'L')
                k2 = self.ElementParameter(element_params, 'K2', default=0.)
                sext = Sext(element_name, length=length, k2=k2)
                elements[element_name] = sext

            elif element_type == "KOCT":
                length = self.ElementParameter(element_params, 'L')
                k3 = self.ElementParameter(element_params, 'K3', default=0.)
                octu = Octu(element_name, length=length, k3=k3)
                elements[element_name] = octu

            elif element_type == "RFCA":
                length = self.ElementParameter(element_params, 'L')
                rf = RF(element_name, length=length)
                elements[element_name] = rf

            elif element_type == "SOLE":
                length = self.ElementParameter(element_params, 'L')
                solenoid = Solenoid(element_name, length=length)
                elements[element_name] = solenoid

            elif element_type == "LINE":
                lattice_elements = element_params.strip().strip('(').strip(')').split(',')
                for lattice_element in lattice_elements:
                    lattice_element = lattice_element.strip()
                if element_name == beamline:
                    for lattice_element in lattice_elements:
                        if lattice_element in beamlines:
                            self.AddBeamline(elements, beamlines, lattice_element)
                        elif lattice_element in elements:
                            self.Lattice.AddElement(elements[lattice_element])
                        else:
                            self.IgnoredElements.append(lattice_element)
                else:
                    beamlines[element_name] = lattice_elements

            else:
                if element_type not in self.IgnoredElementTypes:
                    self.IgnoredElementTypes.append(element_type)

        # Measure the length of the lattice
        self.Lattice.MeasureLength()

        if kwargs.get('verbose'):
            self.ReportParseErrors()

        self.Lattice.MeasureLength()

        print("Total lattice length {}m.".format(self.Lattice.Length))

        print('''
Completed.
-----------------------------------------------------
''')

    # ---------------------------------------------------------------------------
    def ElementParameter(self, elements, parameter, default=None):
        value = default
        for element in elements:
            if element.startswith(parameter):
                value = float(element.split('=')[1].strip().strip(','))
        return value

    # ---------------------------------------------------------------------------
    def WriteLattice(self, **kwargs):

        if kwargs.get('outputFile', None) is not None:
            outputFile = kwargs.get('outputFile')
        else:
            outputFile = "{}.lte".format(self.Lattice.Name)

        print('''
-----------------------------------------------------
Writing lattice in ELEGANT format to\n{}
'''.format(outputFile))

        access_mode = 'a' if kwargs.get('append', False) else 'w'
        outFile = open(outputFile, access_mode)
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
            self.Lattice.Quads[quad].WriteElegant(outFile,
                                                  kick=True, n_slices=10, synch_rad=True, k1_zero=kwargs.get("k1_zero", False))
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
        if kwargs.get('recirc', False):
            self.WriteMiscElements(outFile)
            outFile.write('\n')

        # Write lattice
        outFile.write('! Lines\n')
        if kwargs.get('recirc', False):
            outFile.write("{}: LINE = (rc, ".format(self.Lattice.Name))
        else:
            outFile.write("{}: LINE = (".format(self.Lattice.Name))
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
