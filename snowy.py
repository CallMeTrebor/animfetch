import subprocess
import time as t
import random
import sys


def create_snow_matrix(width, height, snowflakes=0.05):
    # Initialize matrix with empty spaces
    matrix = [[" " for _ in range(width)] for _ in range(height)]
    # Randomly place snowflakes in the top row
    for x in range(width):
        if random.random() < snowflakes:
            matrix[0][x] = "*"
    return matrix


def update_snow_matrix(matrix, width, height):
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
        if random.random() < 0.05:
            if matrix[0][x] == " ":
                matrix[0][x] = "*"
    return matrix


def print_matrix(matrix):
    for row in matrix:
        print("".join(row))


def main():
    # Parse command line arguments
    if len(sys.argv) != 4:
        print("Usage: python snowy.py <width> <height> <fps>")
        return
    width = int(sys.argv[1])
    height = int(sys.argv[2])
    fps = float(sys.argv[3])

    matrix = create_snow_matrix(width, height)
    is_tty = sys.stdout.isatty()
    while True:
        if is_tty:
            print("\033[H\033[J", end="")  # Clear screen if standalone
        print_matrix(matrix)
        print()  # Print a blank line as a frame separator
        matrix = update_snow_matrix(matrix, width, height)
        t.sleep(1 / fps)


if __name__ == "__main__":
    main()
