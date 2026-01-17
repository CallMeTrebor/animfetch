import math
import socket
import subprocess
import sys

from animfetch.provider import Provider

from animfetch.providers.source import planets_cpp as _cpp_mod  # type: ignore

update_stars = _cpp_mod.update_stars  # type: ignore[assignment]
update_planets = _cpp_mod.update_planets  # type: ignore[assignment]
Planet = _cpp_mod.Planet  # type: ignore[assignment]
RGB = _cpp_mod.RGB  # type: ignore[assignment]

# Horizontal stretch factor to compensate for tall terminal characters
ASPECT_RATIO = 2.0


connection_time_passed = 5.0  # Start at 5.0 to check immediately
connection_status = False

vpn_check_time_passed = 5.0  # Check VPN status every second
vpn_status = False


def is_connected_to_vpn(delta_time: float = 0) -> bool:
    """Check if connected to a VPN by looking for VPN network interfaces."""
    global vpn_check_time_passed, vpn_status

    vpn_check_time_passed += delta_time
    if vpn_check_time_passed < 1.0:
        return vpn_status
    vpn_check_time_passed = 0.0

    try:
        # Check for common VPN interface names
        result = subprocess.run(
            ["ip", "link", "show"], capture_output=True, text=True, timeout=0.1
        )
        output = result.stdout.lower()

        # Common VPN interface names
        vpn_interfaces = ["tun", "tap", "wg", "ppp", "vpn"]
        vpn_status = any(interface in output for interface in vpn_interfaces)
        return vpn_status
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        vpn_status = False
        return False


def is_connected_to_network(delta_time: float = 0) -> bool:
    global connection_time_passed, connection_status

    connection_time_passed += delta_time
    if connection_time_passed < 1.0:  # Check every second (more responsive)
        return connection_status
    connection_time_passed = 0.0

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(0.05)  # Faster timeout
        sock.connect(("8.8.8.8", 80))
        sock.close()
        connection_status = True
        return True
    except (OSError, socket.error):
        connection_status = False
        return False


def update_state(
    frame,
    width,
    height,
    star_data,
    planet_data,
    delta_time: float = 0,
    generate_stars: bool = True,
):
    frame, star_data = update_stars(
        frame, width, height, star_data, delta_time, generate_stars
    )
    frame, planet_data = update_planets(
        frame, width, height, planet_data, delta_time, ASPECT_RATIO
    )

    # Build a map of positions to colors (paths and planets)
    color_map = {}
    centerX = width // 2
    centerY = height // 2

    # First add path colors (will be overwritten by planet positions)
    for planet in planet_data:
        if planet.get_show_path() and planet.get_radius() >= 0.5:
            radius = planet.get_radius()
            path_color = planet.get_path_color()
            num_points = max(
                16, int(math.ceil(2.0 * math.pi * radius * ASPECT_RATIO * 2.0))
            )
            for i in range(num_points):
                angle = (2.0 * math.pi * i) / num_points
                x = centerX + round(radius * math.cos(angle) * ASPECT_RATIO)
                y = centerY + round(radius * math.sin(angle))
                if 0 <= x < width and 0 <= y < height:
                    color_map[(y, x)] = path_color

    # Then add planet colors (overwrite path positions where planets are)
    for planet in planet_data:
        x = centerX + round(planet.get_x() * ASPECT_RATIO)
        y = centerY + round(planet.get_y())
        if 0 <= x < width and 0 <= y < height:
            color = planet.get_color()
            color_map[(y, x)] = color

    return (frame, star_data, planet_data, color_map)


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
        self.sun = Planet(0.1, 0.0, "Sun", RGB(255, 255, 0), False, True)
        self.earth = Planet(3.0, 0.0, "Earth", RGB(0, 100, 255))
        self.mars = Planet(6.0, math.pi / 4, "Mars", RGB(255, 50, 0))
        self.tunnel_planet = Planet(
            12, 1.25 * math.pi, "TunnelPlanet", RGB(150, 150, 0), False, True
        )
        self.planet_data = [self.sun, self.earth, self.mars]
        self.planet_colors = {}

        self.frame = []
        self.is_tty = sys.stdout.isatty()

    def get_frame(self) -> list[str] | None:
        rendered_frame = render_frame(self.frame, self.planet_colors)
        return ["".join(line) for line in rendered_frame] + ["\n"]

    def update_state(self, delta_time: float = 0):
        generate_stars = is_connected_to_network(delta_time)

        vpn_connected = is_connected_to_vpn(delta_time)
        has_tunnel = self.tunnel_planet in self.planet_data
        if vpn_connected and not has_tunnel:
            self.planet_data.append(self.tunnel_planet)
        elif not vpn_connected and has_tunnel:
            self.planet_data.remove(self.tunnel_planet)

        self.frame = [[" " for _ in range(self.width)] for _ in range(self.height)]
        self.frame, self.star_data, self.planet_data, self.planet_colors = update_state(
            self.frame,
            self.width,
            self.height,
            self.star_data,
            self.planet_data,
            delta_time,
            generate_stars,
        )

    def get_description(self) -> str:
        return "Planets animation with twinkling stars"
