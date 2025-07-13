import subprocess
import time as t

def get_neofetch_data():
    neofetch_command = ["neofetch", "--off"]
    neofetch_data = subprocess.run(neofetch_command, capture_output=True, text=True)
    return neofetch_data.stdout.strip().splitlines()

def get_anim_frame(index):
    path = f"./anim/{index}.txt"
    content = ""
    with open(path, 'r') as file:
        content = file.read()
    lines = content.splitlines()
    longest_line_length = max([len(line) for line in lines])
    lines = [line.ljust(longest_line_length) for line in lines]
    return lines

def get_anim_frames(lower, upper):
    frames = []
    for i in range(lower, upper + 1):
        frames.append(get_anim_frame(i))
    return frames

def get_full_frames(anim_frames, specs):
    longest_line_length = max([len(line) for frame in anim_frames for line in frame])
    frames = []
    for anim_frame in anim_frames:
        # padd the frame if needed
        anim_frame = [line.ljust(longest_line_length) for line in anim_frame]
        frame = []
        for i in range(max(len(anim_frame), len(specs))):
            anim_line = anim_frame[i] if i < len(anim_frame) else " " * longest_line_length
            spec_line = specs[i] if i < len(specs) else " " * longest_line_length
            frame.append(anim_line + "  " + spec_line)

        frames.append(frame)

    return frames

def main():
    frames = get_full_frames(get_anim_frames(1, 2), get_neofetch_data())

    fps = 2
    time = None
    frame_num = len(frames)
    current_frame = 0
    while True:
        # clear the screen
        print("\033[H\033[J", end="")
        print("\n".join(frames[current_frame]))
        current_frame = (current_frame + 1) % frame_num
        t.sleep(1 / fps)

main()
