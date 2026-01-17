from math import floor
import sys
import random

from animfetch.provider import Provider

from animfetch.providers.source import planets_cpp as _cpp_mod  # type: ignore

update_stars = _cpp_mod.update_stars  # type: ignore[assignment]
update_planets = _cpp_mod.update_planets  # type: ignore[assignment]
Planet = _cpp_mod.Planet  # type: ignore[assignment]
RGB = _cpp_mod.RGB  # type: ignore[assignment]


def update_state(frame, width, height, star_data, planet_data, delta_time: float = 0):
    frame, star_data = update_stars(frame, width, height, star_data, delta_time)
    frame, planet_data = update_planets(frame, width, height, planet_data, delta_time)

    # Build a map of planet positions to colors
    planet_colors = {}
    centerX = width // 2
    centerY = height // 2
    for planet in planet_data:
        x = centerX + round(planet.get_x())
        y = centerY + round(planet.get_y())
        if 0 <= x < width and 0 <= y < height:
            color = planet.get_color()
            planet_colors[(y, x)] = color

    return (frame, star_data, planet_data, planet_colors)


def render_frame(frame, planet_colors):
    colored_frame = []
    for y, row in enumerate(frame):
        colored_row = []
        for x, char in enumerate(row):
            if (y, x) in planet_colors:
                color = planet_colors[(y, x)]
                # Apply ANSI RGB color code
                colored_char = f"\033[38;2;{color.r};{color.g};{color.b}m{char}\033[0m"
                colored_row.append(colored_char)
            else:
                colored_row.append(char)
        colored_frame.append(colored_row)
    return colored_frame


class PlanetsProvider(Provider):

    def __init__(self, width, height, fps) -> None:
        super().__init__(width, height, fps)
        self.star_data = []
        sun = Planet(0.1, 0.0, "Sun", RGB(255, 255, 0))
        earth = Planet(2.0, 0.0, "Earth", RGB(0, 100, 255))
        self.planet_data = [sun, earth]
        self.planet_colors = {}

        self.frame = []
        self.is_tty = sys.stdout.isatty()

    def get_frame(self) -> list[str] | None:
        rendered_frame = render_frame(self.frame, self.planet_colors)
        return ["".join(line) for line in rendered_frame] + ["\n"]

    def update_state(self, delta_time: float = 0):
        self.frame = [[" " for _ in range(self.width)] for _ in range(self.height)]
        self.frame, self.star_data, self.planet_data, self.planet_colors = update_state(
            self.frame,
            self.width,
            self.height,
            self.star_data,
            self.planet_data,
            delta_time,
        )

    def get_description(self) -> str:
        return "Planets animation with twinkling stars"
