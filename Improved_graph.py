import pickle
import random
import networkx as nx
import matplotlib.pyplot as plt
import mplcursors

# Set the number of available colors
num_colours = 30


# Function to count conflicts in the graph coloring
def count_conflicts(G, colours):
    conflicts = 0
    for node in G.nodes():
        for neighbor in G.neighbors(node):
            if colours[node] == colours[neighbor]:
                conflicts += 1
    return conflicts // 2


# Function to randomly add edges to the graph
def randomly_add_edges(G, num_edges):
    for _ in range(num_edges):
        node1 = random.choice(list(G.nodes()))
        node2 = random.choice(list(G.nodes()))
        if node1 != node2 and not G.has_edge(node1, node2):
            G.add_edge(node1, node2)


# Function to randomly delete edges from the graph
def randomly_delete_edges(G, num_edges):
    edges_to_remove = random.sample(list(G.edges()), num_edges)
    G.remove_edges_from(edges_to_remove)


# Function to optimize the graph coloring using TABU search
def optimise_colouring(G, num_colours, modified_graph):
    # Initialize colors randomly for each node
    colours = {node: random.randint(0, num_colours - 1) for node in G.nodes()}
    best_solution = colours.copy()
    best_conflicts = count_conflicts(G, best_solution)
    conflict_history = [best_conflicts]
    tabu_list = []
    modified_graph = G.copy()
    iterations = 0
    while iterations < 1000 and best_conflicts > 0:
        # Generate neighbor solutions by changing colors of nodes
        neighbour_solutions = []
        for node in modified_graph.nodes():
            for colour in range(num_colours):
                if colours[node] != colour:
                    neighbour = colours.copy()
                    neighbour[node] = colour
                    neighbour_conflicts = count_conflicts(modified_graph, neighbour)
                    neighbour_solutions.append((neighbour, neighbour_conflicts))
        # Sort neighbor solutions based on conflicts count
        neighbour_solutions.sort(key=lambda x: x[1])

        # Find the best neighbor solution not in the tabu list
        best_neighbour = None
        for neighbour, conflicts in neighbour_solutions:
            if neighbour not in tabu_list:
                best_neighbour = neighbour
                break

        # If no non-tabu neighbor found, select the best among all neighbors
        if best_neighbour is None:
            best_solution = neighbour_solutions[0][0]

        # Update current colors and conflicts with the best neighbor solution
        colours = best_neighbour
        current_conflicts = count_conflicts(G, colours)

        # Update tabu list
        tabu_list.append(best_neighbour)
        if len(tabu_list) == 10:
            tabu_list.pop(0)

        # Update best solution if current conflicts are fewer
        if current_conflicts < best_conflicts:
            best_solution = colours.copy()
            best_conflicts = current_conflicts
        iterations += 1
        # Add random edges after a certain number of iterations
        if iterations == 20:
            randomly_add_edges(modified_graph, 20)
            randomly_add_edges(modified_graph, 20)
        # Append current conflicts to conflict history
        conflict_history.append(best_conflicts)

    # Return conflict history, iterations, and whether conflicts are resolved
    if best_conflicts == 0:
        return conflict_history, iterations, True
    else:
        return conflict_history, iterations, False


# Load the graph from a pickle file
with open("graph_with_colors.pickle", "rb") as f:
    Graph_loaded = pickle.load(f)

# Get node colors from the loaded graph
node_colors = nx.get_node_attributes(Graph_loaded, "colour").values()

# Draw the initial graph with colors
plt.figure(figsize=(8, 6))
pos = nx.spring_layout(Graph_loaded)
nx.draw(
    Graph_loaded,
    pos,
    with_labels=True,
    node_color=list(node_colors),  # Convert colors to a list
    cmap=plt.cm.rainbow,  # Use a color map
    node_size=200,
    edge_color="gray",
    linewidths=0.05,
    font_size=10,
)
plt.title("Initial Graph with Colors")
plt.show()

# Perform color optimization using TABU search until conflicts are resolved
zero_found = True
total_conflict_history = []
modified_graph = Graph_loaded.copy()
while zero_found != False:
    print(num_colours)
    # Optimize the coloring using TABU search
    conflict_history, num_iterations, zero_found = optimise_colouring(Graph_loaded, num_colours, modified_graph)
    # If conflicts remain, increase the number of available colors
    if zero_found == False:
        num_colours += 1
        break
    else:
        total_conflict_history.append((num_colours, conflict_history))
        num_colours -= 1

# Plot the conflict history for different numbers of colors using TABU search
fig, ax = plt.subplots()
lines = []
labels = []
for num_colors, conflict_history in total_conflict_history:
    line, = plt.plot(range(len(conflict_history)), conflict_history, label=f"Num Colors Available: {num_colors}")
    lines.append(line)
    labels.append(f"Color: {num_colors}")

plt.xlabel("Iterations")
plt.ylabel("Conflicts")
plt.title("Conflict History using TABU search")
plt.legend(lines, labels, title='Number of Colors', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True)

# Enable cursor for interactive annotation
mplcursors.cursor(hover=True).connect("add", lambda sel: sel.annotation.set_text(sel.artist.get_label()))

plt.show()
