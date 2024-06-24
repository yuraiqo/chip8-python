import sys
import pygame
from os.path import exists
from display import Display
from keyboard import Keyboard
from cpu import CPU


def main() -> None:
    rom = sys.argv[1]
    display = Display(10)
    keyboard = Keyboard()
    cpu = CPU(display, keyboard)

    if exists(rom):
        cpu.load_sprites()
        cpu.load_rom(rom)
    else:
        print("Provided ROM does not exist!")
        sys.exit()

    pygame.display.set_caption("Chip-8")
    clock = pygame.time.Clock()
    run = True

    while run:
        clock.tick(60)
        cpu.event_handler()
        cpu.cycle()


if __name__ == "__main__":
    main()
