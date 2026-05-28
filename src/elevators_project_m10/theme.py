from dataclasses import dataclass

Color = tuple[int, int, int]


@dataclass(frozen=True)
class Theme:
    screen_color: Color = (255, 255, 255)
    black_space_color: Color = (0, 0, 0)
    numbers_default_color: Color = (225, 0, 0)
    numbers_on_hold_color: Color = (255, 215, 0)
    button_default_color: Color = (128, 128, 128)
    button_on_hold_color: Color = (0, 128, 0)

    builder: int = -1
    order_completed: int = -1
    order: int = 0
