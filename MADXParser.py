# MADXParser.py
#
# Implementation of an interface to MADX-formatted lattice descriptions.
# Provides input (in development) and output tools.
# M Wallbank, Fermilab <wallbank@fnal.gov>
# July 2023

import os, copy
from LatticeParser import LatticeParser
from LatticeData import *
from datetime import datetime

# ---------------------------------------------------------------------------
class MADXParser(LatticeParser):
    def __init__(self, **kwargs):
        LatticeParser.__init__(self)

    # ---------------------------------------------------------------------------
    def ParseInput(self, **kwargs):
        inputFile = kwargs.get('inputFile')
        print('''
-----------------------------------------------------
Importing lattice in MAD-X format from\n{}
'''.format(inputFile))

        self.Lattice.Name = os.path.basename(inputFile).strip('.seq')

        variables = {}
        elements = {}
        in_sequence = False

        for line in open(inputFile, 'r'):
            lte_line = line.strip()
            if not lte_line or lte_line.startswith('!') or not lte_line.endswith(';'): continue
            lte_line = lte_line.strip(';')

            # Sequence
            if lte_line.startswith("endsequence"):
                in_sequence = False
                continue
            if in_sequence:
                if ':' in lte_line:
                    line_split = lte_line.split(':')
                    element_name = line_split[0].strip()
                    element_type = line_split[1].split(',')[0].strip()
                    element_params = line_split[1].split(',')[1:]
                    element_params = [e.strip() for e in element_params]
                else:
                    element_name = lte_line.split(',')[0].strip()
                    element_type = element_name
                    element_params = lte_line.split(',')[1:]
                    element_params = [e.strip() for e in element_params]
                if element_type in elements:
                    lattice_element = copy.deepcopy(elements[element_type])
                    at = self.ElementParameter(element_params, 'at', variables)
                    lattice_element.Name = element_name
                    lattice_element.Center = at
                    self.Lattice.AddElement(lattice_element, measure_length=False)
                else:
                    self.IgnoredElements.append(element_name)

            # Variables
            first_colon = lte_line.find(':')
            if first_colon < 0 or lte_line[first_colon+1] == '=':
                parameter = lte_line.split(':=') if ':' in lte_line else lte_line.split('=')
                variables[parameter[0].strip()] = parameter[1].strip()
                continue

            # Elements
            line_split = lte_line.split(':')
            element_name = line_split[0].strip()
            element_variables = lte_line.strip(element_name+':').strip()
            element_params = element_variables.split(',')[1:]
            element_params = [e.strip() for e in element_params]

            if len(element_params) and element_params[0] in elements:
                element = copy.deepcopy(elements[element_params[0]])
                elements[element_name] = element

            if element_variables.startswith("sbend") or element_variables.startswith("rbend"):
                length = self.ElementParameter(element_params, 'l', variables)
                angle = self.ElementParameter(element_params, 'angle', variables)
                e1 = self.ElementParameter(element_params, 'e1', variables)
                e2 = self.ElementParameter(element_params, 'e2', variables)
                dipole = Dipole(element_name, length=length, angle=angle, e1=e1, e2=e2)
                if element_variables.startswith("rbend"):
                    dipole.Sector = False
                elements[element_name] = dipole

            if element_variables.startswith("dipedge"):
                e1 = self.ElementParameter(element_params, 'e1', variables)
                angle = self.ElementParameter(element_params, 'h', variables)
                hgap = self.ElementParameter(element_params, 'hgap', variables)
                fint = self.ElementParameter(element_params, 'fint', variables)
                dipole_edge = DipoleEdge(element_name, angle=angle, e1=e1, gap=hgap, fringek=fint)
                elements[element_name] = dipole_edge

            if element_variables.startswith("quad"):
                length = self.ElementParameter(element_params, 'l', variables)
                k1 = self.ElementParameter(element_params, 'k1', variables)
                quad = Quad(element_name, length=length, k1=k1)
                elements[element_name] = quad

            if element_variables.startswith("sequence"):
                self.Lattice.Name = element_name
                length = self.ElementParameter(element_params, 'l', variables)
                self.Lattice.Length = length
                refer = self.ElementParameter(element_params, 'refer', variables)
                if refer is not None and refer != 'center':
                    raise RuntimeError("MADXParser currently works with coordinates referring to the element center.")
                in_sequence = True

        # Associate edges to dipoles after reading in complete lattice
        non_edge_dipoles = self.Lattice.AssociateDipoleEdges()

        self.Lattice.MeasureLength()
        print("Before inserting drifts, lattice length {}".format(self.Lattice.Length))

        # Insert drifts into lattice
        self.Lattice.InsertDrifts()

        self.Lattice.MeasureLength()
        print("After inserting drifts, lattice length {}".format(self.Lattice.Length))

        if kwargs.get('verbose'):
            self.ReportParseErrors()
            if non_edge_dipoles:
                self.ReportParseError(non_edge_dipoles, "Dipoles with no edges in the lattice")

