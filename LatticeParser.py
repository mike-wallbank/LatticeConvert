# LatticeParser.py
#
# Template interface to a generic lattice parser.
# Intended to be 'pure virtual' (if such a concept exists in Python!).
# M Wallbank, Fermilab <wallbank@fnal.gov>
# July 2023

from math import *
import re

class LatticeParser:
    def __init__(self):
        self.InvalidExpressions = []
        self.InvalidVariables = []
        self.IgnoredElementTypes = []
        self.MissingParameters = []
        self.IgnoredElements = []

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

    def SolveExpression(self, expression):
        value = None
        try:
            value = eval(expression)
        except NameError:
            self.InvalidExpressions.append(expression.strip())
        return value
