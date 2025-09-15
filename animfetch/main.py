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


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """Animfetch CLI"""
    # If no subcommand is provided, default to 'run'
    if ctx.invoked_subcommand is None:
        # Remove the first argument (the script/entry point)
        # and call run with default options
        # Use Click's Context to invoke the run command
        ctx.invoke(run)


@cli.command()
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
@click.option(
    "--calculate-frame-time",
    type=bool,
    default=False,
    is_flag=True,
    help="Calculate and display the time taken to render frames on average",
)
def run(fps, width, height, provider, fetch_command, calculate_frame_time):
    """Run the animation with the selected provider."""
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

    # Frame time measurement state
    total_render_time = 0.0
    frames_measured = 0
    last_render_time = None

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

            # Start render timer (exclude sleep, include frame generation, formatting, and printing)
            render_start = t.perf_counter()

            anim_frame = provider_instance.get_frame()
            if not anim_frame:
                break
            frame = format_frame(anim_frame, specs)
            print("\033[H\033[J", end="")
            print("\n".join(frame))

            # Stop render timer right after printing the frame
            render_time = t.perf_counter() - render_start
            total_render_time += render_time
            frames_measured += 1
            last_render_time = render_time

            # Optionally display frame timing stats (shown for the just-rendered frame)
            if calculate_frame_time and frames_measured > 0:
                avg_ms = (total_render_time / frames_measured) * 1000.0
                last_ms = (
                    last_render_time * 1000.0 if last_render_time is not None else 0.0
                )
                print(
                    f"[frame-time] last: {last_ms:.2f} ms | avg: {avg_ms:.2f} ms | frames: {frames_measured}"
                )
            t.sleep(max(0, frame_wait_time))


@cli.command()
def ls():
    """List all providers with their descriptions."""
    choices = get_provider_choices()
    click.echo("\n=== Provider List ===\n")
    for provider_name in choices:
        try:
            provider_module = __import__(
                f"animfetch.providers.{provider_name}", fromlist=["Provider"]
            )
            ProviderClass = getattr(
                provider_module, f"{provider_name.capitalize()}Provider"
            )
            desc = ProviderClass(1, 1, 1).get_description()
        except Exception as e:
            desc = f"(Error: {e})"
        click.echo(click.style(provider_name, bold=True) + f": {desc}")


if __name__ == "__main__":
    import sys

    # If no subcommand is provided, default to 'run'
    if len(sys.argv) == 1 or (len(sys.argv) > 1 and sys.argv[1] not in cli.commands):
        # Remove script name from argv and call run with remaining args
        sys.argv.insert(1, "run")
    cli()
