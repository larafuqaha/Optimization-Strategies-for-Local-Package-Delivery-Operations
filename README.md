# Optimization Strategies for Local Package Delivery Operations

A Python implementation of two metaheuristic optimization algorithms — **Simulated Annealing (SA)** and **Genetic Algorithm (GA)** — applied to a constrained vehicle routing and package assignment problem.

**Course:** Artificial Intelligence — ENCS3340  
**Institution:** Birzeit University, Department of Electrical and Computer Engineering  

---

## Problem Overview

Given a set of delivery vehicles (each with a weight capacity) and a set of packages (each with a destination, weight, and priority), the goal is to:

- Assign every package to a vehicle without exceeding its capacity
- Determine the delivery order for each vehicle to minimize total travel distance
- Favor higher-priority packages in routing decisions

All vehicles start and end their routes at the shop, located at coordinates `(0, 0)`.

---

## Algorithms

### Simulated Annealing

The solution is represented as a set of per-vehicle package lists. Starting from a random valid assignment, the algorithm iteratively generates neighbors by swapping packages between vehicles and accepts worse solutions with a probability based on the current temperature.

Key parameters:
- `INITIAL_TEMP = 1000`
- `COOLING_RATE = 0.95` — tuned from 0.75 (faster but worse solutions) to 0.95 (slower, more consistent)
- `STOP_TEMP = 1`
- `ITERATIONS_PER_TEMP = 100`

### Genetic Algorithm

Solutions are encoded as chromosomes — lists of vehicle objects with assigned packages. Each generation produces new children via crossover (merging packages from two parents, deduplicating, and reassigning by priority) and random mutation (swapping packages between vehicles when capacity allows).

Key parameters:
- `POP_SIZE = 60`
- `GENERATIONS = 500`
- `MUTATION_PROB = 0.09` — tuned across 0.01, 0.05, and 0.1; 0.1 gave the most consistent results

---

## Priority Handling

Route distance includes a priority-based penalty:

```
adjusted_distance = distance × (1.0 + 0.1 × (priority - 1))
```

If the adjusted distance exceeds `1.5×` the base distance, the penalty is dropped and the base distance is used instead. This avoids penalizing high-priority packages at the cost of unreasonably long routes.

---

## Input Format

The program reads from a plain text file. Each line is either a `vehicle` or `package` entry:

```
vehicle <capacity>
package <x> <y> <weight> <priority>
```

Example (`input.txt`):
```
vehicle 100
vehicle 100

package 10 12 30 2
package 5 7 25 1
package 8 9 10 3
```

---

## Running the Program

```bash
python code.py
```

The program prompts for the input filename, then presents a menu:

```
Please choose one of the following:
1- Simulated Annealing
2- Genetic Algorithm
3- Quit
```

---

## Output

For each algorithm, the program prints:

- **Initial random solution** — routes, weights, and distances per vehicle
- **Optimized solution** — same format after running the algorithm
- **Total distance** in kilometers
- **Execution time** in seconds

Example output format:
```
Vehicle 1: Capacity = 100
Route: Shop (0,0) --> Package (5.0, 7.0), Priority: (1) --> Package (12.0, 6.0), Priority: (1) --> Shop (0,0)
Total weight = 55.0
Route distance: 46.39 km
```

---

## Constraint Handling

Capacity constraints are enforced throughout:

- During initial solution generation, the algorithm retries up to `MAX_ATTEMPTS = 500` times to find a valid assignment
- In SA neighbor generation, swaps are only accepted if neither vehicle exceeds capacity after the swap
- In GA crossover and mutation, weight checks are performed before any assignment

If no valid solution can be constructed, the program exits with an error message.

---

## Test Cases

| Case | Description | Result |
|------|-------------|--------|
| Basic Feasibility | 4 packages, 2 vehicles (100 kg each) | All packages assigned, capacity respected |
| Overcapacity Package | 1 package (150 kg) exceeding all vehicles | Program exits with clear error message |
| Distance Optimization | 6 packages, 2 vehicles | GA reduced total distance from 77.55 km to 53.59 km |
| SA vs. GA Comparison | 10 packages, 3 vehicles | GA found shorter distance; SA was significantly faster |

---

## Files

| File | Description |
|------|-------------|
| `code.py` | Main source code |
| `input.txt` | Sample input file (10 vehicles, 40 packages) |
| `report.pdf` | Project report |

---
