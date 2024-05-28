import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from matplotlib.colors import LinearSegmentedColormap
import ast


# Load data from the file
try:
    with open('data1.txt', 'r') as f:
        data_str = f.read().strip()
        data = np.array(ast.literal_eval(data_str))
except FileNotFoundError:
    print("File 'data1.txt' not found.")
    exit(1)
except ValueError:
    print("Invalid data format in 'data1.txt'.")
    exit(1)


# Normalize data for better color mapping within 400-600 and above 600
data_normalized = np.zeros_like(data, dtype=float)
data_normalized[data <= 600] = (data[data <= 600] - 400) / (600 - 400)
data_normalized[data > 600] = 1 + (data[data > 600] - 600) / (data.max() - 600)


# Set up the plot
fig, ax = plt.subplots()
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.set_aspect('equal')


# Create a custom colormap with lower saturation and more transparent colors
colors = [(0, "#B3E5FC"), (0.25, "#B2DFDB"), (0.4, "#FFF9C4"), (0.65, "#FFCC80"), (1, "#FFAB91")]
cmap = LinearSegmentedColormap.from_list("custom_cmap", colors, N=512)


# Create a gradient background
gradient = np.linspace(0, 1, 512)
gradient = np.vstack((gradient, gradient))
ax.imshow(gradient, aspect='auto', cmap=cmap, extent=[0, 100, 0, 100])


# Generate random polygons and color them based on normalized data values
patches = []
polygon_colors = []
polygon_alphas = []
num_polygons = 80  # More polygons for a richer look
for _ in range(num_polygons):
    num_sides = np.random.randint(3, 10)
    base_radius = 5 + np.random.rand() * 20  # Variable radius for diversity
    position = np.random.rand(2) * 100  # Position on the canvas
    color_index = np.random.randint(0, len(data_normalized))  # Choose a random index
    color_val = data_normalized[color_index]  # Use normalized data value for color
    angles = np.linspace(0, 2 * np.pi, num_sides, endpoint=False)
    radius_noise = base_radius + np.random.rand(num_sides) * 10 - 5  # Add noise to radius
    polygon_points = np.c_[radius_noise * np.cos(angles), radius_noise * np.sin(angles)] + position
    polygon = Polygon(polygon_points, closed=True)
    patches.append(polygon)
    polygon_colors.append(color_val)  # Color mapped by normalized data value
    polygon_alphas.append(0.3 + 0.5 * color_val)  # Alpha value based on normalized data


# Ensure the alpha values are within the 0-1 range
polygon_alphas = np.clip(polygon_alphas, 0, 1)


# Create color mapping using the custom colormap
colors_rgba = cmap(np.clip(np.array(polygon_colors), 0, 1))

# Adjust color saturation and alpha to add more richness
for i in range(len(colors_rgba)):
    color_noise = np.random.rand() * 0.1 - 0.05  # Add small noise to color
    alpha_noise = np.random.rand() * 0.2 - 0.1  # Add small noise to alpha
    colors_rgba[i][:3] = np.clip(colors_rgba[i][:3] + color_noise, 0, 1)  # Adjust color
    colors_rgba[i][-1] = np.clip(polygon_alphas[i] + alpha_noise, 0, 1)  # Adjust alpha


# Add polygons to the plot
p = PatchCollection(patches, facecolors=colors_rgba, edgecolors='none')
ax.add_collection(p)


# Remove axes for a cleaner look
ax.set_axis_off()


# Display plot without transparent borders
fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
plt.show()
