import copy
from random import shuffle,randint

file_name = '20x20.txt'

data, N1,N,M = 0, 0, 0,0
def read_file(file_name):
    global N
    global M 
    global data
    global N1
    file = open(file_name,'r')
    N, M = list(map(int,file.readline().split()))
    data = []
    N1 = 0
    for i in range(N):
        string = [0] * M
        vehicle = list(map(int,file.readline().split()))
        for s in vehicle[1:]:
            string[int(s)-1] = 1
            N1+=1
        data.append(string)

class Cluster(object):
    def __init__(self, vehicles=[], details=[]):
        self._vehicles: list = vehicles
        self._details: list = details
        result = self.get_matrix()
        self.N1_in: int = result[1]
        self.N0_in: int = result[2]
        self.matrix = result[0]
    def __repr__(self):
        s=""
        for m in self.matrix:
            s+= str(m).replace(","," ")[1:-1] +'\n'
        return f"\nCustomer {self._vehicles, self._details, self.N1_in, self.N0_in} \n{s[:-1]}"
    
    def get_matrix(self):
        mat = []
        for v in self._vehicles:
            line = []
            for d in self._details:
                line.append(data[v][d])
            mat.append(line)
            N1_in = sum([sum(m) for m in mat])
            N0_in = len(self._vehicles)*len(self._details) - N1_in
        return mat, N1_in, N0_in
    
    def delete_vehicle(self,number):
        i = self._vehicles.index(number)
        n1 = sum(self.matrix[i][:])
        n0 = len(self._details) - n1
        self.N1_in -= n1
        self.N0_in -= n0
        self.matrix = self.matrix[:i] + self.matrix[i+1:] 
        self._vehicles.pop(i)
    
    def add_vehicle(self,number):
        line = []
        for d in self._details:
            line.append(data[number][d])
        n1 = sum(line)
        n0 = len(self._details) - n1
        self.N1_in += n1
        self.N0_in += n0
        self.matrix.append(line)
        self._vehicles.append(number)
        
    def delete_detail(self,number):
        i = self._details.index(number)
        n1 = sum(r[i] for r in self.matrix)
        n0 = len(self._vehicles) - n1
        self.N1_in -= n1
        self.N0_in -= n0
        [r.pop(i) for r in self.matrix]
        self._details.pop(i)
    
    def add_detail(self,number):
        line = []
        for v in self._vehicles:
            line.append(data[v][number])
        n1 = sum(line)
        n0 = len(self._vehicles) - n1
        self.N1_in += n1
        self.N0_in += n0
        [r.append(line.pop(0)) for r in self.matrix]
        self._details.append(number)