#             line_split = lte_line.split(':')
#             element_name = line_split[0].strip().strip('\"')
#             element_variables = line_split[1].strip()
#             if element_variables.startswith("LINE"):
#                 element_type = element_variables.split('=')[0].strip()
#                 element_params = element_variables.split('=')[1]
#             else:
#                 element_type = element_variables.split(',')[0].strip()
#                 element_params = element_variables.split(',')[1:]
#                 element_params = [e.strip() for e in element_params]

#             if element_type == "DRIF":
#                 length = self.ElementParameter(element_params, 'L')
#                 drift = Drift(element_name, length)
#                 elements[element_name] = drift

#             elif element_type == "CSBEND":
#                 length = self.ElementParameter(element_params, 'L')
#                 angle = self.ElementParameter(element_params, 'ANGLE')
#                 k1 = self.ElementParameter(element_params, 'K1')
#                 gap = self.ElementParameter(element_params, 'HGAP')
#                 fint = self.ElementParameter(element_params, 'FINT')
#                 if fint is None: fint = 0.5
#                 dipole = Dipole(element_name, length, angle, None, k1, gap, fint)
#                 elements[element_name] = dipole

#             elif element_type == "KQUAD":
#                 length = self.ElementParameter(element_params, 'L')
#                 k1 = self.ElementParameter(element_params, 'K1')
#                 tilt = self.ElementParameter(element_params, 'TILT')
#                 if tilt is None:
#                     quad = Quad(element_name, length, k1)
#                     elements[element_name] = quad
#                 else:
#                     squad = SQuad(element_name, length, k1, tilt)
#                     elements[element_name] = squad

#             elif element_type == "KSEXT":
#                 length = self.ElementParameter(element_params, 'L')
#                 k2 = self.ElementParameter(element_params, 'K2')
#                 sext = Sext(element_name, length, k2)
#                 elements[element_name] = sext

#             elif element_type == "KOCT":
#                 length = self.ElementParameter(element_params, 'L')
#                 k3 = self.ElementParameter(element_params, 'K3')
#                 octu = Octu(element_name, length, k3)
#                 elements[element_name] = octu

#             elif element_type == "RFCA":
#                 length = self.ElementParameter(element_params, 'L')
#                 rf = RF(element_name, length, None, None)
#                 elements[element_name] = rf

#             elif element_type == "LINE":
#                 lattice_elements = element_params.strip().strip('(').strip(')').split(',')
#                 for lattice_element in lattice_elements:
#                     lattice_element = lattice_element.strip()
#                     if lattice_element in elements:
#                         self.Lattice.AddElement(elements[lattice_element])
#                     else:
#                         self.IgnoredElements.append(lattice_element)

#             else:
#                 if element_type not in self.IgnoredElementTypes:
#                     self.IgnoredElementTypes.append(element_type)

#         if kwargs.get('verbose'):
#             self.ReportParseErrors()

#         print("Total lattice length {}m.".format(self.Lattice.Length))

#         print('''
# Completed.
# -----------------------------------------------------
# ''')

    # ---------------------------------------------------------------------------
    def ElementParameter(self, elements, parameter, variables):
        value = None
        for element in elements:
            if element.startswith(parameter):
                param_value = element.split(':=')[1].strip() if ':' in element else element.split('=')[1].strip()
                value = self.VariableValue(param_value, variables)
        return value

    # ---------------------------------------------------------------------------
    def VariableValue(self, parameter, variables):
        loop_parameter = parameter
        while loop_parameter in variables:
            loop_parameter = variables[loop_parameter]
        return float(loop_parameter)

    # ---------------------------------------------------------------------------
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
        outFile.write("{}: SEQUENCE, L={}, REFER=ENTRY;\n".format(self.Lattice.Name, self.Lattice.Length))
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
