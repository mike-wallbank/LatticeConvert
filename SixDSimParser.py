# SixDSimParser.py
#
# Implementation of an interface to 6DSim-formatted lattice descriptions.
# Provides input and output (in development) tools.
# M Wallbank, Fermilab <wallbank@fnal.gov>
# July 2023

import os
from LatticeParser import LatticeParser
from LatticeData import *

# ---------------------------------------------------------------------------
class SixDSimParser(LatticeParser):
    def __init__(self, **kwargs):
        LatticeParser.__init__(self)

    # ---------------------------------------------------------------------------
    def ParseInput(self, **kwargs):
        inputFile = kwargs.get('inputFile')
        print('''
-----------------------------------------------------
Importing lattice in 6DSim format from\n{}
'''.format(inputFile))
        
        self.Lattice.Name = os.path.basename(inputFile).strip('.6ds')

        mode = ''
        variables = {}
        elements = {}

        for line in open(inputFile, 'r'):
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
                    line_split[1] = self.ExpandExpression(line_split[1], variables)
                variables[line_split[0].strip()] = self.SolveExpression(line_split[1])

            # Add variables
            if mode != 'INFO':
                if '$c' not in variables:
                    print('INFO (SixDSimParser): Adding \'$c\' = 2.99792458E10 to variables')
                    variables['$c'] = 2.99792458E10
                if '$rigidity' not in variables:
                    if '$pc' not in variables:
                        print("ERROR (SixDSimParser): momentum ($pc) not found in variable list")
                        exit()
                variables['rigidity'] = (variables['$pc']*1.e6) / (variables['$c']*1e-2)

            # Elements
            if mode == 'ELEMENTS' and line.startswith('ID'):
                line_split = line.split()
                element_name = line_split[1]
                element_type = line_split[2]

                if element_type == "Gap":
                    length = self.ElementParameter(line_split, 'L', variables) * 0.01
                    drift = Drift(element_name, length)
                    elements[element_name] = drift

                elif element_type == "Dipole":
                    length = self.ElementParameter(line_split, 'L', variables) * 0.01
                    curvature = self.ElementParameter(line_split, 'Hy', variables)
                    # convert kG to SI and normalize
                    k0 = curvature * 1.e-1 / variables['rigidity']
                    gradient = self.ElementParameter(line_split, 'G', variables)
                    # convert kG/cm to SI and normalize
                    k1 = gradient * 1.e1 / variables['rigidity'] if gradient else 0.
                    inA = self.ElementParameter(line_split, 'inA', variables)
                    outA = self.ElementParameter(line_split, 'outA', variables)
                    gap = self.ElementParameter(line_split, 'poleGap', variables)
                    if gap: gap *= 0.01
                    fringek = self.ElementParameter(line_split, 'fringeK', variables)
                    if fringek: fringek /= 2.
                    dipole = Dipole(element_name, length, None, k0, k1, gap, fringek)
                    elements[element_name] = dipole

                elif element_type == "DipEdge":
                    curvature = self.ElementParameter(line_split, 'Hy', variables)
                    gap = self.ElementParameter(line_split, 'poleGap', variables)
                    if gap: gap *= 0.01
                    inA = self.ElementParameter(line_split, 'inA', variables)
                    fringek = self.ElementParameter(line_split, 'fringeK', variables)
                    if fringek: fringek /= 2.
                    dipedge = DipoleEdge(element_name, curvature, gap, fringek)
                    elements[element_name] = dipedge

                elif element_type == "Quad":
                    length = self.ElementParameter(line_split, 'L', variables) * 0.01
                    gradient = self.ElementParameter(line_split, 'G', variables)
                    # convert kG/cm to SI and normalize
                    k1 = gradient * 1.e1 / variables['rigidity']
                    quad = Quad(element_name, length, k1)
                    elements[element_name] = quad

                elif element_type == "SQuad":
                    length = self.ElementParameter(line_split, 'L', variables) * 0.01
                    gradient = self.ElementParameter(line_split, 'G', variables)
                    k1 = gradient * 10 / variables['rigidity']
                    angle = self.ElementParameter(line_split, 'rotA', variables)
                    squad = SQuad(element_name, length, k1, angle)
                    elements[element_name] = squad

                elif element_type == "Mult":
                    length = self.ElementParameter(line_split, 'L', variables) * 0.01

                    if 'M2N' in line_split:
                        gradient = self.ElementParameter(line_split, 'M2N', variables)
                        # convert kG/cm2 to SI and normalize
                        k2 = gradient * 1.e3 / variables['rigidity']
                        sext = Sext(element_name, length, k2)
                        elements[element_name] = sext

                    elif 'M3N' in line_split:
                        gradient = self.ElementParameter(line_split, 'M3N', variables)
                        # convert kG/cm3 to SI and normalize
                        k3 = gradient * 1.e5 / variables['rigidity']
                        octu = Octu(element_name, length, k3)
                        elements[element_name] = octu

                elif element_type == "Acc":
                    length = self.ElementParameter(line_split, 'L', variables) * 0.01
                    energy = self.ElementParameter(line_split, 'U', variables)
                    frequency = self.ElementParameter(line_split, 'F', variables)
                    rf = RF(element_name, length, energy, frequency)
                    elements[element_name] = rf

                else:
                    if element_type not in self.IgnoredElementTypes:
                        self.IgnoredElementTypes.append(element_type)

            # Lattice
            if mode == 'LATTICE':
                line_split = line.split()
                for lattice_element in line_split:
                    if lattice_element in elements:
                        self.Lattice.AddElement(elements[lattice_element])
                    else:
                        self.IgnoredElements.append(lattice_element)

        # Associate edges to dipoles after reading in complete lattice
        non_edge_dipoles = self.Lattice.AssociateDipoleEdges()

        if kwargs.get('verbose'):
            #print(variables)
            self.ReportParseErrors()
            if non_edge_dipoles:
                self.ReportParseError(non_edge_dipoles, "Dipoles with no edges in the lattice")

        print("Total lattice length {}m.".format(self.Lattice.Length))

        print('''
Completed.
-----------------------------------------------------
''')

    # ---------------------------------------------------------------------------
    def ElementParameter(self, line, parameter, variables):
        value = None
        try:
            index = line.index(parameter)
            value_str = self.ExpandExpression(line[index+1], variables)
            value = self.SolveExpression(value_str)
        except ValueError:
            self.MissingParameters.append("Parameter {} not found for element {} ({})"
                                          .format(parameter, line[1], line[2]))
        return value

    # ---------------------------------------------------------------------------
    def WriteLattice(self):
        pass
