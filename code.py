#Lara Foqaha 1220071 section 4      # Dana Taher 1221240 section 1

import math
import random
import time

MAX_ATTEMPTS = 500 # for SA initial solution (trying to get valid sol. up to 500 times)
INITIAL_TEMP = 1000
COOLING_RATE = 0.1
STOP_TEMP = 1
ITERATIONS_PER_TEMP = 100
POP_SIZE = 60
MUTATION_PROB = 0.09
GENERATIONS = 500
MAX_FITNESS_BASE = 100000 # for GA fitness function fitness = MAX - total distance 
PRIORITY_DISTANCE_TOLERANCE = 1.5  # accepting up to 1.5x worse distance for higher priority packages

# data structures
class Package:
    def __init__(self, x, y, weight, priority):
        self.x = x
        self.y = y
        self.weight = weight
        self.priority = priority

class Vehicle:
    def __init__(self, capacity):
        self.capacity = capacity
        self.packages = []  #  packages for each vehicle 
        self.route = []     # (x, y) route

def read_input_file(filename):
    packages = []
    vehicles = []
    with open(filename, 'r') as f:
        lines = f.readlines()

        for line in lines:
            parts = line.strip().split()
            if not parts:
                continue
            if parts[0] == 'vehicle':
                capacity = int(parts[1])
                vehicles.append(Vehicle(capacity))
            elif parts[0] == 'package':
                x = float(parts[1])
                y = float(parts[2])
                weight = float(parts[3])
                priority = int(parts[4])
                packages.append(Package(x, y, weight, priority))

    return vehicles, packages

def euclidean_distance(x1, y1, x2, y2):
    return math.sqrt(pow((x2 - x1), 2) + pow((y2 - y1), 2))

# function to compute the total distance for a route
def compute_route_distance(vehicle):
    base_distance = 0
    adjusted_distance = 0
    current_x = 0
    current_y = 0

    for p in vehicle.packages:
        dist = euclidean_distance(current_x, current_y, p.x, p.y)
        base_distance += dist

        # extra distance increases with the priority number and priority 1 stays the same
        extra_distance = 1.0 + (p.priority - 1) * 0.1  
        adjusted_distance += dist * extra_distance

        current_x = p.x
        current_y = p.y

    # returning to shop
    return_dist = euclidean_distance(current_x, current_y, 0, 0)
    base_distance += return_dist
    adjusted_distance += return_dist  

    # if extra distance makes it 1.5x worse then ignoring priority
    if adjusted_distance >= PRIORITY_DISTANCE_TOLERANCE * base_distance:
        return base_distance
    else:
        return adjusted_distance
 
 #################### SA #####################

 # initial solution for SA
def generate_initial_solution(vehicles, packages):

    for i in range(MAX_ATTEMPTS): # trying to find a valid random initial solution
        for v in vehicles:
            v.packages = []

        random.shuffle(packages) # randomly shuffling packages
        success = True

        for pkg in packages:
            random.shuffle(vehicles) 
            assigned = False

            for v in vehicles:
                total_weight = 0
                for p in v.packages:
                    total_weight += p.weight
                if total_weight + pkg.weight <= v.capacity:
                    v.packages.append(pkg)
                    assigned = True
                    break

            if not assigned:
                success = False
                break  # break and retry whole assignment

        if success:
            return  # exiting function successfully

    # if it reachs here all attempts failed
    print("Could not assign all packages within capacity limits.\n")
    exit(1) 

# making a copy of the current solution
def make_node(vehicles):
    new_vehicles = []
    for v in vehicles:
        new_v = Vehicle(v.capacity)
        new_v.packages = list(v.packages) # copying package objects
        new_vehicles.append(new_v)
    return new_vehicles

# computing the total cost (sum of route distances) fro all vehicles
def total_cost(vehicles):
    total =0
    for v in vehicles:
        distance = compute_route_distance(v)
        total += distance
    return total

