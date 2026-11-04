# TSP LNS solver

Solver for the Travelling Salesman Problem using Large Neighborhood Search (LNS) with simulated annealing acceptance. Written offline, without any AI tools or even internet connection, only using study materials. Design decisions were written down before coding, including the first takes and why they changed: [BEFORE_CODING.md](BEFORE_CODING.md).

## How it works

- Initial solution: greedy nearest neighbor from a random start city.
- Destroy: two operators. Random removal (k random cities) for diversity, radial removal (random city and its nearest neighbors) to rebuild a whole region. The size k is drawn randomly from an interval every iteration.
- Repair: removed cities go back one by one in random order, each to the position with the cheapest insertion cost.
- Acceptance: simulated annealing with the Metropolis criterion, a worse route is accepted with probability `exp(-delta/T)`. Temperature is relative to the initial route cost and cools down exponentially with elapsed time.
- Best route is stored separately and written to the output during the run, so there is always a valid answer, even if the process gets stopped.
- Feasibility: the solver works only with permutations, every route is checked before writing.
- Time limit is measured from the process start, with a safety margin.

## Usage

```
python solver/main.py data/tsp_280.json output.json
```

Input is a JSON with `Timeout` (seconds) and `Matrix` (distance matrix). Output is a JSON list of city IDs in route order.

## Instances

Three larger instances in `data/`, based on TSPLIB (gr202, a280, gr666):

- `tsp_202.json`: 202 cities, timeout 300 s
- `tsp_280.json`: 280 cities, timeout 300 s
- `tsp_666.json`: 666 cities, timeout 300 s

Each file also contains coordinates and the known optimal route with its cost (`GlobalBest`, `GlobalBestVal`). These are only for comparing the result against the optimum, the solver never uses them.

## Parameters

Defaults in `lns_solver`: start and end temperature in % of the initial route cost, weight of the random destroy, safety margin and write interval. Chosen as reasonable defaults, to be tuned on more instances.

## Next steps

- 2-opt and or-opt as local search after repair, swap of two cities as a cheap extra move
- Incremental cost evaluation (function already prepared)
- Restart from the best route after a long time without improvement
- Parameter tuning on extra instances
