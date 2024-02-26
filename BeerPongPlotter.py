# ==================================================================
# Design Unit  : BeerPongPlotter.py
#
# File Name    : BeerPongPlotter.py
#
# Purpose      : This file contains the BeerPongPlotter class to plot the
#               Beer pong configurations in the Studentdorm GLH
#
# Author       : Vincent von Appen
#
# System       : MacOS M1/Python3.11
# ------------------------------------------------------------------
#
# Revision List
# Version      Author              Date        Changes
# 1.0          Vincent von Appen   25.02.2024  Initial version
# ==================================================================

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path
import numpy as np


Radius = 1
X_DIS = 2.1
Y_DIS = 2.1


class Position:
    """
    A class to represent a position on the beer pong table.

    Index:
        (1)
       (2)(3)
     (4)(5)(6)
    (7)(8)(9)(10)

    Position is a tuple (row, column) where row is the y-coordinate and column is the x-coordinate.
            (1, 1)
         (2, 1)(2, 2)
      (3, 1)(3, 2)(3, 3)
    (4, 1)(4, 2)(4, 3)(4, 4)

    X and Y coordinates:
                                        (0, 0)
                        (-Y_DIS, Y_DIS/2)(-Y_DIS, X_DIS/2)
                    (-2*Y_DIS, -X_DIS)(-2*Y_DIS, 0)(2*Y_DIS, X_DIS)
    (-3*Y_DIS, -1.5*X_DIS/2)(-3*Y_DIS, -X_DIS/2)(-3*Y_DIS, X_DIS/2)(-3*Y_DIS, 1.5*X_DIS/2)

    Positions can be with half steps, e.g. (1.5, 1.5) is the middle of the first row.

    Attributes:
    - index: The index of the position.
    - position: The position as a tuple (row, column)
    - id: The hash of the position.
    - x: The x-coordinate of the position.
    - y: The y-coordinate of the position.
    """

    def __init__(self, index, position = (0, 0)):
        """
        Construct a new BeerPongPosition object.

        Parameters:
        - index: The index of the position.
        - position: The position as a tuple (row, column) (default: (0, 0)).
        """
        self.index = index
        self.position = position
        #create hash for id
        self.id = hash(self.position)
        
        if position != (0, 0) and self._check_position():
            self._init_xy_position()
        else:
            self._init_xy_index()
        
    
    def _check_position(self):
        """
        Check if the position is valid.

        The position must be a tuple (row, column) where row is the y-coordinate and column is the x-coordinate.

        Returns:
        - True if the position is valid, False otherwise.
        """
        if self.position[0] < 0 or self.position[1] < 0:
            raise ValueError("Position must be positive.")
        if self.position[0] < self.position[1]:
            raise ValueError("The row must be greater than or equal to the column.")
        if self.position[0] > 4:
            raise ValueError("The row must be less than or equal to 4.")
        if self.position[1] > 4:
            raise ValueError("The column must be less than or equal to 4.")

        # Check if using full numbers without half steps
        if all(isinstance(i, int) for i in self.position):
            expected_index = sum(range(self.position[0])) + self.position[1]
            if self.index != expected_index:
                raise ValueError(f"Index does not match the expected value for the position {self.position}. Expected index: {expected_index}, given index: {self.index}.")

        return True

    def _init_xy_position(self):
        """
        Initialize the x and y coordinates of the position.

        Position is a tuple (row, column) where row is the y-coordinate and column is the x-coordinate.
        This needs to be converted to the x and y coordinates of the position.
        """
        # Centering the triangle on the x-axis
        max_width = (self.position[0] - 1) * X_DIS  # Maximum width of the current row
        start_x = -max_width / 2  # Starting x position to center the row

        # Calculate the actual x and y positions
        self.x = start_x + (self.position[1] - 1) * X_DIS
        self.y = -(self.position[0] - 1) * Y_DIS


    def _init_xy_index(self):
        """
        Initialize the x and y coordinates of the position.

        Index:
            (1)
           (2)(3)
          (4)(5)(6)
        (7)(8)(9)(10)

        Position is a single number from 1 to 10.
        This needs to be converted to the x and y coordinates of the position.
        """
        mapping = {
            1: (1, 1),
            2: (2, 1),
            3: (2, 2),
            4: (3, 1),
            5: (3, 2),
            6: (3, 3),
            7: (4, 1),
            8: (4, 2),
            9: (4, 3),
            10: (4, 4)
        }
        self.position = mapping[self.index]
        self._init_xy_position()


