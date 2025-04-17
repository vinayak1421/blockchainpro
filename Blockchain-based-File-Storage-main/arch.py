import matplotlib.pyplot as plt
import networkx as nx

# Create a directed graph
G = nx.DiGraph()

# Define the layers and components in the architecture
layers = {
    "Access Control": ["RFID Scanner", "Fingerprint Sensor", "PIN Authentication"],
    "Secure Vault": ["Document Upload System", "Blockchain for Document Security"],
    "Fire Safety": ["Thermal Sensors", "LED Alert", "Siren"],
    "System Security": ["Virtual Machine", "VM Isolation", "Regular Patching", "Security Policies"],
}

# Add edges to represent connections between layers and components
connections = [
    ("RFID Scanner", "Fingerprint Sensor"),
    ("Fingerprint Sensor", "PIN Authentication"),
    ("PIN Authentication", "Secure Vault"),
    ("Document Upload System", "Blockchain for Document Security"),
    ("Thermal Sensors", "LED Alert"),
    ("Thermal Sensors", "Siren"),
    ("Virtual Machine", "VM Isolation"),
    ("Virtual Machine", "Regular Patching"),
    ("Virtual Machine", "Security Policies"),
]

# Add nodes and edges to the graph
for layer, components in layers.items():
    for component in components:
        G.add_node(component, layer=layer)

for connection in connections:
    G.add_edge(*connection)

# Generate the layout for the graph
pos = nx.spring_layout(G, seed=42)

# Draw the nodes with labels
plt.figure(figsize=(12, 8))
nx.draw_networkx_nodes(G, pos, node_size=3000, node_color="lightblue")
nx.draw_networkx_labels(G, pos, font_size=10, font_color="black")

# Draw the edges
nx.draw_networkx_edges(G, pos, arrowstyle="->", arrowsize=10, edge_color="gray")

# Add title and display the diagram
plt.title("Layered Architecture Diagram")
plt.axis("off")
plt.show()
