# LatticeData.py
#
# Definitions of data structures to hold generic information about a lattice.
# M Wallbank, Fermilab <wallbank@fnal.gov>
# July 2023

import numpy as np

class Element:
    def __init__(self, name, **kwargs):
        self.Name = name
        self.Center = kwargs.get('center') if 'center' in kwargs else None

class Drift(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.Length = kwargs.get('length')

    def WriteElegant(self, outFile):
        outFile.write("{}: DRIF, L={}\n".format(self.Name, self.Length))

    def WriteMADX(self, outFile):
        outFile.write("{}: DRIFT, L={};\n".format(self.Name, self.Length))

class RF(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.Length = kwargs.get('length')
        self.Energy = kwargs.get('energy') if 'energy' in kwargs else None
        self.Frequency = kwargs.get('frequency') if 'frequency' in kwargs else None

    def WriteElegant(self, outFile):
        outFile.write("{}: RFCA, L={}, CHANGE_T=1\n".format(self.Name, self.Length))

    def WriteMADX(self, outFile):
        outFile.write("{}: RFCAVITY, L={}, VOLT=3e-5, LAG=0, HARMON=4;\n".format(self.Name, self.Length))

class DipoleEdge(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.Angle = kwargs.get('angle', None)
        self.E1 = kwargs.get('e1', None)
        self.K0 = kwargs.get('k0', None)
        self.Gap = kwargs.get('gap', None)
        self.FringeK = kwargs.get('fringek', None)

class Dipole(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.UpEdge = None
        self.DownEdge = None
        self.Sector = True
        self.Length = kwargs.get('length', None)
        self.Angle = kwargs.get('angle', None)
        self.K0 = kwargs.get('k0', None)
        self.K1 = kwargs.get('k1', 0.)
        self.Gap = kwargs.get('gap', 0.)
        self.FringeK = kwargs.get('fringek', 0.)
        self.E1 = kwargs.get('e1', 0.)
        self.E2 = kwargs.get('e2', 0.)
        if self.Angle is None:
            self.Angle = self.K0 * self.Length if self.K0 else 0.
        if self.K0 is None:
            self.K0 = self.Angle / self.Length if self.Angle else 0.

    def AddUpEdge(self, edge):
        self.UpEdge = edge
        if self.Gap is None: self.Gap = edge.Gap
        if self.FringeK is None: self.FringeK = edge.FringeK
        if edge.E1 is not None: self.E1 = edge.E1

    def AddDownEdge(self, edge):
        self.DownEdge = edge
        if self.Gap == None: self.Gap = edge.Gap
        if self.FringeK == None: self.FringeK = edge.FringeK
        if edge.E1 is not None: self.E2 = edge.E1

    def WriteElegant(self, outFile, n_slices=10, synch_rad=True):
        if self.Gap is None: self.Gap = 0.
        if self.FringeK is None: self.FringeK = 0.
        if self.Sector:
            outFile.write("{}: CSBEND, L={}, ANGLE={}, K1={}, HGAP={}, FINT={}, INTEGRATION_ORDER=4, N_SLICES={}, SYNCH_RAD={}, ISR={}\n"
                          .format(self.Name, self.Length, self.Angle, self.K1, self.Gap, self.FringeK, n_slices, int(synch_rad), int(synch_rad)))
        else:
            length = self.Length * np.sin(self.Angle) / self.Angle
            edge_angle = self.Angle
            outFile.write("{}: CSBEND, L={}, ANGLE={}, K1={}, HGAP={}, FINT={}, E1={}, E2={}, INTEGRATION_ORDER=4, N_SLICES={}, SYNCH_RAD={}, ISR={}\n"
                          .format(self.Name, length, self.Angle, self.K1, self.Gap, self.FringeK, edge_angle, edge_angle,
                                  n_slices, int(synch_rad), int(synch_rad)))

    def WriteMADX(self, outFile):
        outFile.write("IN{}: DIPEDGE, H={}, HGAP={}, FINT={}, E1={};\n"
                      .format(self.Name, self.Angle/self.Length, self.Gap, self.FringeK, self.E1))
        outFile.write("{}: SBEND, L={}, ANGLE={}, K1={};\n"
                      .format(self.Name, self.Length, self.Angle, self.K1))
        outFile.write("OUT{}: DIPEDGE, H={}, HGAP={}, FINT={}, E1={};\n"
                      .format(self.Name, self.Angle/self.Length, self.Gap, self.FringeK, self.E2))

class Quad(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.Length = kwargs.get('length')
        self.K1 = kwargs.get('k1', 0.)

    def WriteElegant(self, outFile, **kwargs):
        quadType = "KQUAD" if kwargs.get("kick", True) else "QUAD"
        outFile.write("{}: {}, L={}, N_SLICES={}, SYNCH_RAD={}, K1={}\n"
                      .format(self.Name, quadType, self.Length, kwargs.get("n_slices"), int(kwargs.get("synch_rad")),
                              self.K1 if not kwargs.get("k1_zero") else 0.))

    def WriteMADX(self, outFile):
        outFile.write("{}: QUADRUPOLE, L={}, K1={};\n".format(self.Name, self.Length, self.K1))

class SQuad(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.Length = kwargs.get('length')
        self.K1 = kwargs.get('k1', 0.)
        self.Tilt = kwargs.get('tilt', 0.)

    def WriteElegant(self, outFile, kick=True, n_slices=10, synch_rad=True):
        quadType = "KQUAD" if kick else "QUAD"
        outFile.write("{}: {}, L={}, N_SLICES={}, SYNCH_RAD={}, K1={}, TILT={}\n"
                      .format(self.Name, quadType, self.Length, n_slices, int(synch_rad), self.K1, self.Tilt))

    def WriteMADX(self, outFile):
        outFile.write("{}: QUADRUPOLE, L={}, K1S={};\n".format(self.Name, self.Length, self.K1))

class Sext(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.Length = kwargs.get('length')
        self.K2 = kwargs.get('k2', 0.)

    def WriteElegant(self, outFile, kick=True, n_slices=10, synch_rad=True):
        sextType = "KSEXT" if kick else "SEXT"
        outFile.write("{}: {}, L={}, N_SLICES={}, SYNCH_RAD={}, K2={}\n"
                      .format(self.Name, sextType, self.Length, n_slices, int(synch_rad), self.K2))

    def WriteMADX(self, outFile):
        outFile.write("{}: SEXTUPOLE, L={}, K2={};\n".format(self.Name, self.Length, self.K2))

class Octu(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.Length = kwargs.get('length')
        self.K3 = kwargs.get('k3', 0.)

    def WriteElegant(self, outFile, kick=True, n_slices=10, synch_rad=True):
        octuType = "KOCT" if kick else "OCTU"
        outFile.write("{}: {}, L={}, N_SLICES={}, SYNCH_RAD={}, K3={}\n"
                      .format(self.Name, octuType, self.Length, n_slices, int(synch_rad), self.K3))

    def WriteMADX(self, outFile):
        outFile.write("{}: OCTUPOLE, L={}, K3={};\n".format(self.Name, self.Length, self.K3))

class Solenoid(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.Length = kwargs.get('length')

    def WriteMADX(self, outFile):
        outFile.write("{}: DRIFT, L={};\n".format(self.Name, self.Length))

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
        self.Solenoids = {}

    def AddElement(self, element, **kwargs):

        # Log the location of the element in the beamline
        if element.Center is not None:
            if hasattr(element, 'Length'):
                self.Locations[element.Name] = [element.Center - element.Length/2.]
            else:
                self.Locations[element.Name] = [element.Center]
        else:
            if element.Name in self.Sequence:
                self.Locations[element.Name].append(self.Locations[element.Name][-1])
                last_occurance = max(i for i,e in enumerate(self.Sequence) if e == element.Name)
                for index in range(len(self.Sequence)-last_occurance):
                    inter_lattice_element = self.Elements[self.Sequence[last_occurance+index]]
                    if hasattr(inter_lattice_element, 'Length'):
                        self.Locations[element.Name][-1] += inter_lattice_element.Length
            else:
                self.MeasureLength()
                self.Locations[element.Name] = [self.Length]

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
        if element.__class__.__name__ == "Solenoid": self.Solenoids[element.Name] = element

    def AssociateDipoleEdges(self):
        """Associate dipole edges with the dipole elements through their locations in a lattice sequence."""

        non_edge_dipoles = []
        if not self.DipoleEdges:
            return
        for dipole in self.Dipoles:
            try:
                index = self.Sequence.index(dipole)
            except ValueError:
                continue
            if index-1 < 0 or index+1 >= len(self.Sequence):
                non_edge_dipoles.append(dipole)
                continue
            upEdge = self.Sequence[index-1]
            downEdge = self.Sequence[index+1]
            if upEdge not in self.DipoleEdges or downEdge not in self.DipoleEdges:
                non_edge_dipoles.append(dipole)
                continue
            self.Dipoles[dipole].AddUpEdge(self.DipoleEdges[upEdge])
            self.Dipoles[dipole].AddDownEdge(self.DipoleEdges[downEdge])
            print("Adding edges {} and {} to dipole {}".format(upEdge, downEdge, dipole))
        return non_edge_dipoles

    def InsertDrifts(self, mode):
        """Insert drifts into a lattice defined as a line."""

        lattice_length = self.Length
        lattice_coordinate = 0.
        drift_index = 0
        drifts = {}
        for lte_index,lte_element in enumerate(self.Sequence):
            lte_location = self.Locations[lte_element][0]
            drift_length = lte_location - lattice_coordinate
            if drift_length > 0.:
                drift = Drift("drift"+str(drift_index), length=drift_length)
                self.Elements[drift.Name] = drift
                self.Drifts[drift.Name] = drift
                drifts[drift.Name] = lte_index+drift_index
                drift_index += 1
            lattice_coordinate += drift_length
            if hasattr(self.Elements[lte_element], 'Length'):
                lattice_coordinate += self.Elements[lte_element].Length
        for drift in drifts:
            self.Sequence.insert(drifts[drift], drift)
        self.MeasureLength()

        ends_drift_length = lattice_length - self.Length
        if mode == "both":
            start_drift = Drift("drift_start", length=ends_drift_length/2.)
            self.Elements[start_drift.Name] = start_drift
            self.Drifts[start_drift.Name] = start_drift
            self.Sequence.insert(0, start_drift.Name)
            end_drift = Drift("drift_end", length=ends_drift_length/2.)
            self.Elements[end_drift.Name] = end_drift
            self.Drifts[end_drift.Name] = end_drift
            self.Sequence.append(end_drift.Name)
        elif mode == "end":
            end_drift = Drift("drift_end", length=ends_drift_length)
            self.Elements[end_drift.Name] = end_drift
            self.Drifts[end_drift.Name] = end_drift
            self.Sequence.append(end_drift.Name)
        self.MeasureLength()
        print("Length of lattice after adding drifts {} (defintion {})".format(self.Length, lattice_length))
        
    def MeasureLength(self):
        """Measure the length of the lattice by summing up all of the elements in the sequence."""

        self.Length = 0.
        for element in self.Sequence:
            if hasattr(self.Elements[element], 'Length'):
                self.Length += self.Elements[element].Length

