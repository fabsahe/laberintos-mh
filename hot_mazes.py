import sys
import random
from math import e

# Laberintos def
SOLUTION_FOUND = 0x1
SOLUTION_NOT_FOUND = 0x2

class maze_t:
    '''Estructura de datos para manejar la informacion del laberinto'''
    def __init__(self, data, r1, c1, r2, c2):
        '''Inicializar laberinto'''
        self.r = len(data)
        self.c = len(data[0])
        self.data = data
        self.startstate = (r1, c1)
        self.goalstate = (r2, c2)

    def __str__(self):
        '''da la representacion numerica del laberinto '''
        s = ""
        for i in self.data:
            s += str(i)
            s += "\n"
        return s 

    def nextstate(self, currentstate):
        '''da los siguientes estados del laberinto'''
        if currentstate != self.startstate and self.data[currentstate[0] - 1][currentstate[1]] == 1:
            yield (currentstate[0] - 1, currentstate[1])
        if self.data[currentstate[0]][currentstate[1] + 1] == 1:
            yield (currentstate[0], currentstate[1] + 1)
        if currentstate != self.goalstate and self.data[currentstate[0] + 1][currentstate[1]] == 1:
            yield (currentstate[0] + 1, currentstate[1])
        if self.data[currentstate[0]][currentstate[1] - 1] == 1:
            yield (currentstate[0], currentstate[1] - 1)
    
    def value(self, state):
        '''funcion heuristica
        regresa el valor h(n) de un estado'''
        return abs(self.goalstate[0] - state[0]) + abs(self.goalstate[1] - state[1])

    def is_better(self, s1, s2):
        '''funcion que dice si el estado s1 es mejor que el estado s2'''
        val1 = self.value(s1)
        val2 = self.value(s2)
        if val1 == val2:
            return s1[0] > s2[0]
        return bool(val1 < val2)

def get_pos(data, val):
    '''regresa la posicion de un estado y el numero de apariciones'''
    r = len(data)
    c = len(data[0])
    r_pos = -1
    c_pos = -1
    cont = 0
    for i in range(r):
        for j in range(c):
            if data[i][j] == val:
                cont = cont + 1
                r_pos = i
                c_pos = j
    return cont, r_pos, c_pos

def get_maze(filename):
    '''regresa un objeto laberinto a partir de un archivo'''
    try:
        f = open(filename, "r+")
        l = f.readlines()
        l = [i[:-1] for i in l]

        if len(set(len(i) for i in l)) != 1:
            raise Exception
        for i in l:
            s = set(i)
            if not s.issubset({'S', 'E', 'X', ' ', chr(9608)}):
                raise Exception

        data = [[1 if i == ' ' else 0 for i in j] for j in l]

        data_ori = [[i for i in j] for j in l]
        nst, r1, c1 = get_pos(data_ori, 'S')
        ned, r2, c2 = get_pos(data_ori, 'E')

        if nst == 1 and ned == 1:
            data[r1][c1] = 1
            data[r2][c2] = 1
            return maze_t(data,r1,c1,r2,c2)
        raise Exception
    except Exception:
        pass
    finally:
        try:
            f.close()
        except:
            pass
    return None

def direction(prev, cur):
    '''devuelve la direccion de un estado respecto a su estado anterior'''
    if cur[0] > prev[0]:
        return "abajo"
    if cur[0] < prev[0]:
        return "arriba"
    if cur[1] > prev[1]:
        return "derecha"
    if cur[1] < prev[1]:
        return "izquierda"
    return "inicio"


# recocido simulado
name = "simulated annealing"

delta_E = lambda E1, E2: E1 - E2

def probability(dE, T):
    k = 1e-2
    exp = - (dE / (k * T))
    return e ** exp

def simulated_annealing(maze):
    currentstate = maze.startstate
    goalstate = maze.goalstate

    path = [currentstate]
    testpath = []
    T = 200
    prev = None
    while currentstate != goalstate:
        found = False
        E1 = maze.value(currentstate)
        P = True
        for state in maze.nextstate(currentstate):
            if P:
                P = False
            if state == prev:
                continue
            E2 = maze.value(state)
            if state == goalstate:
                path.append(state)
                return path, SOLUTION_FOUND
            if maze.is_better(state, currentstate):
                path.extend(testpath)
                path.append(state)
                testpath = []
                prev = currentstate
                currentstate = state
                found = True
                break
            else:
                p = probability(delta_E(E2, E1), T)
                if p < random.random():
                    found = True
                    testpath.append(state)
                    prev = currentstate
                    currentstate = state
                    break
        if not found:
            return path, SOLUTION_NOT_FOUND
        T = 0.9 * T
    return path, SOLUTION_FOUND


if __name__ == '__main__':

    maze = get_maze('a.maze')

    if not maze:
        print('ERROR: el archivo del laberinto no es correcto', file = sys.stderr)
        sys.exit()

    result = SOLUTION_NOT_FOUND
    while result == SOLUTION_NOT_FOUND:
        path, result = simulated_annealing(maze)

    resolvedpath = []
    a = resolvedpath.append
    if result == SOLUTION_FOUND:
        print("Ruta encontrada")
        prev = path[0]
        for item in path:
            a(direction(prev, item))
            prev = item
        a("salida")
    elif result == SOLUTION_NOT_FOUND:
        print("Ruta no encontrada")
        print("Se puede llegar hasta:")
        prev = path[0]
        for item in path:
            a(direction(prev, item))
            prev = item
        a("salida")

    print(", ".join(resolvedpath))
