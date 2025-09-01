# animfetch

Animated system info fetcher with a simple CLI and pluggable providers.

A small terminal utility that renders simple ASCII animations alongside system information (fetched via a command such as `fastfetch`). Built to be extended with custom animation providers.

## Features

- Small CLI using Click
- Pluggable providers: drop a Python file in the `providers/` folder
- Default providers included: `snowy`, `planets`
- Uses a system-info command (default: `fastfetch`) to show live specs next to the animation

## Installation

Clone the repository and install with pipx (recommended):

```bash
git clone https://github.com/CallMeTrebor/animfetch.git
cd animfetch
pipx install .
```

Alternatively, install locally with pip:

```bash
python -m pip install .
```

After installation, the `animfetch` command will be available.

## Usage

Show the available providers:

```bash
animfetch ls
```

Run the default animation (runs `run` by default):

```bash
animfetch run
```

Run with a specific provider and options:

```bash
animfetch run --provider snowy --fps 20 --width 80
```

Change the system-info command (default is `fastfetch -l none --pipe false`):

```bash
animfetch run --fetch-command "neofetch --off"
```

## Creating your own provider

Drop a `.py` file in the `providers/` folder (for example, `providers/myprovider.py`).

Your provider must implement the `Provider` interface defined in `animfetch/provider.py`. In short, implement a class named `<filename.capitalize()>Provider` that subclasses `Provider` and implements these methods:

- `get_frame(self) -> list[str] | None` — return the next frame as a list of strings (one string per row). Return `None` or an empty value to stop the animation.
- `update_state(self, delta_time: float = 0)` — update internal animation state (called every loop with the elapsed time)
- `get_description(self) -> str` — short description used by `animfetch ls`

Minimal example skeleton (put this in `providers/myprovider.py`):

```python
from animfetch.provider import Provider


class MyproviderProvider(Provider):
    def __init__(self, width, height, fps):
        super().__init__(width, height, fps)
        # init your state here

    def get_frame(self) -> list[str] | None:
        # return a list of strings (rows) representing the frame
        matrix = [" " * self.width for _ in range(self.height)] + ["\n"]
        matrix[len(matrix) // 2] = "Hello, World!".center(self.width)
        return matrix

    def update_state(self, delta_time: float = 0):
        # advance animation state, physics, etc.
        pass

    def get_description(self) -> str:
        return "My custom example provider"

```

That's it — the CLI will discover the new file automatically and list it via `animfetch ls`.

## Notes

- The CLI defaults to using `fastfetch` to fetch system specs. If you don't have `fastfetch`, either install it or pass another command via `--fetch-command`.
- Providers should be named with a `.py` filename and not start with `__` to be auto-discovered.
- For the time being, the tool was extensively tested only on Linux. If you encounter any problems, feel free to open an issue.

## Contributing

Before contributing, please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening pull requests.
