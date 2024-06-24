import pygame
from random import randint


class CPU:

    def __init__(self) -> None:
        self.memory = bytearray(4096)

        self.v_regs = [0] * 16
        self.i_reg = 0
        self.pc = 0x200
        self.stack = []

        self.delay_timer = 0
        self.sound_timer = 0

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
            self.memory[0x50 + i] = s

    def cycle(self) -> None:
        for i in range(self.speed):
            opcode = self.memory[self.pc] << 8 | self.memory[self.pc + 1]
            self.execute_instruction(opcode)
        self.update_timers()
        self.display.render()

    def update_timers(self) -> None:
        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            self.sound_timer -= 1

    def execute_instruction(self, opcode) -> None:
        self.pc += 2
        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4
        nnn = (opcode & 0x0FFF)
        kk = (opcode & 0x00FF)
        n = (opcode & 0x000F)
        op = (opcode & 0xF000)
        match op:
            case 0x0:
                match opcode:
                    # clear display
                    case 0x00E0:
                        self.display.clear()
                    # return from subroutines
                    case 0x000E:
                        self.pc = self.stack.pop()
            case 0x1:
                # jump to location nnn
                self.pc = nnn
            case 0x2:
                # call subroutine at nnn
                self.stack.append(self.pc)
                self.pc = nnn
            case 0x3:
                # skip next instruction if Vx == kk
                if self.v_regs[x] == kk:
                    self.pc += 2
            case 0x4:
                # skip next instruction if Vx != kk
                if self.v_regs[x] != kk:
                    self.pc += 2
            case 0x5:
                # skip next instruction if Vx == Vy
                if self.v_regs[x] == self.v_regs[y]:
                    self.pc += 2
            case 0x6:
                # set Vx to kk
                self.v_regs[x] = kk
            case 0x7:
                # set Vx to Vx + kk
                self.v_regs[x] += kk
                self.v_regs[x] &= 0xFF
            case 0x8:
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
                        self.v[0xF] = 0
                        if self.v_regs[x] > 0xFF:
                            self.v[0xF] = 1
                        self.v_regs[x] &= 0xFF