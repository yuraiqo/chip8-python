import pygame
import sys
from random import randint


class CPU:

    def __init__(self, display, keyboard) -> None:
        self.memory = bytearray(4096)

        self.v_regs = [0] * 16
        self.i_reg = 0
        self.pc = 0x200
        self.stack = []

        self.delay_timer = 0
        self.sound_timer = 0

        self.display = display
        self.keyboard = keyboard

        self.speed = 10

    def load_rom(self, path) -> None:
        with open(path, "rb") as binary:
            data = binary.read()
        for i in range(len(data)):
            self.memory[self.pc + i] = data[i]

    def load_sprites(self):
        sprites = [
            0xF0, 0x90, 0x90, 0x90, 0xF0,   # 0
            0x20, 0x60, 0x20, 0x20, 0x70,   # 1
            0xF0, 0x10, 0xF0, 0x80, 0xF0,   # 2
            0xF0, 0x10, 0xF0, 0x10, 0xF0,   # 3
            0x90, 0x90, 0xF0, 0x10, 0x10,   # 4
            0xF0, 0x80, 0xF0, 0x10, 0xF0,   # 5
            0xF0, 0x80, 0xF0, 0x90, 0xF0,   # 6
            0xF0, 0x10, 0x20, 0x40, 0x40,   # 7
            0xF0, 0x90, 0xF0, 0x90, 0xF0,   # 8
            0xF0, 0x90, 0xF0, 0x10, 0xF0,   # 9
            0xF0, 0x90, 0xF0, 0x90, 0x90,   # A
            0xE0, 0x90, 0xE0, 0x90, 0xE0,   # B
            0xF0, 0x80, 0x80, 0x80, 0xF0,   # C
            0xE0, 0x90, 0x90, 0x90, 0xE0,   # D
            0xF0, 0x80, 0xF0, 0x80, 0xF0,   # E
            0xF0, 0x80, 0xF0, 0x80, 0x80    # F
        ]
        for i, s in enumerate(sprites):
            self.memory[i] = s

    def cycle(self) -> None:
        for _ in range(self.speed):
            opcode = self.memory[self.pc] << 8 | self.memory[self.pc + 1]
            self.execute_instruction(opcode)
        self.update_timers()
        self.display.render()

    def update_timers(self) -> None:
        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            self.sound_timer -= 1

    def event_handler(self) -> None:
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    sys.exit()
                case pygame.KEYDOWN:
                    self.keyboard.key_down(event.key)
                case pygame.KEYUP:
                    self.keyboard.key_up(event.key)

    def draw(self, x, y, n) -> None:
        self.v_regs[0xF] = 0
        for i in range(n):
            sprite = self.memory[self.i_reg + i]
            for j in range(8):
                if sprite & 0x80:
                    if self.display.set_pixel(self.v_regs[x] + j,
                                              self.v_regs[y] + i):
                        self.v_regs[0xF] = 1
                sprite <<= 1

    def execute_instruction(self, opcode) -> None:
        self.pc += 2
        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4
        nnn = (opcode & 0x0FFF)
        kk = (opcode & 0x00FF)
        n = (opcode & 0x000F)
        op = (opcode & 0xF000)
        match op:
            case 0x0000:
                match opcode:
                    # clear display
                    case 0x00E0:
                        self.display.clear()
                    # return from subroutines
                    case 0x00EE:
                        self.pc = self.stack.pop()
            case 0x1000:
                # jump to location nnn
                self.pc = nnn
            case 0x2000:
                # call subroutine at nnn
                self.stack.append(self.pc)
                self.pc = nnn
            case 0x3000:
                # skip next instruction if Vx == kk
                if self.v_regs[x] == kk:
                    self.pc += 2
            case 0x4000:
                # skip next instruction if Vx != kk
                if self.v_regs[x] != kk:
                    self.pc += 2
            case 0x5000:
                # skip next instruction if Vx == Vy
                if self.v_regs[x] == self.v_regs[y]:
                    self.pc += 2
            case 0x6000:
                # set Vx to kk
                self.v_regs[x] = kk
            case 0x7000:
                # set Vx to Vx + kk
                self.v_regs[x] += kk
                self.v_regs[x] &= 0xFF
            case 0x8000:
                match n:
                    case 0x0:
                        # set Vx to Vy
                        self.v_regs[x] = self.v_regs[y]
                    case 0x1:
                        # set Vx to Vx OR Vy
                        self.v_regs[x] |= self.v_regs[y]
                    case 0x2:
                        # set Vx to Vx AND Vy
                        self.v_regs[x] &= self.v_regs[y]
                    case 0x3:
                        # set Vx to Vx XOR Vy
                        self.v_regs[x] ^= self.v_regs[y]
                    case 0x4:
                        # set Vx to Vx + Vy, set VF to carry
                        self.v_regs[x] += self.v_regs[y]
                        self.v_regs[0xF] = 0
                        if self.v_regs[x] > 0xFF:
                            self.v_regs[0xF] = 1
                        self.v_regs[x] &= 0xFF
                    case 0x5:
                        # set Vx to Vx - Vy, VF set to NOT borrow
                        self.v_regs[0xF] = 0
                        if self.v_regs[x] > self.v_regs[y]:
                            self.v_regs[0xF] = 1
                        self.v_regs[x] -= self.v_regs[y]
                        self.v_regs[x] &= 0xFF
                    case 0x6:
                        # set Vx to Vx SHR 1
                        self.v_regs[0xF] = self.v_regs[x] & 0x1
                        self.v_regs[x] >>= 1
                    case 0x7:
                        # set Vx to Vy - Vx, VF set to NOT borrow
                        self.v_regs[0xF] = 0
                        if self.v_regs[x] < self.v_regs[y]:
                            self.v_regs[0xF] = 1
                        self.v_regs[x] = self.v_regs[y] - self.v_regs[x]
                        self.v_regs[x] &= 0xFF
                    case 0xE:
                        # set Vx to Vx SHL 1
                        self.v_regs[0xF] = (self.v_regs[x] & 0x80) >> 7
                        self.v_regs[x] <<= 1
                        self.v_regs[x] &= 0xFF
            case 0x9000:
                # skip next instruction if Vx != Vy
                if self.v_regs[x] != self.v_regs[y]:
                    self.pc += 2
            case 0xA000:
                # set I to nnn
                self.i_reg = nnn
            case 0xB000:
                # jump to location nnn + V0
                self.pc = nnn + self.v_regs[0x0]
            case 0xC000:
                # set Vx to random byte AND kk
                self.v_regs[x] = randint(0, 255) & kk
            case 0xD000:
                # display n-byte sprite starting at
                # memory location I at (Vx, Vy), set VF to collision
                self.draw(x, y, n)
            case 0xE000:
                match kk:
                    case 0x9E:
                        # skip next instruction if key
                        # with value of Vx is pressed
                        if self.keyboard.is_key_pressed(self.v_regs[x]):
                            self.pc += 2
                    case 0xA1:
                        # skip next instructioin if key
                        # with value of Vx is not pressed
                        if not self.keyboard.is_key_pressed(self.v_regs[x]):
                            self.pc += 2
            case 0xF000:
                match kk:
                    case 0x07:
                        # set Vx to delay timer value
                        self.v_regs[x] = self.delay_timer
                    case 0x0A:
                        # wait for key press, store the value of the key in Vx
                        is_key_pressed = True
                        while is_key_pressed:
                            self.event_handler()
                            for i, k in enumerate(self.keyboard.key_pressed):
                                if k:
                                    self.v_regs[x] = i
                                    is_key_pressed = False
                                    break
                    case 0x15:
                        # set delay timer to Vx
                        self.delay_timer = self.v_regs[x]
                    case 0x18:
                        # set sound timer to Vx
                        self.sound_timer = self.v_regs[x]
                    case 0x1E:
                        # set I to I + Vx
                        self.i_reg += self.v_regs[x]
                    case 0x29:
                        # set I to location of sprite for digit Vx
                        self.i_reg = self.v_regs[x] * 5
                    case 0x33:
                        # store BCD representation of Vx in
                        # memory locations I, I+1, I+2
                        self.memory[self.i_reg] = self.v_regs[x] // 100
                        self.memory[self.i_reg + 1] = self.v_regs[x] % 100 // 10
                        self.memory[self.i_reg + 2] = self.v_regs[x] % 10
                    case 0x55:
                        # store registers V0 through Vx from memory
                        # starting at location I
                        for i in range(x + 1):
                            self.memory[self.i_reg + i] = self.v_regs[i]
                    case 0x65:
                        # read registers V0 through Vx from memory
                        # starting at location I
                        for i in range(x + 1):
                            self.v_regs[i] = self.memory[self.i_reg + i]
