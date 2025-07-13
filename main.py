import subprocess

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


def main():
    specs = get_neofetch_data()
    frame = get_anim_frame(1)

    for i in range(max(len(specs), len(frame))):
        spec_line = specs[i] if i < len(specs) else ""
        frame_line = frame[i] if i < len(frame) else " " * len(frame[-1])
        print(f"{frame_line}  {spec_line}")

main()
