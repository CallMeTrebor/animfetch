from abc import ABC, abstractmethod
import time as t


class Provider(ABC):
    def __init__(self, width, height, fps) -> None:
        super().__init__()
        self.width = width
        self.height = height
        self.fps = fps

    @abstractmethod
    def get_frame(self) -> list[str] | None:
        pass

    @abstractmethod
    def update_state(self, delta_time: float = 0):
        pass

    @abstractmethod
    def get_description(self) -> str:
        pass
