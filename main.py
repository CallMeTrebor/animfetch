import subprocess
import time as t
import sys


def get_neofetch_data():
    neofetch_command = ["neofetch", "--off"]
    neofetch_data = subprocess.run(neofetch_command, capture_output=True, text=True)
    return neofetch_data.stdout.strip().splitlines()


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


def launch_frame_provider(script_name, params=[]):
    command = [sys.executable, script_name] + params
    process = subprocess.Popen(command, stdout=subprocess.PIPE, text=True)
    return process


def main():
    if len(sys.argv) < 3:
        print("Usage: python main.py <fps> <script> [script_args...]")
        sys.exit(1)
    try:
        fps = float(sys.argv[1])
    except ValueError:
        print("FPS must be a number.")
        sys.exit(1)
    specs = get_neofetch_data()
    script_name = sys.argv[2]
    params = sys.argv[3:]
    provider = launch_frame_provider(script_name, params)

    while True:
        anim_frame = get_frame(provider)
        if not anim_frame:
            break
        frame = format_frame(anim_frame, specs)
        print("\033[H\033[J", end="")
        print("\n".join(frame))
        time_to_wait = 1 / fps if fps > 0 else 0
        t.sleep(time_to_wait)


main()
