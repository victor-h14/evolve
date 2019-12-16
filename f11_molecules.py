# reboot

import networkx as nx
import matplotlib.pyplot as plt
import threading
from random import randint, shuffle

###############################################################################

class Life():
    def __init__(self):
        self.machines = None

###############################################################################

class Machine():
    def __init__(self, code):
        self.code = code.split(".")        
        self.synthesis_cost = len(code)
        self.action_index = 0

        #code manual LETTER:ARG1,ARG2,...,ARGN
        #catch - C - index, team
        #release - R - index
        #give - G - index, machine
        #unlink - U - index, team (size 2 or 3)
        #link - L - index, team1, team2
        #join - J - index1, team1, index2, team2
        #transform - T - index, team, part

        self.actions = []        
        catch_index = 0
        for step in code.split("."):
            if step[0] == "C":
                catch = step.split(":")[1]
                action = "self.catch(" + str(catch_index) + ", '" + catch + "')"
                catch_index += 1
                self.actions.append(action)
            elif step[0] == "R" and catch_index != 0:
                action = "self.release(" + str(catch_index - 1) + ")"
                self.actions.append(action)
            elif step[0] == "G" and catch_index != 0:
                give = step.split(":")[1]
                give = give.split(",")
                action = "self.give(" + give[0] + ", " + give[1] + ")"
                self.actions.append(action)
            elif step[0] == "U" and catch_index != 0:
                unlink = step.split(":")[1]
                action = "self.unlink(" + str(catch_index - 1) + ", '" + unlink + "')"
                self.actions.append(action)
            elif step[0] == "L" and catch_index != 0:
                link = step.split(":")[1]
                link = link.split(",")
                action = "self.link(" + str(catch_index - 1) + ", '" + link[0] + "', '" + link[1] + "')"
                self.actions.append(action)
            elif step[0] == "J" and catch_index > 1:
                join = step.split(":")[1]
                join = join.split(",")
                action = "self.join(" + str(catch_index - 1) + ", '" + join[0] + "', " + str(catch_index - 2) + ", '" + join[1] + "')"
                self.actions.append(action)
            elif step[0] == "T" and catch_index != 0:
                transform = step.split(":")[1]
                transform = transform.split(",")
                action = "self.transform(" + str(catch_index - 1) + ", '" + transform[0] + "', '" + transform[1] + "')"
                self.actions.append(action)
            
        self.attachment = [None for i in range(catch_index)]
        
    def act(self):
        print(self.actions[self.action_index])
        eval(self.actions[self.action_index])
        self.action_index = (self.action_index + 1) % len(self.actions)
    
    def catch(self, index, team):
        if self.attachment[index] != None:
            return
        
        i = randint(0, len(molecules) - 1)
        team = [i for i in team]
        
        if molecules[i].attached == True:
            return
        
        if molecules[i].find_team(team) != None:
            self.attachment[index] = molecules[i]
            self.attachment[index].attached = True
            print("energy consumed")
    
    def release(self, index):
        if self.attachment[index] == None:
            return
        self.attachment[index].attached = False
        self.attachment[index] = None
        print("energy consumed")
    
    def give(self):
        pass
    
    def unlink(self, index, team):
        if self.attachment[index] == None:
            return
        
        team = [i for i in team]
        pos = self.attachment[index].find_team(team) 
        if pos == None:
            return
        
        if len(pos) == 3:
            del pos[randint(1,2)]
        
        value = self.attachment[index].del_connection(pos[0], pos[1])        
        if value == None:
            self.attachment[index] = None
        elif value: 
            print("energy consumed")
        
    def link(self, index, team1, team2):
        if self.attachment[index] == None:
            return
        
        team1 = [i for i in team1]
        pos1 = self.attachment[index].find_team(team1) 
        
        team2 = [i for i in team2]
        pos2 = self.attachment[index].find_team(team2) 
        
        if pos1 == None or pos2 == None:
            return
        
        if self.attachment[index].add_connection(pos1[0], pos2[0]):        
            print("energy consumed")
    
    def join(self, index1, team1, index2, team2):
        if self.attachment[index1] == None or self.attachment[index1] == None:
            return
        
        if self.attachment[index1] == self.attachment[index2]:
            return
        
        team1 = [i for i in team1]
        pos1 = self.attachment[index1].find_team(team1) 
        
        team2 = [i for i in team2]
        pos2 = self.attachment[index2].find_team(team2) 
        
        if pos1 == None or pos2 == None:
            return
        
        if self.attachment[index1].merge(self.attachment[index2], pos1[0], pos2[0]):
            molecules.remove(self.attachment[index2])
            self.attachment[index2] = self.attachment[index1]
            print("energy consumed")
            self.attachment[index2].plot_structure()
    
    def transform(self, index, team, part):
        if self.attachment[index] == None:
            return
        
        team = [i for i in team]
        pos = self.attachment[index].find_team(team) 
        
        if pos == None:
            return
        if pos[0] == part:
            return
        
        if self.attachment[index].transform_part(pos[0], part):
            print("energy consumed")

###############################################################################  

