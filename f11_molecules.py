# reboot

import networkx as nx
from random import randint


class Molecule():
    def __init__(self):
        self.structure = nx.Graph()
        self.index = 0
        self.parts = None
    
    def __repr__(self):
        connections = [self.parts[edge[0]] + " - " + self.parts[edge[1]]
                       for edge in self.get_connections()]
        value = ""
        for connection in connections:
            value += connection + "\n"
        if value == "":
            return "empty"
        return value

    def __len__(self):
        return len(self.parts)
    
    def update_parts(self):
        self.parts = self.structure.nodes()
    
    def set_hex(self, style):
        parts = [style + str(i) for i in range(6)]
        self.structure.add_nodes_from(parts)
        
        for i in range(5):
            self.structure.add_edge(parts[i], parts[i+1])
        self.structure.add_edge(parts[0], parts[5])
        self.update_parts()
        self.index = 6
    
    def is_connected(self, position1, position2):
        return self.structure.has_edge(self.parts[position1],
                                       self.parts[position2])
            
    
    def get_parts(self):
        parts = []
        for part in self.parts:
            parts.append(part[0])
        return parts
    
    def get_connections(self):
        connections = []
        for connection in self.structure.edges():
            connections.append([self.parts.index(connection[0]),
                               self.parts.index(connection[1])])
        return connections
    
    def get_connection_number(self, position):
        if position >= len(self):
            print("position out of the molecule bonds")
            return
        
        return nx.degree(self.structure)[self.parts[position]]
    
    def add_part(self, part, position):
        if position >= len(self):
            print("position out of the molecule bonds")
            return
        
        part += str(self.index)
        self.index += 1
        
        self.structure.add_node(part)
        self.update_parts()
        self.structure.add_edge(part, self.parts[position])
        
        
    def add_piece(self, piece, position1, position2):
        if position1 >= len(self) or position2 >= len(piece):
            print("position out of the molecule bonds")
            return
        
        size = len(self)
        parts = piece.get_parts()
        for i in range(len(parts)):
            parts[i] += str(self.index)
            self.index += 1
        
        self.structure.add_nodes_from(parts)
        self.update_parts()
        connections = piece.get_connections()
        for connection in connections:
            connection[0] = self.parts[connection[0] + size]
            connection[1] = self.parts[connection[1] + size]
            
        self.structure.add_edges_from(connections)
        self.add_connection(position1, position2 + size)
        
    def add_connection(self, position1, position2):
        if position1 >= len(self) or position2 >= len(self):
            print("position out of the molecule bonds")
            return
        
        if self.is_connected(position1, position2):
            print("parts are already connected")
            return
        
        self.structure.add_edge(self.parts[position1],
                                self.parts[position2])

    def del_connection(self, position1, position2):
        if position1 >= len(self) or position2 >= len(self):
            print("position out of the molecule bonds")
            return
        
        if not self.is_connected(position1, position2):
            print("parts are not connected")
            return
        
        self.structure.remove_edge(self.parts[position1],
                                   self.parts[position2])
        
        
    def find_team(self, part, n1 = None, n2 = None):
        parts = self.get_parts()
        pos = [i for i in range(len(parts)) if parts[i] == part]
        
        if n1 != None:
            remove = []
            for i in pos:
                has_con_n1 = [self.is_connected(i, j) for j in range(len(parts)) if parts[j] == n1]
                if not True in has_con_n1:
                    remove.append(i)
            for i in remove:
                pos.remove(i)
                    
        if n2 != None:
            remove = []
            for i in pos:
                has_con_n2 = [self.is_connected(i, j) for j in range(len(parts)) if parts[j] == n2]
                if not True in has_con_n2:
                    remove.append(i)
            for i in remove:
                pos.remove(i)
        
        if n1 == n2 and n1 != None:
            remove = []
            for i in pos:
                has_con_n1 = [self.is_connected(i, j) for j in range(len(parts)) if parts[j] == n1]
                if sum(has_con_n2) < 2:
                    remove.append(i)
            for i in remove:
                pos.remove(i)
            
        if len(pos) == 0:
            return None
        
        n = randint(0, len(pos) - 1)
        return pos[n]

molecules = []    
for i in range(1000):
    mol = Molecule()
    molecules.append(mol)
    mol.set_hex("A")
    
for i in range(999):
    molecules[999].add_piece(molecules[i], 0, 0)
    molecules[i] = molecules[999]
