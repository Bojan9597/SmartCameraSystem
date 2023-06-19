import numpy as np
from scipy.interpolate import Rbf
import itertools
from ErrorHandler import ErrorHandler
import cv2
import numpy as np
from scipy.interpolate import griddata
from scipy.interpolate import Rbf
class CoordinatesCalculator:
    def __init__(self, file):
        self.coordinatesWA = self.read_coordinatesWA(file)
        self.coordinatesPTZ = self.read_coordinatesPTZ(file)
        self.pani = []
        self.tilti= []
        self.calculateCorrespondingCoordinate(self.coordinatesWA, self.coordinatesPTZ, "linear", rescale=True)
        # self.calculateCorrespondingCoordinateRbf()
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

    def getNearestNotNan(self, i, j, matrix):
        counter = 1
        while True:
            for k in range(i - counter, i + counter):
                for l in range(j - counter, j + counter):
                    if k > 0 and k < 1080 and l > 0 and l < 1920:
                        if not np.isnan(matrix[k][l]):
                            return matrix[k][l]
                    else:
                        continue
            counter += 1

    def calculateCorrespondingCoordinateRbf(self,coordinatesWA,  coordinatesPTZ, method,epsilon,smoothness):
        x = np.linspace(0, 1920, 1920)
        y = np.linspace(0, 1080, 1080)
        X, Y = np.meshgrid(x, y)

        coordinateWAX = np.array(coordinatesWA)[:, 0]
        coordinateWAY = np.array(coordinatesWA)[:, 1]
        coordinatePTZpan = np.array(coordinatesPTZ)[:, 0]
        coordinatePTZtilt = np.array(coordinatesPTZ)[:, 1]

        # Perform RBF interpolation for pan
        rbf_pan = Rbf(coordinateWAX, coordinateWAY, coordinatePTZpan, function=method, epsilon=epsilon, smooth=smoothness)
        self.pani = rbf_pan(X, Y)

        # Perform RBF interpolation for tilt
        rbf_tilt = Rbf(coordinateWAX, coordinateWAY, coordinatePTZtilt, function=method, epsilon=epsilon, smooth=smoothness)
        self.tilti = rbf_tilt(X, Y)

        for i in range(1080):
            for j in range(1920):
                if np.isnan(self.pani[i][j]):
                    self.pani[i][j] = self.getNearestNotNan(i, j, self.pani)

                if np.isnan(self.tilti[i][j]):
                    self.tilti[i][j] = self.getNearestNotNan(i, j, self.tilti)

    def calculateCorrespondingCoordinate(self,coordinatesWA, coordinatesPTZ,method,rescale):
        x = np.linspace(0, 192, 192)
        y = np.linspace(0, 108, 108)
        X, Y = np.meshgrid(x, y)

        self.coordinateWAX = np.array(coordinatesWA)[:, 0] // 10
        self.coordinateWAY = np.array(coordinatesWA)[:, 1] // 10

        self.coordinatePTZpan = np.array(coordinatesPTZ)[:, 0]
        self.coordinatePTZtilt = np.array(coordinatesPTZ)[:, 1]

        self.pani = griddata((self.coordinateWAX, self.coordinateWAY), self.coordinatePTZpan, (X, Y), method=method,rescale=rescale)
        self.tilti = griddata((self.coordinateWAX, self.coordinateWAY), self.coordinatePTZtilt, (X, Y), method=method,rescale=rescale)
        for i in range(108):
            for j in range(192):
                if np.isnan(self.pani[i][j]):
                    self.pani[i][j] = self.getNearestNotNan(i, j, self.pani)

                if np.isnan(self.tilti[i][j]):
                    self.tilti[i][j] = self.getNearestNotNan(i, j, self.tilti)

    def getNearestNotNan(self, i, j, matrix):
        counter = 1
        while True:
            for k in range(i - counter, i + counter):
                for l in range(j - counter, j + counter):
                    if k > 0 and k < 108 and l > 0 and l < 192:
                        if not np.isnan(matrix[k][l]):
                            return matrix[k][l]
                    else:
                        continue
            counter += 1
    def getTiltAndPan(self,x, y):
        return self.pani[int(y/10)][int(x/10)], self.tilti[int(y/10)][int(x/10)]

    def errorCalculation(self):
        self.coordinatesWA = self.read_coordinatesWA("Coordinates.txt")
        self.coordinatesPTZ = self.read_coordinatesPTZ("Coordinates.txt")
        test_values_wa = self.read_coordinatesWA("testCoordinates.txt")
        test_values_ptz = self.read_coordinatesPTZ("testCoordinates.txt")
        methodRbf = ['multiquadric', 'inverse', 'gaussian', 'linear', 'cubic', 'quintic', 'thin_plate']
        best_error = (float('inf'))
        methodGrid = ['nearest', 'linear', 'cubic']
        epsilon = [0.1, 0.5, 1, 2, 5, 10]
        smoothness = [0.1, 0.5, 1, 2, 5, 10]
        rescale = [True, False]
        file = open("error.txt", "w")
        for i in range(3, 0, -1):

            coordinatesWA = self.coordinatesWA[::i]
            coordinatesPTZ = self.coordinatesPTZ[::i]
            with open("error.txt", "a") as file:
                file.write(f"Number of points: {len(coordinatesWA)}\n\n")
            for method in methodRbf:
                for e in epsilon:
                    for s in smoothness:
                        try:
                            self.calculateCorrespondingCoordinateRbf(coordinatesWA, coordinatesPTZ, method, e, s)
                            error = 0
                            for i in range(len(test_values_wa)):
                                pan, tilt = self.getTiltAndPan(test_values_wa[i][0], test_values_wa[i][1])
                                error += abs(pan - test_values_ptz[i][0]) + abs(tilt - test_values_ptz[i][1])
                            with open("error.txt", "a") as file:
                                file.write(
                                    f"RBF Interpolation: Method: {method} Epsilon: {e} Smoothness: {s} Error: {error}\n")
                            if error < best_error:
                                best_error = error
                                best_method = method
                                best_epsilon = e
                                best_smoothness = s
                        except:
                            continue
            for method in methodGrid:
                for r in rescale:
                    try:
                        self.calculateCorrespondingCoordinate(coordinatesWA, coordinatesPTZ, method, r)
                        error = 0
                        for i in range(len(test_values_wa)):
                            pan, tilt = self.getTiltAndPan(test_values_wa[i][0], test_values_wa[i][1])
                            error += abs(pan - test_values_ptz[i][0]) + abs(tilt - test_values_ptz[i][1])
                        with open("error.txt", "a") as file:
                            file.write(f"Grid Interpolation: Method: {method} Rescale: {r} Error: {error}\n")
                        if error < best_error:
                            best_error = error
                            best_method = method
                            best_rescale = r
                    except:
                        continue
        if best_method in methodRbf:
            print(
                f"Best method: {best_method} Best epsilon: {best_epsilon} Best smoothness: {best_smoothness} Error: {best_error}")
        else:
            print(f"Best method: {best_method} Best rescale: {best_rescale} Error: {best_error}")
# Usage example:
# calculator = CoordinatesCalculator('Coordinates.txt')

# calculator.errorCalculation()