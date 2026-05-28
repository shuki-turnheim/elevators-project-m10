from __future__ import annotations

import time

import pygame as pg

from .elevator import Elevator
from .floor import Floor
from .media import MediaAssets
from .screen import ScreenLayout
from .settings import Settings
from .theme import Theme


class Manager:
    def __init__(
        self,
        settings: Settings,
        theme: Theme,
        media: MediaAssets,
        layout: ScreenLayout,
        floors_number: int,
        elevators_numbers: int,
        screen: pg.Surface,
    ):
        self._settings = settings
        self._theme = theme
        self._media = media
        self._layout = layout
        self.__elevators: list[Elevator] = []
        self.__floors: list[Floor] = []
        self.elevators_builder(elevators_numbers, screen)
        self.floors_builder(floors_number, screen)

    def elevators_builder(self, elevators_num: int, screen: pg.Surface) -> None:
        for num_elevator in range(elevators_num):
            elevator = Elevator(
                num_elevator, self._settings, self._theme, self._media, self._layout
            )
            elevator.build_elevator(num_elevator, screen)
            self.__elevators.append(elevator)

    def floors_builder(self, num_floors: int, screen: pg.Surface) -> None:
        for num_floor in range(num_floors):
            floor = Floor(num_floor, self._settings, self._theme, self._media, self._layout)
            floor.build_floor(num_floor, screen)
            self.__floors.append(floor)

    def elevator_selection(self, floor: Floor, screen: pg.Surface) -> None:
        dst = floor.number
        min_arrival_time = float("inf")
        priority_elevator = self.__elevators[0]
        for elevator in self.__elevators:
            arrival_time = elevator.arrival_time(dst)
            if min_arrival_time > arrival_time:
                min_arrival_time = arrival_time
                priority_elevator = elevator
        floor.request_in_process(min_arrival_time, screen)
        priority_elevator.send_order(dst)

    def call(self, event: pg.event.Event, screen: pg.Surface) -> None:
        left = 1
        if event.type == pg.MOUSEBUTTONDOWN and event.button == left:
            mouse_position = pg.mouse.get_pos()
            x1, y1 = mouse_position
            for floor in self.__floors:
                x2, y2 = floor.button
                if (x1 - x2) ** 2 + (y1 - y2) ** 2 <= floor.button_radius**2 and not floor.made_order:
                    elevator_at_floor = []
                    for elevator in self.__elevators:
                        elevator_at_floor.append(elevator.current_location)
                        if floor.permission_checker(elevator_at_floor):
                            self.elevator_selection(floor, screen)

    def update_arrival_time(self, manager: Manager, screen: pg.Surface) -> None:
        for floor in manager.__floors:
            floor.display_clock(screen)

    def travels(self, screen: pg.Surface) -> None:
        for elevator in self.__elevators:
            if elevator.in_travel:
                dest = self.__floors[elevator.dst]
                dest_y = dest.get_roof_position()
                elevator.travel(dest_y, screen)

    def close_finish_orders(self) -> None:
        current_time = time.time()
        for elevator in self.__elevators:
            dest = self.__floors[elevator.dst]
            dest_y = dest.get_roof_position()
            elevator.finish_order(dest_y, current_time)