def initial_solution(k=2): 
    best_sum = 0
    K = min(N,M) // k 
    for _ in range(20):
        shuffled_vehicle = list(range(N))
        shuffled_details = list(range(M))
        shuffle(shuffled_vehicle)
        shuffle(shuffled_details)
        solution = []
        for _ in range(K):
            veh, det, i = [], [], 0
            while (i< N//K) and (len(shuffled_vehicle)>1):
                veh.append(shuffled_vehicle.pop(0))
                i+=1
            i=0
            while (i< M//K) and (len(shuffled_details)>1):
                det.append(shuffled_details.pop(0))
                i+=1
            if (len(veh)>0) and (len(det)>0):
                solution.append(Cluster(veh, det))
        solution.append(Cluster(shuffled_vehicle, shuffled_details))
        cur_sum = object_function(solution)
        if (cur_sum > best_sum):
            best_solution = solution
            best_sum = cur_sum
    return best_solution

def is_feasible(solution): #проверка на то, что решение существует
    res = get_output(solution)
    veh = set(res[0])
    det = set(res[1])
    if (len(veh - det)==0) and (len(det - veh)==0):
        return True
    else:
        return veh, det

def object_function(solution):
    n1 = sum(c.N1_in for c in solution)
    n0 = sum(c.N0_in for c in solution)
    return n1 / (N1 + n0)

def get_output(solution, k=0): #преобразование решения в итоговый вариант
    vehicle = ['_'] * N
    details = ['_'] * M
    for i in range(len(solution)):
        for v in solution[i]._vehicles:
            vehicle[v] = i+k
        for d in solution[i]._details:
            details[d] = i+k
    return vehicle, details

def exchange_vehicle(solution): 
    #функция для LS, позволяющая переместить строку в другой класс (перебирает все строки всех классов)
    best_sum = object_function(solution)
    best_sol = copy.deepcopy(solution)
    for cluster in solution:
        first_cluster = copy.deepcopy(cluster)
        if len(cluster._vehicles)>1:
            for vehicle in cluster._vehicles:
                for c in solution:
                    if (c._vehicles == cluster._vehicles) :
                        continue
                    second_cluster = copy.deepcopy(c)
                    c.add_vehicle(vehicle)
                    cluster.delete_vehicle(vehicle)
                    cur_sum = object_function(solution)
                    if (cur_sum > best_sum):
                        best_sol = copy.deepcopy(solution)
                        best_sum = copy.deepcopy(cur_sum)
                    cluster.add_vehicle(vehicle)
                    c.delete_vehicle(vehicle) 
    solution = (best_sol)
    return copy.deepcopy(solution), best_sum

def exchange_detail(solution):
    #функция для LS, позволяющая переместить столбец в другой класс (перебирает все строки всех классов)
    best_sum = object_function(solution)
    best_sol = copy.deepcopy(solution)
    for cluster in solution:
        first_cluster = copy.deepcopy(cluster)
        if len(cluster._details)>1:
            for detail in cluster._details:
                for c in solution:
                    if (c._vehicles == cluster._vehicles) :
                        continue
                    second_cluster = copy.deepcopy(c)
                    c.add_detail(detail)
                    cluster.delete_detail(detail)
                    cur_sum = object_function(solution)
                    if (cur_sum > best_sum):
                        best_sol = copy.deepcopy(solution)
                        best_sum = copy.deepcopy(cur_sum)
                    cluster.add_detail(detail)
                    c.delete_detail(detail) 
    solution = (best_sol)
    return copy.deepcopy(solution), best_sum

def local_search(solution, vnd):#local search, улучшающий решение
    if vnd == 0:
        vnd = [exchange_vehicle, exchange_detail]
    else:
        vnd = [exchange_detail, exchange_vehicle]
    best_sum = object_function(solution)
#     print("INITIAL ", best_sum)
    old_sum = 0
    step = 0
    while(True):
        while best_sum - old_sum > 0.0001 :
            old_sum = copy.deepcopy(best_sum)
            step += 1
            solution, best_sum = vnd[0](solution)
        old_sum = copy.deepcopy(best_sum)
        solution, best_sum = vnd[1](solution)
        if best_sum - old_sum > 0.0001 :
            continue
        else:
#             print("END AT :{}".format(best_sum))
            break
    return copy.deepcopy(solution), best_sum    

def merge_clusters(cl1,cl2):
    return Cluster(cl1._vehicles + cl2._vehicles, cl1._details + cl2._details)

def split_cluster(cl):
    #предполагаем, что кластер разбивается на два равных по длине кластера
    shuffle(cl._vehicles)
    shuffle(cl._details)
    veh_len = len(cl._vehicles) // 2
    det_len = len(cl._details) // 2
    c1 = Cluster(cl._vehicles[:veh_len], cl._details[:det_len])
    c2 = Cluster(cl._vehicles[veh_len:], cl._details[det_len:])
    return c1,c2
def nice_view(sol,name): #функция для записи ответа в файл
    file = open(name, 'w+')
    res = get_output(sol)
    file.write(str(res[0])[1:-1].replace(', ', ' ') + "\n")
    file.write(str(res[1])[1:-1].replace(', ', ' ') + "\n")
    print(res[0])
    print(res[1])
    file.close()
    total_file = open('VNS_total.txt', 'a+')
    total_file.write(name[:-4] + ' ' + str(object_function(solution))+ "\n")
    print(name[:-4] + ' ' + str(sum([s.object_function() for s in sol]))+ "\n")
    total_file.close()

def merge1(solution, n_shaking_merge):
    if n_shaking_merge == 0:
        return solution
    best_sol = []
    best_sum = -1
    for _ in range(n_shaking_merge):
        temp_sol = copy.deepcopy(solution)
        if len(solution)>1: #слить 2 кластера можно только если их как минимум 2 в решении
            i = randint(0, len(solution)-2)
            j = randint(i+1, len(solution)-1)
            cl = merge_clusters(temp_sol.pop(i), temp_sol.pop(j-1))
            temp_sol.append(cl)
            if object_function(temp_sol) > best_sum:
                best_sol = copy.deepcopy(temp_sol)
                best_sum = object_function(temp_sol)
    return best_sol

def split1(solution, n_shaking_split):
    if n_shaking_split == 0:
        return solution
    best_sol = []
    best_sum = -1
    for _ in range(n_shaking_split):
        temp_sol = copy.deepcopy(solution)
        i = randint(0, len(solution)-1)
        k = 0
        while (len(solution[i]._vehicles)<2 or len(solution[i]._details)<2): 
            #разбить кластер можно только если в нем больше 2 строк и 2 столбцов
            i = randint(0, len(solution)-1)
            k +=1
            if k > len(solution):
                break
        else:
            cls = split_cluster(temp_sol.pop(i))
            temp_sol += cls
            if object_function(temp_sol) > best_sum:
                best_sol = copy.deepcopy(temp_sol)
                best_sum = object_function(temp_sol)
    return best_sol


#MAIN FUNCTION
#вся магия здесь
def main(elem_in_cluster, repeat, vnd, shaking, n_shaking, n_best_sh):
    read_file(file_name)
    if shaking == 0:
        shaking = [merge1, split1, n_best_sh]
    else:
        shaking = [split1, merge1, n_best_sh]
    BS = 0
    BSOL = []
    for _ in range(repeat):
        solution = initial_solution(elem_in_cluster)
        solution, best_sum = copy.deepcopy(local_search(solution, vnd))  
        best_sol = copy.deepcopy(solution)
        for sh_oper in range(2):
            shaking_counter = 0
            while shaking_counter < n_shaking:
                solution = copy.deepcopy(best_sol)
                solution = copy.deepcopy(shaking[sh_oper](solution, shaking[-1]))
                solution, cur_sum = copy.deepcopy(local_search(solution, vnd))  
                if cur_sum > best_sum:
#                     print("Improved in ", shaking[sh_oper].__name__, " to ", cur_sum, ' at ', shaking_counter)
                    shaking_counter = 0
                    best_sum = copy.deepcopy(cur_sum)
                    best_sol = copy.deepcopy(solution)
                else:
                    shaking_counter += 1
#         print(best_sum)           
        if best_sum > BS:
            BS = best_sum
            BSOL = best_sol
    return BSOL, BS
