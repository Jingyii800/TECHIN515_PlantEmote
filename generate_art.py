import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

# Load data from the file
with open('data.txt', 'r') as f:
    data = np.array([int(line.strip()) for line in f])

# Set up the plot
fig, ax = plt.subplots()
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.set_aspect('equal')

# Generate random polygons and color them based on data values
patches = []
colors = []
num_polygons = 100
for _ in range(num_polygons):
    num_sides = np.random.randint(3, 8)
    radius = np.random.rand() * 10  # Radius influences size
    position = np.random.rand(2) * 100  # Position on the canvas
    color_val = np.random.choice(data)  # Choose a random part of the data for color
    polygon = Polygon(radius * np.random.rand(num_sides, 2) + position, closed=True)
    patches.append(polygon)
    colors.append(color_val)  # Color mapped by data value

p = PatchCollection(patches, cmap=plt.cm.viridis, alpha=0.6)
p.set_array(np.array(colors))
ax.add_collection(p)

# Remove axes for a cleaner look
ax.set_axis_off()
plt.show()
