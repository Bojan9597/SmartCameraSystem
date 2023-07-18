import numpy as np
from scipy.interpolate import Rbf
import itertools
from ErrorHandler import ErrorHandler
import cv2
import numpy as np
from scipy.interpolate import griddata
from scipy.interpolate import Rbf
from scipy.interpolate import LinearNDInterpolator
from pykrige.ok import OrdinaryKriging


class CoordinatesCalculator:
    def __init__(self, file):
        self.coordinatesWA = self.read_coordinatesWA(file)
        self.coordinatesPTZ = self.read_coordinatesPTZ(file)
        self.pani = []
        self.tilti = []
        self.calculateCorrespondingCoordinateGrid(self.coordinatesWA, self.coordinatesPTZ, "linear", rescale=True)
        # self.calculateCorrespondingCoordinateLinearND(self.coordinatesWA, self.coordinatesPTZ, "linear", rescale=True)
        # self.calculateCorrespondingCoordinateKriging(self.coordinatesWA, self.coordinatesPTZ, "linear", rescale=True)
        # self.calculateCorrespondingCoordinateRbf(self.coordinatesWA, self.coordinatesPTZ, "linear", rescale=True)

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
                    if k > 0 and k < 108 and l > 0 and l < 192:
                        if not np.isnan(matrix[k][l]):
                            return matrix[k][l]
                    else:
                        continue
            counter += 1

    def calculateCorrespondingCoordinateRbf(self, coordinatesWA, coordinatesPTZ, method, epsilon, smoothness):
        x = np.linspace(0, 1920, 1920)
        y = np.linspace(0, 1080, 1080)
        X, Y = np.meshgrid(x, y)

        coordinateWAX = np.array(coordinatesWA)[:, 0]
        coordinateWAY = np.array(coordinatesWA)[:, 1]
        coordinatePTZpan = np.array(coordinatesPTZ)[:, 0]
        coordinatePTZtilt = np.array(coordinatesPTZ)[:, 1]

        # Perform RBF interpolation for pan
        rbf_pan = Rbf(coordinateWAX, coordinateWAY, coordinatePTZpan, function=method, epsilon=epsilon,
                      smooth=smoothness)
        self.pani = rbf_pan(X, Y)

        # Perform RBF interpolation for tilt
        rbf_tilt = Rbf(coordinateWAX, coordinateWAY, coordinatePTZtilt, function=method, epsilon=epsilon,
                       smooth=smoothness)
        self.tilti = rbf_tilt(X, Y)

        for i in range(1080):
            for j in range(1920):
                if np.isnan(self.pani[i][j]):
                    self.pani[i][j] = self.getNearestNotNan(i, j, self.pani)

                if np.isnan(self.tilti[i][j]):
                    self.tilti[i][j] = self.getNearestNotNan(i, j, self.tilti)

    def calculateCorrespondingCoordinateGrid(self, coordinatesWA, coordinatesPTZ, method, rescale):
        x = np.linspace(0, 192, 192)
        y = np.linspace(0, 108, 108)
        X, Y = np.meshgrid(x, y)

        self.coordinateWAX = np.array(coordinatesWA)[:, 0] // 10
        self.coordinateWAY = np.array(coordinatesWA)[:, 1] // 10

        self.coordinatePTZpan = np.array(coordinatesPTZ)[:, 0]
        self.coordinatePTZtilt = np.array(coordinatesPTZ)[:, 1]

        self.pani = griddata((self.coordinateWAX, self.coordinateWAY), self.coordinatePTZpan, (X, Y), method=method,
                             rescale=rescale)
        self.tilti = griddata((self.coordinateWAX, self.coordinateWAY), self.coordinatePTZtilt, (X, Y), method=method,
                              rescale=rescale)
        for i in range(108):
            for j in range(192):
                if np.isnan(self.pani[i][j]):
                    self.pani[i][j] = self.getNearestNotNan(i, j, self.pani)

                if np.isnan(self.tilti[i][j]):
                    self.tilti[i][j] = self.getNearestNotNan(i, j, self.tilti)

    def calculateCorrespondingCoordinateLinearND(self, coordinatesWA, coordinatesPTZ, rescale):
        x = np.linspace(0, 192, 192)
        y = np.linspace(0, 108, 108)
        X, Y = np.meshgrid(x, y)

        coordinateWAX = np.array(coordinatesWA)[:, 0] // 10
        coordinateWAY = np.array(coordinatesWA)[:, 1] // 10

        coordinatePTZpan = np.array(coordinatesPTZ)[:, 0]
        coordinatePTZtilt = np.array(coordinatesPTZ)[:, 1]

        points = np.column_stack((coordinateWAX, coordinateWAY))
        values_pan = coordinatePTZpan
        values_tilt = coordinatePTZtilt

        # Create LinearNDInterpolator for pan
        interp_pan = LinearNDInterpolator(points, values_pan, rescale=rescale)
        self.pani = interp_pan((X, Y))

        # Create LinearNDInterpolator for tilt
        interp_tilt = LinearNDInterpolator(points, values_tilt, rescale=rescale)
        self.tilti = interp_tilt((X, Y))

        for i in range(108):
            for j in range(192):
                if np.isnan(self.pani[i][j]):
                    self.pani[i][j] = self.getNearestNotNan(i, j, self.pani)

                if np.isnan(self.tilti[i][j]):
                    self.tilti[i][j] = self.getNearestNotNan(i, j, self.tilti)

    def calculateCorrespondingCoordinateKriging(self, coordinatesWA, coordinatesPTZ):
        x = np.linspace(0, 192, 192)
        y = np.linspace(0, 108, 108)
        X, Y = np.meshgrid(x, y)

        coordinateWAX = np.array(coordinatesWA)[:, 0] // 10
        coordinateWAY = np.array(coordinatesWA)[:, 1] // 10

        coordinatePTZpan = np.array(coordinatesPTZ)[:, 0]
        coordinatePTZtilt = np.array(coordinatesPTZ)[:, 1]

        points = np.column_stack((coordinateWAX, coordinateWAY))
        values_pan = coordinatePTZpan
        values_tilt = coordinatePTZtilt

        # Create OrdinaryKriging object for pan
        kriging_pan = OrdinaryKriging(points[:, 0], points[:, 1], values_pan)
        self.pani, _ = kriging_pan.execute('grid', x, y)

        # Create OrdinaryKriging object for tilt
        kriging_tilt = OrdinaryKriging(points[:, 0], points[:, 1], values_tilt)
        self.tilti, _ = kriging_tilt.execute('grid', x, y)

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

    def getTiltAndPan(self, x, y):
        return self.pani[int(y / 10)][int(x / 10)], self.tilti[int(y / 10)][int(x / 10)]

    # def errorCalculation(self):
    #     self.coordinatesWA = self.read_coordinatesWA("../CoordinatesForCalibration.txt")
    #     self.coordinatesPTZ = self.read_coordinatesPTZ("../CoordinatesForCalibration.txt")
    #     test_values_wa = self.read_coordinatesWA("testCoordinates.txt")
    #     test_values_ptz = self.read_coordinatesPTZ("testCoordinates.txt")
    #     methodRbf = ['multiquadric', 'inverse', 'gaussian', 'linear', 'cubic', 'quintic', 'thin_plate']
    #     best_error = (float('inf'))
    #     best_method_type = ""
    #     methodGrid = ['nearest', 'linear', 'cubic']
    #     epsilon = [0.1, 0.5, 1, 2, 5, 10]
    #     smoothness = [0.1, 0.5, 1, 2, 5, 10]
    #     rescale = [True, False]
    #     file = open("error.txt", "w")
    #     for i in range(3, 0, -1):

    #         coordinatesWA = self.coordinatesWA[::i]
    #         coordinatesPTZ = self.coordinatesPTZ[::i]
    #         with open("error.txt", "a") as file:
    #             file.write(f"Number of points: {len(coordinatesWA)}\n\n")
    #         with open("error.txt", "a") as file:
    #             file.write("RBF Interpolation:\n")
    #         for method in methodRbf:
    #             for e in epsilon:
    #                 for s in smoothness:
    #                     try:
    #                         self.calculateCorrespondingCoordinateRbf(coordinatesWA, coordinatesPTZ, method, e, s)
    #                         error = 0
    #                         for i in range(len(test_values_wa)):
    #                             pan, tilt = self.getTiltAndPan(test_values_wa[i][0], test_values_wa[i][1])
    #                             error += abs(pan - test_values_ptz[i][0]) + abs(tilt - test_values_ptz[i][1])
    #                         error /= len(test_values_wa)
    #                         with open("error.txt", "a") as file:
    #                             file.write(
    #                                 f"RBF Interpolation: Method: {method} Epsilon: {e} Smoothness: {s} Error: {error}\n")
    #                         if error < best_error:
    #                             best_method_type = "RBF"
    #                             best_error = error
    #                             best_method = method
    #                             best_epsilon = e
    #                             best_smoothness = s
    #                     except:
    #                         continue
    #         with open("error.txt", "a") as file:
    #             file.write("\n Grid Interpolation\n")
    #         for method in methodGrid:
    #             for r in rescale:
    #                 try:
    #                     self.calculateCorrespondingCoordinateGrid(coordinatesWA, coordinatesPTZ, method, r)
    #                     error = 0
    #                     for i in range(len(test_values_wa)):
    #                         pan, tilt = self.getTiltAndPan(test_values_wa[i][0], test_values_wa[i][1])
    #                         error += abs(pan - test_values_ptz[i][0]) + abs(tilt - test_values_ptz[i][1])
    #                     error /= len(test_values_wa)
    #                     with open("error.txt", "a") as file:
    #                         file.write(f"Grid Interpolation: Method: {method} Rescale: {r} Error: {error}\n")
    #                     if error < best_error:
    #                         best_method_type = "Grid"
    #                         best_error = error
    #                         best_method = method
    #                         best_rescale = r
    #                 except:
    #                     continue
    #         with open("error.txt", "a") as file:
    #             file.write("\nLinearND Interpolation\n")
    #         for rescaled in rescale:
    #             try:
    #                 self.calculateCorrespondingCoordinateLinearND(coordinatesWA, coordinatesPTZ, rescale=rescaled)
    #                 error = 0
    #                 for i in range(len(test_values_wa)):
    #                     pan, tilt = self.getTiltAndPan(test_values_wa[i][0], test_values_wa[i][1])
    #                     error += abs(pan - test_values_ptz[i][0]) + abs(tilt - test_values_ptz[i][1])
    #                 error = error / len(test_values_wa)
    #                 with open("error.txt", "a") as file:
    #                     file.write(f"LinearND Interpolation: Method: {rescaled} Error: {error}\n")
    #                 if error < best_error:
    #                     best_method_type = "LinearND"
    #                     best_error = error
    #                     best_rescale = rescaled
    #             except Exception as e:
    #                 print(e)
    #                 continue
    #         with open("error.txt", "a") as file:
    #             file.write(f"\nKriging Interpolation: \n")
    #         self.calculateCorrespondingCoordinateKriging(coordinatesWA, coordinatesPTZ)
    #         error = 0
    #         try:
    #             for i in range(len(test_values_wa)):
    #                 pan, tilt = self.getTiltAndPan(test_values_wa[i][0], test_values_wa[i][1])
    #                 error += abs(pan - test_values_ptz[i][0]) + abs(tilt - test_values_ptz[i][1])
    #             error /= len(test_values_wa)
    #             with open("error.txt", "a") as file:
    #                 file.write(f"Kriging Interpolation: Error: {error}\n")
    #             if error < best_error:
    #                 best_error = error
    #                 best_method_type = "Kriging"
    #         except:
    #             continue

    #     with open("bestError.txt", "a") as file:
    #         if best_method_type == "RBF":
    #             pass
    #             file.write(
    #                 f"RBF Interpolation: Method: {best_method} Epsilon: {best_epsilon} Smoothness: {best_smoothness} Error: {best_error}\n")
    #         elif best_method_type == "Grid":
    #             pass
    #             file.write(f"Grid Interpolation: Method: {best_method} Rescale: {best_rescale} Error: {best_error}\n")
    #         elif best_method_type == "LinearND":
    #             file.write(f"LinearND Interpolation: Method: {best_rescale} Error: {best_error}\n")
    #         elif best_method_type == "Kriging":
    #             file.write(f"Kriging Interpolation: Error: {best_error}\n")


# Usage example:
# calculator = CoordinatesCalculator("../CoordinatesForCalibration.txt")

# calculator.errorCalculation()