# generating a neighbor by randomly swapping two packages between two vehicles if valid
def random_neighbor(vehicles):
    for k in range(100):  # trying up to 100 times to find a valid neighbor
        new_vehicles = make_node(vehicles)  # making a copy of the current solution

        v1 = random.choice(new_vehicles)
        v2 = random.choice(new_vehicles)
        while v2 == v1:  # making sure two different vehicles
            v2 = random.choice(new_vehicles)

        if not v1.packages or not v2.packages: 
            continue

        # choosing random package indexes
        i = random.randint(0, len(v1.packages) - 1)
        j = random.randint(0, len(v2.packages) - 1)

        p1 = v1.packages[i]
        p2 = v2.packages[j]

        # calculating new weights after swapping
        w1 = 0
        for p in v1.packages:
            w1 += p.weight #total weight before swapping
        w1 = w1 - p1.weight + p2.weight

        w2 = 0
        for p in v2.packages:
            w2 += p.weight
        w2 = w2 - p2.weight + p1.weight

        if w1 <= v1.capacity and w2 <= v2.capacity:
            v1.packages[i] = p2
            v2.packages[j] = p1
            return new_vehicles

    return make_node(vehicles)  # returning a clone if no valid swap found

# function same as book pseudo code
def simulated_annealing(vehicles):

    # initializing
    current = make_node(vehicles) # current <-- make node(initial state)
    current_cost = total_cost(current)
    t = 0
    while True:
        T = INITIAL_TEMP * (pow(COOLING_RATE, t))
        if T < STOP_TEMP: # if T = 0 return current
            break

        for i in range(ITERATIONS_PER_TEMP):
            next_state = random_neighbor(current) # next <-- randomly selected successor of current
            next_cost = total_cost(next_state)
            delta_E = current_cost - next_cost  # delta E <-- value[current] − value[next]

            if delta_E > 0:
                current = next_state # if delta E > 0 then current <-- next
                current_cost = next_cost
            else:
                probability = math.exp(delta_E / T)
                if random.random() < probability:
                    current = next_state # else current <-- next with probability e^(delta E /T)
                    current_cost = next_cost
        t += 1
    return current

####################3## GA ###########################

def fitness(chromosome):
    total = 0
    for v in chromosome:
        total += compute_route_distance(v)
    return MAX_FITNESS_BASE - total

def assign_packages_randomly(vehicles, packages):
    for v in vehicles:
        v.packages = []

    pkgs = list(packages)
    pkgs.sort(key=lambda p: p.priority)  # sorting by priority 

    for pkg in pkgs:
        random.shuffle(vehicles)
        assigned = False
        for v in vehicles:
            current_weight = 0
            for p in v.packages:
                current_weight += p.weight
            if current_weight + pkg.weight <= v.capacity:
                v.packages.append(pkg)
                assigned = True
                break
        if not assigned:
            return False
    return True

def generate_initial_population(vehicle_templates, packages): 
    population = [] # initial set of possible solutions
    for i in range(POP_SIZE):
        # copying vehicles with their capacities 
        vehicles = []
        for v in vehicle_templates:
            vehicles.append(Vehicle(v.capacity))

        success = assign_packages_randomly(vehicles, packages)
        if success:
            population.append(vehicles)

    if not population:
        print("Could not assign all packages within capacity limits.\n")
        exit(1)

    return population

def reproduce(parent1, parent2): #crossover
    n = len(parent1)
    all_packages = [] 

    # all packages from parent 1 and 2
    for i in range(n):
        for p in parent1[i].packages:
            all_packages.append(p)
        for p in parent2[i].packages:
            all_packages.append(p)

    # removing duplicates 
    unique_packages = []
    seen = set()
    for p in all_packages:
        key = (p.x, p.y, p.weight, p.priority)
        if key not in seen:
            unique_packages.append(p)
            seen.add(key)

    unique_packages.sort(key=lambda pkg: pkg.priority)

    # creating child vehicles with same capacities
    child = []
    for v in parent1:
        child.append(Vehicle(v.capacity))

    for pkg in unique_packages:
        assigned = False
        for v in child:
            total_weight = sum(p.weight for p in v.packages)
            if total_weight + pkg.weight <= v.capacity:
                v.packages.append(pkg)
                assigned = True
                break
        if not assigned:
            return random.choice([parent1, parent2])

    return child

# randomly swapping packages between two vehivles of the solution
def mutate(chromosome):
    v1, v2 = random.sample(chromosome, 2)
    if not v1.packages or not v2.packages:
        return

    i = random.randint(0, len(v1.packages) - 1)
    j = random.randint(0, len(v2.packages) - 1)
    p1 = v1.packages[i]
    p2 = v2.packages[j]

    # calculating new weights
    w1 = 0
    for p in v1.packages:
        w1 += p.weight
    w1 = w1 - p1.weight + p2.weight
    
    w2 = 0
    for p in v2.packages:
        w2 += p.weight
    w2 = w2 - p2.weight + p1.weight

    if (w1 <= v1.capacity) and (w2 <= v2.capacity):
        v1.packages[i] = p2
        v2.packages[j] = p1

