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


# Function to optimize the graph coloring
def optimise_colouring(G, num_colours):
    colours = {node: random.randint(0, num_colours - 1) for node in G.nodes()}
    conflicts = count_conflicts(G, colours)
    num_iterations = 0
    conflict_history = [conflicts]
    modified_graph = G.copy()
    while num_iterations < 1000 and conflicts > 0:
        # Select a node with conflicts
        node = random.choice(
            [node for node in modified_graph.nodes() if
             any(colours[node] == colours[neighbor] for neighbor in modified_graph.neighbors(node))])
        neighbor_colors = [colours[neighbor] for neighbor in modified_graph.neighbors(node)]
        all_possible_colors = set(range(num_colours))
        # Find the color that minimizes conflicts with neighbors
        count_conflicts_for_color = lambda color: neighbor_colors.count(color)
        min_conflicts_color = min(all_possible_colors, key=count_conflicts_for_color)
        colours[node] = min_conflicts_color
        conflicts = count_conflicts(modified_graph, colours)
        conflict_history.append(conflicts)
        num_iterations += 1
        # Add random edges after a certain number of iterations
        if num_iterations == 20:
            randomly_add_edges(modified_graph, 20)
            randomly_add_edges(modified_graph, 20)
    # Return optimized colors, iterations, conflict history, and whether conflicts are resolved
    if conflicts == 0:
        return colours, num_iterations, conflict_history, True
    else:
        return colours, num_iterations, conflict_history, False


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

# Perform color optimization until conflicts are resolved
conflicts_not_exceeded = True
total_conflict_history = []
while conflicts_not_exceeded != False:
    print(num_colours)
    # Optimize the coloring
    optimised_colours, num_iterations, conflict_history, conflicts_not_exceeded = optimise_colouring(Graph_loaded,
                                                                                                     num_colours
                                                                                                     )
    # If conflicts remain, increase the number of available colors
    if conflicts_not_exceeded == False:
        num_colours += 1
        break
    else:
        total_conflict_history.append((num_colours, conflict_history))
        num_colours -= 1

# Plot the conflict history for different numbers of colors
fig, ax = plt.subplots()
lines = []
labels = []
for num_colors, conflict_history in total_conflict_history:
    line, = plt.plot(range(len(conflict_history)), conflict_history, label=f"Num Colors Available: {num_colors}")
    lines.append(line)
    labels.append(f"Color: {num_colors}")

plt.xlabel("Iterations")
plt.ylabel("Conflicts")
plt.title("Conflict History")
plt.legend(lines, labels, title='Number of Colors', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True)

# Enable cursor for interactive annotation
mplcursors.cursor(hover=True).connect("add", lambda sel: sel.annotation.set_text(sel.artist.get_label()))

plt.show()
