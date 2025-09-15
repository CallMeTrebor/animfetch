from math import floor
import sys
import random

from animfetch.provider import Provider

from animfetch.providers.source import planets_cpp as _cpp_mod  # type: ignore

update_stars = _cpp_mod.update_stars  # type: ignore[assignment]
update_planets = _cpp_mod.update_planets  # type: ignore[assignment]


def update_state(frame, width, height, star_data, planet_data, delta_time: float = 0):
    frame, star_data = update_stars(frame, width, height, star_data, delta_time)
    frame, planet_data = update_planets(frame, width, height, planet_data, delta_time)
    return (frame, star_data, planet_data)


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
        self.frame, self.star_data, self.planet_data = update_state(
            self.frame,
            self.width,
            self.height,
            self.star_data,
            self.planet_data,
            delta_time,
        )

    def get_description(self) -> str:
        return "Planets animation with twinkling stars"
