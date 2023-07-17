# LatticeData.py
#
# Definitions of data structures to hold generic information about a lattice.
# M Wallbank, Fermilab <wallbank@fnal.gov>
# July 2023

class Drift:
    def __init__(self, name, length):
        self.Name = name
        self.Length = length
        if self.Length is None: self.Length = 0.

    def WriteElegant(self, outFile):
        outFile.write("{}: DRIF, L={}\n".format(self.Name, self.Length))

    def WriteMADX(self, outFile):
        outFile.write("{}: DRIFT, L={};\n".format(self.Name, self.Length))

class RF:
    def __init__(self, name, length, energy, frequency):
        self.Name = name
        self.Length = length
        self.Energy = energy
        self.Frequency = frequency

    def WriteElegant(self, outFile):
        outFile.write("{}: RFCA, L={}, CHANGE_T=1\n".format(self.Name, self.Length))

    def WriteMADX(self, outFile):
        outFile.write("{}: RFCAVITY, L={}, VOLT=3e-5, LAG=0, HARMON=4;\n".format(self.Name, self.Length))

class DipoleEdge:
    def __init__(self, name, k0, gap, fringek):
        self.Name = name
        self.K0 = k0
        self.Gap = gap
        self.FringeK = fringek

class Dipole:
    def __init__(self, name, length, angle, k0, k1, gap, fringek):
        self.Name = name
        self.Length = length
        self.Angle = angle
        self.K0 = k0
        self.K1 = k1
        self.Gap = gap
        self.FringeK = fringek
        self.UpEdge = None
        self.DownEdge = None
        if self.Angle is None:
            self.Angle = self.K0 * self.Length if self.K0 else 0.
        if self.K0 is None:
            self.K0 = self.Angle / self.Length if self.Angle else 0.
        if self.K1 is None: self.K1 = 0.

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
                      .format(self.Name, self.Length, self.Angle, self.K1, self.Gap, self.FringeK, n_slices, int(synch_rad), int(synch_rad)))

    def WriteMADX(self, outFile):
        outFile.write("IN{}: DIPEDGE, H={}, HGAP={}, FINT={};\n"
                      .format(self.Name, self.Angle/self.Length, self.Gap, self.FringeK))
        outFile.write("{}: SBEND, L={}, ANGLE={}, K1={};\n"
                      .format(self.Name, self.Length, self.Angle, self.K1))
        outFile.write("OUT{}: DIPEDGE, H={}, HGAP={}, FINT={};\n"
                      .format(self.Name, self.Angle/self.Length, self.Gap, self.FringeK))

class Quad:
    def __init__(self, name, length, k1):
        self.Name = name
        self.Length = length
        self.K1 = k1
        if self.K1 is None: self.K1 = 0.

    def WriteElegant(self, outFile, kick=True, n_slices=10, synch_rad=True):
        quadType = "KQUAD" if kick else "QUAD"
        outFile.write("{}: {}, L={}, n_slices={}, synch_rad={}, K1={}\n"
                      .format(self.Name, quadType, self.Length, n_slices, int(synch_rad), self.K1))

    def WriteMADX(self, outFile):
        outFile.write("{}: QUADRUPOLE, L={}, K1={};\n".format(self.Name, self.Length, self.K1))

class SQuad:
    def __init__(self, name, length, k1, tilt):
        self.Name = name
        self.Length = length
        self.K1 = k1
        self.Tilt = tilt
        if self.K1 is None: self.K1 = 0.
        if self.Tilt is None: self.Tilt = 0.

    def WriteElegant(self, outFile, kick=True, n_slices=10, synch_rad=True):
        quadType = "KQUAD" if kick else "QUAD"
        outFile.write("{}: {}, L={}, n_slices={}, synch_rad={}, K1={}, TILT={}\n"
                      .format(self.Name, quadType, self.Length, n_slices, int(synch_rad), self.K1, self.Tilt))

    def WriteMADX(self, outFile):
        outFile.write("{}: QUADRUPOLE, L={}, K1S={};\n".format(self.Name, self.Length, self.K1))

class Sext:
    def __init__(self, name, length, k2):
        self.Name = name
        self.Length = length
        self.K2 = k2
        if self.K2 is None: self.K2 = 0.

    def WriteElegant(self, outFile, kick=True, n_slices=10, synch_rad=True):
        sextType = "KSEXT" if kick else "SEXT"
        outFile.write("{}: {}, L={}, n_slices={}, synch_rad={}, K2={}\n"
                      .format(self.Name, sextType, self.Length, n_slices, int(synch_rad), self.K2))

    def WriteMADX(self, outFile):
        outFile.write("{}: SEXTUPOLE, L={}, K2={};\n".format(self.Name, self.Length, self.K2))

class Octu:
    def __init__(self, name, length, k3):
        self.Name = name
        self.Length = length
        self.K3 = k3
        if self.K3 is None: self.K3 = 0.

    def WriteElegant(self, outFile, kick=True, n_slices=10, synch_rad=True):
        octuType = "KOCT" if kick else "OCTU"
        outFile.write("{}: {}, L={}, n_slices={}, synch_rad={}, K3={}\n"
                      .format(self.Name, octuType, self.Length, n_slices, int(synch_rad), self.K3))

    def WriteMADX(self, outFile):
        outFile.write("{}: OCTUPOLE, L={}, K3={};\n".format(self.Name, self.Length, self.K3))

class Lattice:
    def __init__(self):
        self.Name = "Lattice"
        self.Sequence = []
        self.Locations = {}
        self.Length = 0.
        self.Elements = {}
        self.Drifts = {}
        self.RF = {}
        self.Dipoles = {}
        self.DipoleEdges = {}
        self.Quads = {}
        self.SkewQuads = {}
        self.Sexts = {}
        self.Octus = {}

    def AddElement(self, element):

        # Add length to the sequence
        if element.Name in self.Sequence:
            self.Locations[element.Name].append(self.Locations[element.Name][-1])
            last_occurance = max(i for i,e in enumerate(self.Sequence) if e == element.Name)
            for index in range(len(self.Sequence)-last_occurance):
                inter_lattice_element = self.Elements[self.Sequence[last_occurance+index]]
                if hasattr(inter_lattice_element, 'Length'):
                    self.Locations[element.Name][-1] += inter_lattice_element.Length
        else:
            self.Locations[element.Name] = [self.Length]
        if hasattr(element, 'Length'):
            self.Length += element.Length

        # Add element to the sequence
        self.Elements[element.Name] = element
        self.Sequence.append(element.Name)

        # Add element to the definitions
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
