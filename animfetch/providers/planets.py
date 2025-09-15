from math import floor
import sys
import random

from animfetch.provider import Provider

# Prefer C++ implementation if present; fallback to Python reimplementation.
try:
    from animfetch.providers.source import planets_cpp as _cpp_mod  # type: ignore

    update_stars = _cpp_mod.update_stars  # type: ignore[assignment]
except Exception:  # pragma: no cover - optional accel

    def update_stars(frame, width, height, star_data, delta_time: float = 0):
        max_stars = floor((width * height) * 0.02)

        base_star_gen_rate = 0.07
        star_gen_chance = min(
            base_star_gen_rate * 1 / (delta_time + base_star_gen_rate), 1
        )
        if len(star_data) < max_stars and random.random() > star_gen_chance:
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            brightness = random.choice([".", "*", "+"])
            star_data.append((x, y, brightness))

        brighten_rate = 0.25
        dim_rate = 0.5
        brighten_chance = min(brighten_rate * delta_time, 1.0)
        dim_chance = min(dim_rate * delta_time, 1.0)

        new_star_data = []
        for data in star_data:
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

            if updated_data[2] != "!":
                new_star_data.append(updated_data)
                if 0 <= x < width and 0 <= y < height:
                    frame[y][x] = updated_data[2]
            else:
                if 0 <= x < width and 0 <= y < height:
                    frame[y][x] = " "

        return frame, new_star_data


def update_planets(frame, width, height, planet_data, delta_time: float = 0):
    return frame


def update_state(frame, width, height, star_data, planet_data, delta_time: float = 0):
    frame, star_data = update_stars(frame, width, height, star_data, delta_time)
    return (
        update_planets(
            frame,
            width,
            height,
            planet_data,
            delta_time,
        ),
        star_data,
    )


def render_frame(frame):
    return frame


class PlanetsProvider(Provider):

    def __init__(self, width, height, fps) -> None:
        super().__init__(width, height, fps)
        self.star_data = []
        self.planet_data = []

        self.frame = []
        self.is_tty = sys.stdout.isatty()

    def get_frame(self) -> list[str] | None:
        rendered_frame = render_frame(self.frame)
        return ["".join(line) for line in rendered_frame] + ["\n"]

    def update_state(self, delta_time: float = 0):
        self.frame = [[" " for _ in range(self.width)] for _ in range(self.height)]
        self.frame, self.star_data = update_state(
            self.frame,
            self.width,
            self.height,
            self.star_data,
            self.planet_data,
            delta_time,
        )

    def get_description(self) -> str:
        return "Planets animation with twinkling stars"
