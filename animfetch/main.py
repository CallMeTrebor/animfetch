import subprocess
import time as t
import sys
import os
import click

try:
    from animfetch.provider import Provider
    from animfetch.providers.snowy import SnowyProvider
except ImportError:
    # Allow running as script from project root
    from provider import Provider
    from providers.snowy import SnowyProvider


def get_fast_fetch_data():
    fast_fetch_command = ["fastfetch", "-l", "none", "--pipe", "false"]
    fast_fetch_data = subprocess.run(fast_fetch_command, capture_output=True, text=True)
    result = fast_fetch_data.stdout.strip().splitlines()
    return result


def format_frame(anim_frame, specs):
    line_length = max([len(line) for line in anim_frame])
    anim_frame = [line.center(line_length) for line in anim_frame]
    frame = []
    for i in range(max(len(anim_frame), len(specs))):
        anim_line = anim_frame[i] if i < len(anim_frame) else " " * line_length
        spec_line = specs[i] if i < len(specs) else " " * line_length
        frame.append(anim_line + "  " + spec_line)
    return frame


def get_frame(provider):
    if provider and provider.poll() is None:
        lines = []
        while True:
            line = provider.stdout.readline()
            if not line or line.rstrip("\n") == "":
                break
            lines.append(line.rstrip("\n"))
        return lines if lines else None
    return None


def constrain(value, min_value, max_value):
    return max(min_value, min(max_value, value))


@click.command()
@click.option(
    "--fps", default=30, show_default=True, type=float, help="Frames per second"
)
def cli(fps):
    """Animfetch CLI using SnowyProvider."""
    fps = constrain(fps, 0, 1000)
    specs = get_fast_fetch_data()
    provider: Provider = SnowyProvider(50, len(specs), fps)

    t0 = t.time()
    dt = 0.0
    time_to_wait = 1 / fps
    while True:
        dt = t.time() - t0
        t0 = t.time()
        provider.update_state(dt)

        time_to_wait -= dt
        if time_to_wait <= 0:
            time_to_wait = 1 / fps

            anim_frame = provider.get_frame()
            if not anim_frame:
                break
            frame = format_frame(anim_frame, specs)
            print("\033[H\033[J", end="")
            print("\n".join(frame))


if __name__ == "__main__":
    cli()
