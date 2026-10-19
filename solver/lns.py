import time
import random
import math
import json

RANDOM_ENGINE = random

def _write_instance_json(solution, file_path):
    with open(file_path, 'w') as f:
        json.dump(solution, f)

def is_permutation(route, city_count):
    # Write only routes with every city exactly once
    return sorted(route) == list(range(city_count))

def cost_trivial(route, matrix):
    cost_sum = 0
    for i in range (1, len(route)):
        start_vertix, end_vertix = route[i-1], route[i]
        edge_cost = matrix[start_vertix][end_vertix]
        cost_sum += edge_cost
    # Route is a cycle, so add also the edge from the last city back to the first
    cost_sum += matrix[route[-1]][route[0]]
    return cost_sum


def cost_incremental(original_cost, removed_edges, added_edges, matrix):
    # Only the changed edges are counted, prepared for the classical operators
    new_cost = original_cost
    for start_vertix, end_vertix in removed_edges:
        new_cost -= matrix[start_vertix][end_vertix]
    for start_vertix, end_vertix in added_edges:
        new_cost += matrix[start_vertix][end_vertix]
    return new_cost


def get_initial_solution(matrix, start_vertix):
    not_visited = set(range(len(matrix)))
    current_vertix = start_vertix
    route = [current_vertix]
    not_visited.remove(current_vertix)

    while (len(not_visited) > 0):
        # Nearest neighbor only from the cities not visited yet
        nn = min(not_visited, key=lambda city: matrix[current_vertix][city])
        route.append(nn)
        not_visited.remove(nn)
        current_vertix = nn

    return route


def get_neighbor_lists(matrix):
    neighbor_lists = []
    for city in range(len(matrix)):
        other_cities = list(range(len(matrix)))
        other_cities.remove(city)
        # From the nearest to the farthest, city is not its own neighbor
        sorted_neighbors = sorted(other_cities, key=lambda other: matrix[city][other])
        neighbor_lists.append(sorted_neighbors)
    return neighbor_lists


def destroy_radial(current_route, neighbor_lists, k_cities=range(1, 3), k_neighbors=range(3, 9)):
    destroy_cities = RANDOM_ENGINE.choice(k_cities)
    destroy_neighbors = RANDOM_ENGINE.choice(k_neighbors)

    removed = set()

    for i in range(destroy_cities):
        city_idx_to_remove = RANDOM_ENGINE.randrange(len(current_route))
        city_to_remove = current_route[city_idx_to_remove]
        # Log destroy step
        removed.add(city_to_remove)

        # Radial removal, the nearest neighbors of the removed city
        neighbors = neighbor_lists[city_to_remove][:destroy_neighbors]

        for nn in neighbors:
            removed.add(nn)

    # New route without the removed cities, current route stays untouched
    destroyed_route = [city for city in current_route if city not in removed]

    return destroyed_route, removed


def destroy_random(current_route, k_random=range(2, 11)):
    destroy_size = RANDOM_ENGINE.choice(k_random)
    # Small instances can have less cities than k
    destroy_size = min(destroy_size, len(current_route))

    removed = set(RANDOM_ENGINE.sample(current_route, destroy_size))
    destroyed_route = [city for city in current_route if city not in removed]

    return destroyed_route, removed


def repair(destroyed_route, removed, matrix):

    new_route = destroyed_route

    # Removed cities go back in random order
    insert_order = list(removed)
    RANDOM_ENGINE.shuffle(insert_order)

    for removed_city in insert_order:
        cheapest_position = 0
        cheapest_increase = math.inf
        # i = 0 is the edge from the last city back to the first
        for i in range(len(new_route)):
            city_a, city_b = new_route[i-1], new_route[i]
            increase = matrix[city_a][removed_city] + matrix[removed_city][city_b] - matrix[city_a][city_b]
            if increase < cheapest_increase:
                cheapest_increase = increase
                cheapest_position = i
        new_route.insert(cheapest_position, removed_city)

    return new_route



def accept_new(old_cost, new_cost, T):
    delta = new_cost - old_cost

    # Better or equally good solution is always accepted
    if delta <= 0:
        return True
    # No temperature left (route cost 0), only better solutions
    if T <= 0:
        return False

    probability = math.exp(-delta/T)

    # Sample from probability, Metropolis criterion
    return RANDOM_ENGINE.random() < probability



# TODO: Classical operators
def two_opt():
    pass
def swap_two():
    pass



def lns_solver(instance, program_start_time, output_path, safety_margin=3, T_start=0.5, T_end=0.005, random_destroy_weight=0.3, write_interval=2):
    """
    s ← s0;  s* ← s
    repeat
        s′ ← s
        destroy part of s′          (sekce 4)
        repair s′                   (sekce 5)
        if f(s′) < f(s*) then s* ← s′      (best)
        if accept(s′, s) then s ← s′        (current, sekce 8)
    until stopping criteria       (sekce 10)
    return s*
    """

    time_limit = instance['Timeout']
    matrix = instance['Matrix']
    # Short time limits (tests) would be eaten by the whole margin
    safety_margin = min(safety_margin, 0.1 * time_limit)


    # Perform planned initial solution
    start_vertix = RANDOM_ENGINE.randint(0, len(matrix) - 1)
    initial_solution = get_initial_solution(matrix, start_vertix)
    if is_permutation(initial_solution, len(matrix)):
        _write_instance_json(initial_solution, output_path)
    last_write_time = time.time()

    # Nearest neighbors of every city, for radial destroy
    neighbor_lists = get_neighbor_lists(matrix)

    # Set up initial route and cost
    current_route = initial_solution
    current_cost = cost_trivial(initial_solution, matrix)
    best_route = list(initial_solution)
    best_cost = current_cost

    # T_start and T_end are in % of the initial route cost
    T_start_value = current_cost * T_start / 100
    T = T_start_value

    while time.time() - program_start_time < time_limit - safety_margin:
        # Destroy, random removal for diversity, radial removal to rebuild a whole region
        if RANDOM_ENGINE.random() < random_destroy_weight:
            destroyed_route, removed = destroy_random(current_route)
        else:
            destroyed_route, removed = destroy_radial(current_route, neighbor_lists)

        # Repair
        new_route = repair(destroyed_route, removed, matrix)

        # Classical operators ?

        # New evaluation
        # TODO: Incremental cost of destroy + repair, together with the classical operators
        new_cost = cost_trivial(new_route, matrix)

        if new_cost < best_cost:
            best_cost = new_cost
            best_route = list(new_route)
            # write only once in a while, the last write is after the loop
            if time.time() - last_write_time > write_interval:
                if is_permutation(best_route, len(matrix)):
                    _write_instance_json(best_route, output_path)
                last_write_time = time.time()

        # Acceptance
        if accept_new(current_cost, new_cost, T):
            current_route = new_route
            current_cost = new_cost

        # TODO: Restart from the best route after a long time without improvement

        elapsed_time_pc = (time.time() - program_start_time) / (time_limit - safety_margin)

        # Annealing, exponential cooling from T_start to T_end by elapsed time
        T = T_start_value * (T_end / T_start) ** elapsed_time_pc

    # Write the best route at the end
    if is_permutation(best_route, len(matrix)):
        _write_instance_json(best_route, output_path)

    return best_route
