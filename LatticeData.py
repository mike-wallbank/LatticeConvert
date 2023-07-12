# LatticeData.py
#
# Definitions of data structures to hold generic information about a lattice.
# M Wallbank, Fermilab <wallbank@fnal.gov>
# July 2023

class Drift:
    def __init__(self, name, length):
        self.Name = name
        self.Length = length

    def WriteElegant(self, outFile):
        outFile.write("{}: DRIF, L={}\n".format(self.Name, self.Length))

class RF:
    def __init__(self, name, length, energy, frequency):
        self.Name = name
        self.Length = length
        self.Energy = energy
        self.Frequency = frequency

    def WriteElegant(self, outFile):
        outFile.write("{}: RFCA, L={}, CHANGE_T=1\n".format(self.Name, self.Length))

class DipoleEdge:
    def __init__(self, name, k0, gap, fringek):
        self.Name = name
        self.K0 = k0
        self.Gap = gap
        self.FringeK = fringek

class Dipole:
    def __init__(self, name, length, k0, k1, angle, gap, fringek):
        self.Name = name
        self.Length = length
        self.K0 = k0
        self.K1 = k1
        self.Angle = angle
        self.Gap = gap
        self.FringeK = fringek
        self.UpEdge = None
        self.DownEdge = None

        if not self.Angle:
            self.Angle = self.K0 * self.Length if self.K0 else 0

    def AddUpEdge(self, edge):
        self.UpEdge = edge
        if self.Gap is None: self.Gap = edge.Gap
        if self.FringeK is None: self.FringeK = edge.FringeK

    def AddDownEdge(self, edge):
        self.DownEdge = edge
        if self.Gap == None: self.Gap = edge.Gap
        if self.FringeK == None: self.FringeK = edge.FringeK

    def WriteElegant(self, outFile, n_slices=10, synch_rad=True):
        outFile.write("{}: CSBEND, L={}, ANGLE={}, K1={}, HGAP={}, FINT={}, INTEGRATION_ORDER=4, n_slices={}, synch_rad={}, isr={}\n"
                      .format(self.Name, self.Length, self.Angle, self.K1, self.Gap, self.FringeK/2., n_slices, int(synch_rad), int(synch_rad)))

class Quad:
    def __init__(self, name, length, k1):
        self.Name = name
        self.Length = length
        self.K1 = k1

    def WriteElegant(self, outFile, kick=True, n_slices=10, synch_rad=True):
        quadType = "KQUAD" if kick else "QUAD"
        outFile.write("{}: {}, L={}, n_slices={}, synch_rad={}, K1={}\n"
                      .format(self.Name, quadType, self.Length, n_slices, int(synch_rad), self.K1))

class SQuad:
    def __init__(self, name, length, k1, angle):
        self.Name = name
        self.Length = length
        self.K1 = k1
        self.Angle = angle
        if not self.Angle: self.Angle = 0

    def WriteElegant(self, outFile, kick=True, n_slices=10, synch_rad=True):
        quadType = "KQUAD" if kick else "QUAD"
        outFile.write("{}: {}, L={}, n_slices={}, synch_rad={}, K1={}, TILT={}\n"
                      .format(self.Name, quadType, self.Length, n_slices, int(synch_rad), self.K1, self.Angle))

class Sext:
    def __init__(self, name, length, k2):
        self.Name = name
        self.Length = length
        self.K2 = k2

    def WriteElegant(self, outFile, kick=True, n_slices=10, synch_rad=True):
        sextType = "KSEXT" if kick else "SEXT"
        outFile.write("{}: {}, L={}, n_slices={}, synch_rad={}, K2={}\n"
                      .format(self.Name, sextType, self.Length, n_slices, int(synch_rad), self.K2))

class Octu:
    def __init__(self, name, length, k3):
        self.Name = name
        self.Length = length
        self.K3 = k3

    def WriteElegant(self, outFile, kick=True, n_slices=10, synch_rad=True):
        octuType = "KOCT" if kick else "OCTU"
        outFile.write("{}: {}, L={}, n_slices={}, synch_rad={}, K3={}\n"
                      .format(self.Name, octuType, self.Length, n_slices, int(synch_rad), self.K3))

class Lattice:
    def __init__(self):
        self.Sequence = []
        self.Drifts = {}
        self.RF = {}
        self.Dipoles = {}
        self.DipoleEdges = {}
        self.Quads = {}
        self.SkewQuads = {}
        self.Sexts = {}
        self.Octus = {}

    def AddElement(self, element):
        self.Sequence.append(element.Name)
        if element.__class__.__name__ == "Drift": self.Drifts[element.Name] = element
        if element.__class__.__name__ == "RF": self.RF[element.Name] = element
        if element.__class__.__name__ == "Dipole": self.Dipoles[element.Name] = element
        if element.__class__.__name__ == "DipoleEdge": self.DipoleEdges[element.Name] = element
        if element.__class__.__name__ == "Quad": self.Quads[element.Name] = element
        if element.__class__.__name__ == "SQuad": self.SkewQuads[element.Name] = element
        if element.__class__.__name__ == "Sext": self.Sexts[element.Name] = element
        if element.__class__.__name__ == "Octu": self.Octus[element.Name] = element

    def AssociateDipoleEdges(self):
        non_edge_dipoles = []
        if not self.DipoleEdges:
            return
        for dipole in self.Dipoles:
            try:
                index = self.Sequence.index(dipole)
            except ValueError:
                continue
            upEdge = self.Sequence[index-1]
            downEdge = self.Sequence[index+1]
            if upEdge not in self.DipoleEdges or downEdge not in self.DipoleEdges:
                non_edge_dipoles.append(dipole)
            else:
                self.Dipoles[dipole].AddUpEdge(self.DipoleEdges[upEdge])
                self.Dipoles[dipole].AddDownEdge(self.DipoleEdges[downEdge])
        return non_edge_dipoles
