import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata
from sklearn.metrics import mean_squared_error

file_path = "Coordinates.txt"

xy_list = []
pan_tilt_list = []

with open(file_path, 'r') as file:
    for line in file:
        values = line.strip().split(',')
        
        x = int(values[0].split(':')[1].strip())
        y = int(values[1].split(':')[1].strip())
        
        pan = float(values[2].split(':')[1].strip())
        tilt = float(values[3].split(':')[1].strip())
        
        xy_list.append((x, y))
        pan_tilt_list.append((pan, tilt))

x_coords, y_coords = zip(*xy_list)

pan_values, tilt_values = zip(*pan_tilt_list)

scale_factor = 100

pan_values_scaled = np.array(pan_values) * scale_factor
tilt_values_scaled = np.array(tilt_values) * scale_factor

fig, ax = plt.subplots()

ax.quiver(x_coords, y_coords, pan_values_scaled, tilt_values_scaled, angles='xy', scale_units='xy', scale=1)

ax.set_xlim(min(x_coords)-10, max(x_coords)+10)
ax.set_ylim(min(y_coords)-10, max(y_coords)+10)

ax.set_xlabel('X')
ax.set_ylabel('Y')

ax.set_title('Vector Field')

plt.show()

#grid_x, grid_y = np.meshgrid(np.linspace(min(x_coords), max(x_coords), 100), np.linspace(min(y_coords), max(y_coords), 100))
grid_x, grid_y = np.meshgrid(np.linspace(0, 1920, 1920), np.linspace(0, 1080, 1080))

grid_pan = griddata((x_coords, y_coords), pan_values, (grid_x, grid_y), method='linear')
grid_tilt = griddata((x_coords, y_coords), tilt_values, (grid_x, grid_y), method='linear')

fig, ax = plt.subplots()

grid_pan_graph = grid_pan.copy()
grid_tilt_graph = grid_tilt.copy()

grid_pan_graph *= scale_factor
grid_tilt_graph *= scale_factor

#ax.quiver(grid_x, grid_y, grid_pan, grid_tilt, angles='xy', scale_units='xy', scale=1, width=0.004, headwidth=8, headlength=10)

for i in range(0, grid_x.shape[0], 40):
    for j in range(0, grid_x.shape[1], 40):
        ax.arrow(grid_x[i, j], grid_y[i, j], grid_pan_graph[i, j], grid_tilt_graph[i, j], head_width=7, head_length=4, fc='black')

ax.set_xlim(min(x_coords)-10, max(x_coords)+10)
ax.set_ylim(min(y_coords)-10, max(y_coords)+10)

ax.set_xlabel('X')
ax.set_ylabel('Y')

ax.set_title('Interpolated Vector Field')

plt.show()

nan_count_pan = np.isnan(pan_values).sum()
nan_count_tilt = np.isnan(tilt_values).sum()

print("NaN count in pan values:", nan_count_pan)
print("NaN count in tilt values:", nan_count_tilt)

file_path = "testCoordinates.txt"

test_xy_list = []
test_pan_tilt_list = []

with open(file_path, 'r') as file:
    for line in file:
        values = line.strip().split(',')
        
        x = int(values[0].split(':')[1].strip())
        y = int(values[1].split(':')[1].strip())
        
        pan = float(values[2].split(':')[1].strip())
        tilt = float(values[3].split(':')[1].strip())
        
        test_xy_list.append((x, y))
        test_pan_tilt_list.append((pan, tilt))

interpolated_pan_values = []
interpolated_tilt_values = []

for coord in test_xy_list:
    x, y = coord
    
    interpolated_pan = grid_pan[y, x]
    interpolated_tilt = grid_tilt[y, x]

    interpolated_pan_values.append(interpolated_pan)
    interpolated_tilt_values.append(interpolated_tilt)

known_pan_values, known_tilt_values = zip(*test_pan_tilt_list)

known_pan_values = np.array(known_pan_values)
known_tilt_values = np.array(known_tilt_values)

mse_pan = mean_squared_error(known_pan_values, interpolated_pan_values)
mse_tilt = mean_squared_error(known_tilt_values, interpolated_tilt_values)

print("MSE for pan:", mse_pan)
print("MSE for tilt:", mse_tilt)

print(f"{test_pan_tilt_list[0]} {interpolated_pan_values[0]} {interpolated_tilt_values[0]}")

# Initialize lists to store differences between interpolated and known pan and tilt values
pan_differences = []
tilt_differences = []

# Iterate over the test coordinates and calculate the differences
for coord, known_pt in zip(test_xy_list, test_pan_tilt_list):
    x, y = coord
    known_pan, known_tilt = known_pt
    
    # Access the interpolated pan and tilt values from the matrices using the test coordinates
    interpolated_pan_value = grid_pan[y, x]
    interpolated_tilt_value = grid_tilt[y, x]
    
    # Calculate the differences between interpolated and known pan and tilt values
    pan_difference = np.abs(interpolated_pan_value - known_pan)
    tilt_difference = np.abs(interpolated_tilt_value - known_tilt)
    
    # Append the differences to the respective lists
    pan_differences.append(pan_difference)
    tilt_differences.append(tilt_difference)

# Calculate the minimum and maximum errors
min_pan_error = np.min(pan_differences)
max_pan_error = np.max(pan_differences)
min_tilt_error = np.min(tilt_differences)
max_tilt_error = np.max(tilt_differences)

print("Minimum pan error:", min_pan_error)
print("Maximum pan error:", max_pan_error)
print("Minimum tilt error:", min_tilt_error)
print("Maximum tilt error:", max_tilt_error)
