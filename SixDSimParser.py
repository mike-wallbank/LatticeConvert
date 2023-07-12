# SixDSimParser.py
#
# Implementation of an interface to 6DSim-formatted lattice descriptions.
# Provides input and output (in development) tools.
# M Wallbank, Fermilab <wallbank@fnal.gov>
# July 2023

from LatticeParser import LatticeParser
from LatticeData import *

class SixDSimParser(LatticeParser):
    def __init__(self, **kwargs):
        LatticeParser.__init__(self)
        self.Variables = {}
        self.Elements = {}
        self.Lattice = Lattice()

    def ParseInput(self, **kwargs):
        print('''
-----------------------------------------------------
Importing lattice in 6DSim format from\n{}
'''.format(kwargs.get('inputFile')))

        mode = ''

        for line in open(kwargs.get('inputFile'), 'r'):
            line = line.strip()
            if line.startswith('//'): continue

            # Set mode
            if line == "INFO:":
                mode = 'INFO'
                continue
            if line == "ELEMENTS:":
                mode = 'ELEMENTS'
                continue
            if line == "LATTICE:":
                mode = 'LATTICE'
                continue
            if line == "END":
                mode = 'END'
                break

            # Variables
            if mode == 'INFO' and line.startswith('$'):
                line_split = line.split('=')
                if '$' in line_split[1]:
                    line_split[1] = self.ExpandExpression(line_split[1], self.Variables)
                self.Variables[line_split[0].strip()] = self.SolveExpression(line_split[1])

            # Add variables
            if mode != 'INFO':
                if '$c' not in self.Variables:
                    print('INFO: Adding \'$c\' = 2.99792458E10 to variables')
                    self.Variables['$c'] = 2.99792458E10
                if '$rigidity' not in self.Variables:
                    if '$pc' not in self.Variables:
                        print("ERROR: momentum ($pc) not found in variable list")
                        exit()
                self.Variables['rigidity'] = (self.Variables['$pc']*1.e6) / (self.Variables['$c']*1e-2)

            # Elements
            if mode == 'ELEMENTS' and line.startswith('ID'):
                line_split = line.split()
                element_name = line_split[1]

                if line_split[2] == "Gap":
                    length = self.ElementParameter(line_split, 'L') * 0.01
                    drift = Drift(element_name, length)
                    self.Elements[element_name] = drift

                elif line_split[2] == "Dipole":
                    length = self.ElementParameter(line_split, 'L') * 0.01
                    curvature = self.ElementParameter(line_split, 'Hy')
                    # convert kG to SI and normalize
                    k0 = curvature * 1.e-1 / self.Variables['rigidity']
                    gradient = self.ElementParameter(line_split, 'G')
                    # convert kG/cm to SI and normalize
                    k1 = gradient * 1.e1 / self.Variables['rigidity'] if gradient else 0
                    inA = self.ElementParameter(line_split, 'inA')
                    outA = self.ElementParameter(line_split, 'outA')
                    gap = self.ElementParameter(line_split, 'poleGap')
                    if gap: gap *= 0.01
                    fringek = self.ElementParameter(line_split, 'fringeK')
                    dipole = Dipole(element_name, length, k0, k1, None, gap, fringek)
                    self.Elements[element_name] = dipole

                elif line_split[2] == "DipEdge":
                    curvature = self.ElementParameter(line_split, 'Hy')
                    gap = self.ElementParameter(line_split, 'poleGap')
                    if gap: gap *= 0.01
                    inA = self.ElementParameter(line_split, 'inA')
                    fringek = self.ElementParameter(line_split, 'fringeK')
                    dipedge = DipoleEdge(element_name, curvature, gap, fringek)
                    self.Elements[element_name] = dipedge

                elif line_split[2] == "Quad":
                    length = self.ElementParameter(line_split, 'L') * 0.01
                    gradient = self.ElementParameter(line_split, 'G')
                    # convert kG/cm to SI and normalize
                    k1 = gradient * 1.e1 / self.Variables['rigidity']
                    quad = Quad(element_name, length, k1)
                    self.Elements[element_name] = quad

                elif line_split[2] == "SQuad":
                    length = self.ElementParameter(line_split, 'L') * 0.01
                    gradient = self.ElementParameter(line_split, 'G')
                    k1 = gradient * 10 / self.Variables['rigidity']
                    angle = self.ElementParameter(line_split, 'rotA')
                    squad = SQuad(element_name, length, k1, angle)
                    self.Elements[element_name] = squad

                elif line_split[2] == "Mult":
                    length = self.ElementParameter(line_split, 'L') * 0.01

                    if 'M2N' in line_split:
                        gradient = self.ElementParameter(line_split, 'M2N')
                        # convert kG/cm2 to SI and normalize
                        k2 = gradient * 1.e3 / self.Variables['rigidity']
                        sext = Sext(element_name, length, k2)
                        self.Elements[element_name] = sext

                    elif 'M3N' in line_split:
                        gradient = self.ElementParameter(line_split, 'M3N')
                        # convert kG/cm3 to SI and normalize
                        k3 = gradient * 1.e5 / self.Variables['rigidity']
                        octu = Octu(element_name, length, k3)
                        self.Elements[element_name] = octu

                elif line_split[2] == "Acc":
                    length = self.ElementParameter(line_split, 'L') * 0.01
                    energy = self.ElementParameter(line_split, 'U')
                    frequency = self.ElementParameter(line_split, 'F')
                    rf = RF(element_name, length, energy, frequency)
                    self.Elements[element_name] = rf

                else:
                    if line_split[2] not in self.IgnoredElementTypes:
                        self.IgnoredElementTypes.append(line_split[2])

            # Lattice
            if mode == 'LATTICE':
                line_split = line.split()
                for lattice_element in line_split:
                    if lattice_element in self.Elements:
                        self.Lattice.AddElement(self.Elements[lattice_element])
                    else:
                        self.IgnoredElements.append(lattice_element)

        # Associate edges to dipoles after reading in complete lattice
        non_edge_dipoles = self.Lattice.AssociateDipoleEdges()

        if kwargs.get('verbose'):
            #print(self.Variables)
            self.Report(self.InvalidExpressions, "Invalid expressions")
            self.Report(self.InvalidVariables, "Lines with invalid variables")
            self.Report(self.IgnoredElementTypes, "Ignored element types")
            self.Report(self.MissingParameters, "Missing parameters")
            self.Report(self.IgnoredElements, "Ignored lattice elements")
            if non_edge_dipoles:
                self.Report(non_edge_dipoles, "Dipoles with no edges in the lattice")

        print('''
Completed.
-----------------------------------------------------
''')

    def ElementParameter(self, line, parameter):
        value = None
        try:
            index = line.index(parameter)
            value_str = self.ExpandExpression(line[index+1], self.Variables)
            value = self.SolveExpression(value_str)
        except ValueError:
            self.MissingParameters.append("Parameter {} not found for element {} ({})"
                                          .format(parameter, line[1], line[2]))
        return value

    def Report(self, report, description):
        if len(report):
            print("{} ({}):".format(description, len(report)))
            for item in report:
                print('  {}'.format(item))
