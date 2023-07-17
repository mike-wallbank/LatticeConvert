# LatticeParser.py
#
# Template interface to a generic lattice parser.
# Intended to be 'pure virtual' (if such a concept exists in Python!).
# M Wallbank, Fermilab <wallbank@fnal.gov>
# July 2023

from abc import abstractmethod
from math import *
import re
from LatticeData import Lattice

# ---------------------------------------------------------------------------
class LatticeParser:
    def __init__(self):
        self.Lattice = Lattice()

        self.InvalidExpressions = []
        self.InvalidVariables = []
        self.IgnoredElementTypes = []
        self.MissingParameters = []
        self.IgnoredElements = []

    # ---------------------------------------------------------------------------
    def ExpandExpression(self, expression, variables):
        variables_in_expr = re.split('[+ \- * / ( )]', expression)
        for variable in variables_in_expr:
            if variable in variables:
                expression = expression.replace(variable,
                                                str(variables[variable]),
                                                1).strip()
        if '$' in expression:
            self.InvalidVariables.append(expression)
        return expression

    # ---------------------------------------------------------------------------
    def LoadLattice(self, lattice):
        self.Lattice = lattice

    # ---------------------------------------------------------------------------
    def ReportParseErrors(self):
        self.ReportParseError(self.InvalidExpressions, "Invalid expressions")
        self.ReportParseError(self.InvalidVariables, "Lines with invalid variables")
        self.ReportParseError(self.IgnoredElementTypes, "Ignored element types")
        self.ReportParseError(self.MissingParameters, "Missing parameters")
        self.ReportParseError(self.IgnoredElements, "Ignored lattice elements")

    # ---------------------------------------------------------------------------
    def ReportParseError(self, report, description):
        if len(report):
            print("{} ({}):".format(description, len(report)))
            for item in report:
                print('  {}'.format(item))

    # ---------------------------------------------------------------------------
    def SolveExpression(self, expression):
        value = None
        try:
            value = eval(expression)
        except NameError:
            self.InvalidExpressions.append(expression.strip())
        return value

    # ---------------------------------------------------------------------------
    @abstractmethod
    def ParseInput(self):
        pass

    # ---------------------------------------------------------------------------
    @abstractmethod
    def WriteLattice(self):
        pass
