import math
from math import floor
import sys
import time
import random


class State:
    def __init__(self):
        self.WIDTH = 80
        self.HEIGHT = 24
        self.FPS = 60
        self.STAR_DATA = []
        self.PLANET_DATA = []


STATE = State()


def update_planets(frame, delta_time=0):

    return frame


def update_stars(frame, delta_time=0):
    max_stars = floor((STATE.WIDTH * STATE.HEIGHT) * 0.02)

    # add stars if we have less than max_stars
    base_star_gen_rate = 0.07
    star_gen_chance = min(base_star_gen_rate * 1 / (delta_time + base_star_gen_rate), 1)
    if len(STATE.STAR_DATA) < max_stars and random.random() > star_gen_chance:
        x = random.randint(0, STATE.WIDTH - 1)
        y = random.randint(0, STATE.HEIGHT - 1)
        brightness = random.choice([".", "*", "+"])
        STATE.STAR_DATA.append((x, y, brightness))

    # update star states with delta_time-scaled probabilities
    # base rates: brighten 0.25/sec, dim 0.5/sec
    brighten_rate = 0.25
    dim_rate = 0.5
    brighten_chance = min(brighten_rate * delta_time, 1.0)
    dim_chance = min(dim_rate * delta_time, 1.0)

    new_star_data = []
    for data in STATE.STAR_DATA:
        rand_val = random.random()
        x, y, brightness = data
        updated_data = data
        if rand_val < brighten_chance:
            if brightness == ".":
                new_brightness = "*"
            elif brightness == "*":
                new_brightness = "+"
            else:
                new_brightness = "+"
            updated_data = (x, y, new_brightness)
        elif rand_val < brighten_chance + dim_chance:
            if brightness == "+":
                new_brightness = "*"
            elif brightness == "*":
                new_brightness = "."
            else:
                new_brightness = "!"
            updated_data = (x, y, new_brightness)

        # Only keep stars that are not "!"
        if updated_data[2] != "!":
            new_star_data.append(updated_data)
            if 0 <= x < STATE.WIDTH and 0 <= y < STATE.HEIGHT:
                frame[y][x] = updated_data[2]
        else:
            if 0 <= x < STATE.WIDTH and 0 <= y < STATE.HEIGHT:
                frame[y][x] = " "

    STATE.STAR_DATA = new_star_data
    return frame


def update_state(frame, delta_time=0):
    return update_planets(update_stars(frame, delta_time), delta_time)


def render_frame(frame):
    return [[char for char in line] for line in frame]


def parse_args():
    if len(sys.argv) > 2:
        try:
            STATE.WIDTH = int(sys.argv[1])
            STATE.HEIGHT = int(sys.argv[2])
        except ValueError:
            print("Width and height must be integers.")
            sys.exit(1)
    if len(sys.argv) > 3:
        try:
            STATE.FPS = float(sys.argv[3])
        except ValueError:
            print("FPS must be a number.")
            sys.exit(1)


def main():
    parse_args()
    t0 = time.time()
    is_tty = sys.stdout.isatty()
    while True:
        frame = [[" " for _ in range(STATE.WIDTH)] for _ in range(STATE.HEIGHT)]
        dt = time.time() - t0
        t0 = time.time()
        frame = update_state(frame, dt)
        rendered_frame = render_frame(frame)

        if is_tty:
            print("\033[H\033[J", end="")
        for line in rendered_frame:
            print("".join(line))
        print(flush=True)
        time.sleep(1 / STATE.FPS)


main()
