import numpy as np
from scipy.interpolate import Rbf
import itertools
from ErrorHandler import ErrorHandler

class CoordinatesCalculator:
    def __init__(self, file):
        self.coordinatesWA = self.read_coordinatesWA(file)
        self.coordinatesPTZ = self.read_coordinatesPTZ(file)

    def read_coordinatesWA(self, file):
        try:
            coordinates = []
            with open(file, 'r') as f:
                for line in f:
                    x, y = self.extract_coordinatesWA(line)
                    coordinates.append((x, y))
            return coordinates
        except Exception as e:
            ErrorHandler.displayErrorMessage(f"Error in reading coordinates for WA: \n {e}")


    def read_coordinatesPTZ(self, file):
        try:
            coordinates = []
            with open(file, 'r') as f:
                for line in f:
                    pan, tilt = self.extract_coordinatesPTZ(line)
                    coordinates.append((pan, tilt))
            return coordinates
        except Exception as e:
            ErrorHandler.displayErrorMessage(f"Error in reading coordinates for PTZ: \n {e}")

    def extract_coordinatesWA(self, line):
        try:
            parts = line.split(',')
            x = float(parts[0].split(': ')[1].strip())
            y = float(parts[1].split(': ')[1].strip())
            return x, y
        except Exception as e:
            ErrorHandler.displayErrorMessage(f"Error in extracting coordinates for WA: \n {e}")

    def extract_coordinatesPTZ(self, line):
        try:
            parts = line.split(',')
            pan = float(parts[2].split(':')[1].strip())
            tilt = float(parts[3].split(':')[1].strip())
            return pan, tilt
        except Exception as e:
            ErrorHandler.displayErrorMessage(f"Error in extracting coordinates for PTZ: \n {e}")

    def calculate_corresponding_coordinate(self, x, y):
        try:
            src_points = np.array(self.coordinatesWA, dtype=np.float32)
            dst_points = np.array(self.coordinatesPTZ, dtype=np.float32)

            # Separate input and output coordinates
            input_x = src_points[:, 0]
            input_y = src_points[:, 1]
            output_ptzX = dst_points[:, 0]
            output_ptzY = dst_points[:, 1]

            # Define the parameter combinations to evaluate
            epsilon_values = [0.01,0.05, 0.1,0.5, 1.0,5,  10.0]  # Adjust the epsilon values as needed
            smoothing_functions = ['linear', 'cubic', 'quintic']  # Choose the desired smoothing functions
            grid_resolution = 1000  # Adjust the grid resolution as needed

            best_ptzX = None
            best_ptzY = None
            best_error = float('inf')

            # Perform grid search to find the best RBF interpolation function
            for epsilon, smoothing in itertools.product(epsilon_values, smoothing_functions):
                function_kwargs = {'function': smoothing, 'smooth': epsilon}

                # Create the RBF interpolation function
                rbf_x = Rbf(input_x, input_y, output_ptzX, **function_kwargs)
                rbf_y = Rbf(input_x, input_y, output_ptzY, **function_kwargs)

                # Create a finer grid for interpolation
                x_grid = np.linspace(min(input_x), max(input_x), grid_resolution)
                y_grid = np.linspace(min(input_y), max(input_y), grid_resolution)

                # Calculate the corresponding ptzX and ptzY for the given x and y
                ptzX = rbf_x(x, y)
                ptzY = rbf_y(x, y)

                # Calculate the error between the interpolated values and the actual values
                error = np.abs(ptzX - output_ptzX).mean() + np.abs(ptzY - output_ptzY).mean()

                # Update the best results if the current error is lower
                if error < best_error:
                    best_error = error
                    best_ptzX = ptzX
                    best_ptzY = ptzY

                print(error)

            # Limit ptzX and ptzY to the range of -1 to 1
            ptzX = max(min(best_ptzX, 1), -1)
            ptzY = max(min(best_ptzY, 1), -1)

            return ptzX, ptzY
        except Exception as e:
            ErrorHandler.displayErrorMessage(f"Error in calculating corresponding coordinates: \n {e}")
            return 0, 0


# Usage example:
calculator = CoordinatesCalculator('Coordinates.txt')
ptz_x, ptz_y = 123, 648
wa_x, wa_y = calculator.calculate_corresponding_coordinate(ptz_x, ptz_y)
print("Corresponding Coordinates:")
print(f"X: {wa_x}, Y: {wa_y}")
