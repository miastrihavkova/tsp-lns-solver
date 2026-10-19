## Solution representation

The solution will be represented as an array of integers (IDs of the vertices).

## Infeasible solutions

The algorithm is designed to strictly operate with permutations, avoiding infeasible solutions entirely (just check the permutation befor ewriting to a file).

## Initial solution

A trivial initial solution is a randomly shuffled array of IDs. A better initial solution is generated using a greedy algorithm (nearest neighbor). Optionally add 2-opt for nearest neighbor.

## Destroy/repair methods

**First take**

*The destroy method removes k random edges from the current solution. The repair method uses a greedy approach to reconnect the vertices to achieve a better overall cost.*

**Final decision**

If we take out edges, there are still parts of the path left and repair needs to consider the order as well, which is difficult / costly. It is simpler to remove k cities from the route. We will use random removal (k random cities) for diversity and radial removal (random city + its k-1 nearest neighbors) to rebuild a whole region. K should be chosen randomly from an interval. Simply taking out cities and returning them is cheapest insertion and easier to code. For repair, removed cities are inserted one by one in random order, each to the position with the smallest cost increase.

## Classical operators

2-opt and or-opt as local search after each repair, swap of 2 cities as a cheap extra move. 2-opt can also be used once on the initial solution (optional).

## Cost function

### Trivial evaluation

Computes the sum of all edge lengths in the current route, which needs to be minimized.

### Incremental evaluation (our choice)

Computes only the difference (delta) in cost caused by a local move, rather than recalculating the entire route from scratch.

## Solution acceptance

**First take**

*A new solution is accepted only if its overall cost is lower than the current best solution.*

**Final decision**

The initial take was a hill climbing in its core, which can get very easily stuck on local optima. We will try to implement simulated annealing. Worse solution will be accepted with probability `exp(-delta/T)`, T is relative to the route cost and decreases with elapsed time, Best solution should also be always stored separately.

## Termination criteria

**First take**

*The algorithm terminates if the allocated time limit runs out or if it gets stuck in a local optimum.*

**Final decision**

The combination of hill climbing and time limit can waste a lot of time being stuck, which can be used for more search. For time limit, we should use limit minus safety margin, measured form the process start If there is no improvement for. along time, we can restart from the best solution. The best solution is written to the output file during the run.

## Parametrization

The interval for k, so k_min, k_max, destroy operator weights, T start and T end (in % of cost), safety time margin. First as defaults in code, tuned later, ideally checked on extra instances.
