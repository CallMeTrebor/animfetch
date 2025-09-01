import subprocess
import time as t
import click
from animfetch.provider import Provider
import os


def get_fetch_data(fetch_command="fastfetch -l none --pipe false"):
    fetch_command_split = fetch_command.split(" ")
    fetch_data = subprocess.run(fetch_command_split, capture_output=True, text=True)
    result = fetch_data.stdout.strip().splitlines()
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


def get_provider_choices():
    providers_dir = os.path.join(os.path.dirname(__file__), "providers")
    choices = []
    for fname in os.listdir(providers_dir):
        if fname.endswith(".py") and not fname.startswith("__"):
            choices.append(fname[:-3])
    return choices


@click.command()
@click.option(
    "--fps", default=30, show_default=True, type=float, help="Frames per second"
)
@click.option(
    "--width", default=50, show_default=True, type=int, help="Width of the animation"
)
@click.option("--height", default=-1, type=int, help="Height of the animation")
@click.option(
    "--provider",
    default=get_provider_choices()[0],
    type=click.Choice(get_provider_choices(), case_sensitive=False),
    help="Animation provider to use",
)
@click.option(
    "--fetch-command",
    default="fastfetch -l none --pipe false",
    show_default=True,
    type=str,
    help="Command to fetch system information",
)
def cli(fps, width, height, provider, fetch_command):
    """Animfetch CLI using selected provider."""
    fps = constrain(fps, 0, 1000)
    specs = get_fetch_data(fetch_command)

    # Dynamically import the selected provider
    provider_module = __import__(
        f"animfetch.providers.{provider}", fromlist=["Provider"]
    )
    ProviderClass = getattr(provider_module, f"{provider.capitalize()}Provider")
    provider_instance: Provider = ProviderClass(
        width, len(specs) if height == -1 else height, fps
    )

    t0 = t.time()
    dt = 0.0
    frame_wait_time = 1 / fps
    fetch_wait_time = 5.0  # seconds
    while True:
        dt = t.time() - t0
        t0 = t.time()
        provider_instance.update_state(dt)

        fetch_wait_time -= dt
        if fetch_wait_time <= 0:
            fetch_wait_time = 5.0
            specs = get_fetch_data(fetch_command)

        frame_wait_time -= dt
        if frame_wait_time <= 0:
            frame_wait_time = 1 / fps

            anim_frame = provider_instance.get_frame()
            if not anim_frame:
                break
            frame = format_frame(anim_frame, specs)
            print("\033[H\033[J", end="")
            print("\n".join(frame))


if __name__ == "__main__":
    cli()
