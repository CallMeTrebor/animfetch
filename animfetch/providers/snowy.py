import time as t
import random
import sys
from animfetch.provider import Provider
import argparse


def create_snow_matrix(width, height, snowflakes_chance=0.05):
    # Initialize matrix with empty spaces
    matrix = [[" " for _ in range(width)] for _ in range(height)]
    # Randomly place snowflakes in the top row
    for x in range(width):
        if random.random() < snowflakes_chance:
            matrix[0][x] = "*"
    return matrix


def update_snow_matrix(
    matrix, width, height, snowflakes_chance=0.05, should_update=True
):
    # Move snowflakes down by one row
    for y in range(height - 2, -1, -1):
        for x in range(width):
            if matrix[y][x] == "*":
                if matrix[y + 1][x] == " ":
                    matrix[y][x] = " "
                    matrix[y + 1][x] = "*"
                elif y + 1 == height - 1:
                    # Delete snowflake if it reaches the bottom
                    matrix[y][x] = " "
    # Remove snowflakes at the bottom row
    for x in range(width):
        if matrix[height - 1][x] == "*":
            matrix[height - 1][x] = " "
    # Add new snowflakes at the top
    for x in range(width):
        if random.random() < snowflakes_chance:
            if matrix[0][x] == " ":
                matrix[0][x] = "*"
    return matrix


class SnowyProvider(Provider):
    SNOWFLAKE_CHANCE = 0.05

    def __init__(self, width, height, fps) -> None:
        super().__init__(width, height, fps)
        self.matrix = create_snow_matrix(width, height, SnowyProvider.SNOWFLAKE_CHANCE)
        self.is_tty = sys.stdout.isatty()

    def get_frame(self) -> list[str] | None:
        self.matrix = update_snow_matrix(
            self.matrix,
            self.width,
            self.height,
            SnowyProvider.SNOWFLAKE_CHANCE,
        )
        return ["".join(row) for row in self.matrix] + ["\n"]

    def update_state(self, delta_time=0.0):
        pass

    def get_description(self) -> str:
        result = f"Snowy Animation: {self.width}x{self.height} at {self.fps} FPS"
        if not self.is_tty:
            result += " (not a TTY, clearing disabled)"
        return result