# random_selection = WEIGHTED-RANDOM-CHOICES(population, weights, 2) in pseudo code
#choose two random parent solutions to crossover
def random_selection(population, weights):
        return random.choices(population, weights=weights, k=2)

# function same as book pseudo code
def genetic_algorithm(population, fitness_fn):

    best = max(population, key=fitness_fn)

    for i in range(GENERATIONS): # generations = 500
        weights = []
        for individual in population: # weights <-- WEIGHTED-BY(population, fitness)
            value = fitness_fn(individual)
            weights.append(value)

        population2 = [] # population2 <-- empty list

        for j in range(len(population)):
            parent1, parent2 = random_selection(population, weights) # parent1,parent2 <-- WEIGHTED-RANDOM-CHOICE(population, weights, 2)
            child = reproduce(parent1, parent2) # child <-- REPRODUCE(parent1, parent2)

            if random.random() < MUTATION_PROB: # if small random probability
                mutate(child) # then child <-- MUTATE(child)

            population2.append(child) # adding child to population2

        # updating best solution
        possible_solution = max(population2, key=fitness_fn)
        if fitness_fn(possible_solution) > fitness_fn(best):
            best = possible_solution

        population = population2  # population <-- population2

    return best #return best individual in population

##############################################

def print_initial_solution(vehicles):
    print("\n*** INITIAL RANDOM SOLUTION ***\n")
    total_distance = 0

    for i, v in enumerate(vehicles):
        print(f"Vehicle {i+1}: Capacity = {v.capacity}")
        print("Route: Shop (0,0)", end="")

        load = 0
        for p in v.packages:
            print(f" --> Package ({p.x}, {p.y}), Priority: ({p.priority})", end="")
            load += p.weight

        print(" --> Shop(0,0)")
        print(f"Total weight = {load}")

        dist = compute_route_distance(v)
        total_distance += dist
        print(f"Route Distance: {dist:.2f} km")
        print("---------------------------")

    print(f"\nInitial total distance travelled: {total_distance:.6f} Km\n")
    print("___________________________________________________")

def print_optimized_solution(vehicles):
    print("\n*** FINAL OPTIMIZED SOLUTION ***\n")
    total_distance = 0

    for i, v in enumerate(vehicles):
        print(f"Vehicle {i+1}: Capacity = {v.capacity}")
        print("Route: Shop (0,0)", end="")

        load = 0
        for p in v.packages:
            print(f" --> Package ({p.x}, {p.y}), Priority: ({p.priority})", end="")
            load += p.weight

        print(" --> Shop (0,0)")
        print(f"Total weight = {load}")

        dist = compute_route_distance(v)
        total_distance += dist
        print(f"Route distance: {dist:.2f} km")
        print("---------------------------")

    print(f"Total distance travelled: {total_distance:.6f} Km\n")

#####################################################################
print("Enter the name of the input file: ")
filename = input().strip()

try:
    vehicles, packages = read_input_file(filename)
except FileNotFoundError:
    print(f"\nFile '{filename}' does not exist.\n")
    print("Enter the name of the input file: ")
    filename = input().strip()
    vehicles, packages = read_input_file(filename)

print("Read", len(packages), "packages and", len(vehicles), "vehicles")

########## menu ##############
while True:
    print("\nPlease choose one of the following:")
    print("1- Simulated Annealing")
    print("2- Genetic Algorithm")
    print("3- Quit")
    choice = input()

    if choice == '1':
        generate_initial_solution(vehicles, packages)
        print_initial_solution(vehicles)
        start_time = time.time()
        optimized = simulated_annealing(vehicles)
        end_time = time.time()
        print_optimized_solution(optimized)
        total_time = end_time - start_time
        print(f"Simulated Annealing Time: {total_time:.4f} seconds")

    elif choice == '2':
        population = generate_initial_population(vehicles, packages)
        print_initial_solution(population[0])
        start_time = time.time()
        best = genetic_algorithm(population, fitness)
        end_time = time.time()
        print_optimized_solution(best)
        total_time = end_time - start_time
        print(f"Genetic Algorithm Time: {total_time:.4f} seconds")

    elif choice == '3':
        print("\nExiting...")
        break

    else:
        print("\nInvalid choice. Please choose 1,2 or 3\n")