class BeerPongCup(Position):
    """
    A class to represent a beer pong cup.

    Attributes:
    - Position: The position of the cup.
    - radius: The radius of the cup.
    - color: The color of the cup.
    """

    def __init__(self, index, position = (0, 0), radius = Radius, color = "red"):
        """
        Construct a new BeerPongCup object.

        Parameters:
        - position: The position of the cup.
        - radius: The radius of the cup (default: 1).
        - color: The color of the cup (default: "red").
        - phantom: True if the cup is a phantom cup, False otherwise (default: False).
        """
        super().__init__(index, position)
        self.radius = radius
        self.color = color
        self.phantom = False

    def plot(self, ax):
        """
        Plot the beer pong cup.

        Parameters:
        - ax: The axis to plot the cup on.
        """
        if self.phantom:
            circle = plt.Circle((self.x, self.y), self.radius, color="grey", fill=False, linestyle=':')
        else:
            circle = plt.Circle((self.x, self.y), self.radius, color=self.color, fill=False)
        ax.add_artist(circle)


class BeerPongConfig:
    """
    A class to represent a beer pong table.

    Attributes:
    - positions: A list of all positions on the table.
    - cups: A list of all cups on the table.
    """

    def __init__(self, title, indices = None, positions = None, phantoms = None):
        """
        Construct a new BeerPongTable object.

        Improvements:
        - Phantoms at other positions

        Parameters:
        - title: The title of the table.
        - indices: A list of indices on the table (default: None).
        - positions: A list of all positions on the table (default: None).
        - phantoms: A list of indices of the phantom cups on the table (default: None).
        """
        self.title = title
        self.cups = []

        if indices is not None:
            self.cups.extend(self._init_indices(indices))

        if positions is not None:
            self.cups.extend(self._init_positions(positions))
        
        if phantoms is not None:
            self.cups.extend(self._init_phantoms(phantoms))
        
        if indices is None and positions is None and phantoms is None:
            # Create cups (all cups are real cups by default)
            self.cups.extend(self._complete_table())

        if len(self.cups) == 0:
            print("Warning: No cups were created.")
        elif len(self.cups) > 10:
            print("Warning: More than 10 cups were created.")


    def _init_indices(self, indices):
        """
        Initialize the indices on the table.

        Parameters:
        - indices: A list of indices on the table.

        Returns:
        - A list of all positions on the table.
        """
        cups = []
        for index in indices:
            cups.append(BeerPongCup(index))
        return cups 

    def _init_positions(self, positions = None):
        """
        Create a list of all positions on the table.

        Returns:
        - A list of all positions on the table.
        """
        cups = []
        for x, y in positions:
            cups.append(BeerPongCup(-1, (x, y)))
        return cups
    
    def _init_phantoms(self, phantoms):
        """
        Initialize the phantom cups on the table.

        Parameters:
        - phantoms: A list of indices of the phantom cups on the table.

        Returns:
        - A list of all phantom cups on the table.
        """
        phantom_cups = []

        if isinstance(phantoms[0], int):
            for index in phantoms:
                cup = BeerPongCup(index)
                cup.phantom = True
                phantom_cups.append(cup)
        elif isinstance(phantoms[0], tuple):
            for x, y in phantoms:
                cup = BeerPongCup(-1, (x, y))
                cup.phantom = True
                phantom_cups.append(cup)
        else:
            raise ValueError("Phantoms must be a list of indices or a list of positions.")
        
        return phantom_cups

    def _complete_table(self):
        """
        Create a list of all indices on the table.

        Returns:
        - A list of all indices on the table.
        """
        cups = []
        for i in range(1, 11):
            cups.append(BeerPongCup(i))
        return cups

    def _plot(self):
        """
        Plot the beer pong table.
        """
        fig, ax = plt.subplots()
        ax.set_aspect('equal')

        # Set axis limits
        ax.set_xlim(-6, 6)
        ax.set_ylim(-8, Y_DIS*1.5)

        # disable numbers on axis
        ax.set_xticks([])
        ax.set_yticks([])

        # Plot cups
        for cup in self.cups:
            cup.plot(ax)

        # Triangle points
        triangle_points = [(-2.3*X_DIS, -3.5*Y_DIS), (0, Y_DIS*1.1), (2.3*X_DIS, -3.5*Y_DIS)]

        # Plot triangle
        triangle = plt.Polygon(triangle_points, closed=True, edgecolor='grey', fill=False, linestyle=':')
        ax.add_patch(triangle)

        # Add title
        plt.title(self.title)

        return fig, ax

    def plot(self):
        """
        Plot the beer pong table.
        """
        fig, ax = self._plot()
        plt.show()

    def save(self, directory):
        """
        Save the beer pong table to a file.

        Parameters:
        - filename: The filename to save the table to.
        """
        fig, ax = self._plot()
        plt.savefig(directory+self.title + ".png")


if __name__ == "__main__":

    directory = "./configs/"

    fullTable = BeerPongConfig(title="Full Table")
    fullTable.save(directory)

    emptyTable = BeerPongConfig(title="Empty Table", phantoms=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    emptyTable.save(directory)

    # Wenzent
    wenzent = BeerPongConfig(title="Wenzent", indices=[4, 5, 6, 8, 9])
    wenzent.save(directory)

    #       Index:
    #        (1)
    #       (2)(3)
    #      (4)(5)(6)
    #    (7)(8)(9)(10)
