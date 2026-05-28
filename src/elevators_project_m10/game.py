import logging
import time

import pygame as pg

from .manager import Manager
from .media import MediaAssets
from .screen import ScreenLayout
from .settings import Settings
from .theme import Theme

logging.basicConfig(level=logging.INFO)


def run(
    settings: Settings | None = None,
    theme: Theme | None = None,
    elevators_numbers: int | None = None,
    floors_number: int | None = None,
) -> None:
    settings = settings or Settings()
    theme = theme or Theme()
    elevators_numbers = (
        elevators_numbers if elevators_numbers is not None else settings.elevators_count
    )
    floors_number = floors_number if floors_number is not None else settings.floors_count

    layout = ScreenLayout.from_building(settings, elevators_numbers, floors_number)
    screen = layout.create_display(theme)
    media = MediaAssets.load(settings)
    manager = Manager(
        settings, theme, media, layout, floors_number, elevators_numbers, screen
    )

    start_T = 0.0
    finish_T = 0.0
    finish = False
    while not finish:
        sleep_T = finish_T - start_T
        if (1 / settings.floor_height) > sleep_T:
            time.sleep(abs((1 / settings.floor_height) - sleep_T))
        start_T = time.time()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                finish = True
            manager.call(event, screen)

        manager.travels(screen)
        manager.update_arrival_time(manager, screen)
        manager.close_finish_orders()
        pg.display.flip()
        pg.time.Clock().tick(settings.floor_height * 4)
        finish_T = time.time()