class Molecule():
    def __init__(self, molecule_index):
        self.structure = nx.Graph()
        self.molecule_index = molecule_index
        self.index = 0
        self.attached = False
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
    
    def __eq__(self, other):
        if type(other) == Molecule:
            return self.molecule_index == other.molecule_index
        return False
    
    def update_parts(self):
        self.parts = list(self.structure.nodes())
    
    def set_hex(self, style):
        parts = [style + str(i) for i in range(6)]
        self.structure.add_nodes_from(parts)
        
        for i in range(5):
            self.structure.add_edge(parts[i], parts[i+1])
        self.structure.add_edge(parts[0], parts[5])
        self.update_parts()
        self.index = 6
    
    def set_structure(self, structure):
        self.structure = structure
        self.index = len(list(self.structure.nodes()))
        self.update_parts()
    
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
            return False      
        return nx.degree(self.structure)[self.parts[position]]
    
    def add_part(self, part, position):
        if position >= len(self):
            print("position out of the molecule bonds")
            return False
        
        part += str(self.index)
        self.index += 1
        
        self.structure.add_node(part)
        self.update_parts()
        self.structure.add_edge(part, self.parts[position])
        return True
        
    def add_connection(self, position1, position2):
        if position1 >= len(self) or position2 >= len(self):
            print("position out of the molecule bonds")
            return False
        
        if self.is_connected(position1, position2) or position1 == position2:
            print("parts are already connected")
            return False
        
        self.structure.add_edge(self.parts[position1],
                                self.parts[position2])
        return True

    def del_connection(self, position1, position2):
        if position1 >= len(self) or position2 >= len(self):
            print("position out of the molecule bonds")
            return False
        
        if not self.is_connected(position1, position2):
            print("parts are not connected")
            return False
        
        self.structure.remove_edge(self.parts[position1],
                                   self.parts[position2])
        
        if not nx.is_connected(self.structure):
            nodes_set = list(nx.connected_components(self.structure))
            molecules.remove(self)
            for nodes in nodes_set:
                i_molecules[0] += 1
                molecule = Molecule(i_molecules[0])
                molecule.set_structure(nx.Graph(nx.subgraph(self.structure, nodes)))
                molecules.append(molecule)
            return None
        return True
    
    def del_part(self, position):
        if position >= len(self):
            print("position out of the molecule bonds")
            return False
                
        self.structure.remove_node(self.parts[position])
        self.update_parts()
        return True
    
    def transform_part(self, position, part):
        if position >= len(self):
            print("position out of the molecule bonds")
            return False
        
        connections = [con for con in self.get_connections() if position in con]
        self.del_part(position)
        
        part += str(self.index)
        self.index += 1
        self.structure.add_node(part)
        self.update_parts()
        
        for con in connections:
            if con[0] == position:
                position = con[1]
            else:
                position = con[0]
            self.add_connection(len(self) - 1, position)
        return True
        
    def merge(self, molecule, position1, position2):
        if position1 >= len(self) or position2 >= len(molecule):
            print("position out of the molecule bonds")
            return False
        
        size = len(self)
        parts = molecule.get_parts()
        for i in range(len(parts)):
            parts[i] += str(self.index)
            self.index += 1
        
        self.structure.add_nodes_from(parts)
        self.update_parts()
        connections = molecule.get_connections()
        for connection in connections:
            connection[0] = self.parts[connection[0] + size]
            connection[1] = self.parts[connection[1] + size]
            
        self.structure.add_edges_from(connections)
        self.add_connection(position1, position2 + size)
        return True
    
    def plot_structure(self):
        nx.draw(self.structure)
        plt.show()
    
    def find_team(self, team):
        parts = self.get_parts()
        pos = [i for i in range(len(parts)) if parts[i] == team[0]]
        shuffle(pos)
        
        if len(pos) == 0:
            return None        
        if len(team) == 1:
            return [pos[0]]
        elif len(team) == 2:
            pos_n1 = [i for i in range(len(parts)) if parts[i] == team[1]]
            shuffle(pos_n1)
            
            for p in pos:
                for n1 in pos_n1:
                    if len(nx.shortest_path(self.structure, 
                                            self.parts[p],
                                            self.parts[n1])) == 2:
                        return [p, n1]
        elif len(team) == 3:
            pos_n1 = [i for i in range(len(parts)) if parts[i] == team[1]]
            shuffle(pos_n1)
            pos_n2 = [i for i in range(len(parts)) if parts[i] == team[2]]
            shuffle(pos_n2)
            for p in pos:
                for n1 in pos_n1:
                    for n2 in pos_n2:
                        if len(nx.shortest_path(self.structure, self.parts[p], self.parts[n1])) == 2 and len(nx.shortest_path(self.structure, self.parts[p], self.parts[n2])) == 2 and len(nx.shortest_path(self.structure, self.parts[n1], self.parts[n2])) == 3:
                            return [p, n1, n2]
        return None

###############################################################################

class StopWatch():
    def __init__(self, time, function):
        self.time = time
        self.function = function
        self.thread = threading.Timer(self.time, self.update)
    
    def update(self):
        self.function()
        self.thread = threading.Timer(self.time, self.update)
        self.thread.start()
    
    def start(self):
        self.thread.start()
    
    def cancel(self):
        self.thread.cancel()

###############################################################################

def create_world(n_molecules):
    for i in range(n_molecules):
        mol = Molecule(i)
        molecules.append(mol)
        mol.set_hex("A")

def update():
    m.act()

molecules = []
i_molecules = [100]
create_world(i_molecules[0])
#m = Machine("C:A.C:A.J:AAA,AAA.R")
m = Machine("C:A.U:AA.R")

timer = StopWatch(1, update)
timer.start()
