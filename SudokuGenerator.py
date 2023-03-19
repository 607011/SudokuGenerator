#!/usr/bin/env python3

import sys
import time
from datetime import datetime
import numpy as np
from numpy.random import MT19937, SeedSequence

class Sudoku:
    def __init__(self):
        self.board = np.zeros((9, 9), dtype=np.int8)
        self.rng = MT19937(SeedSequence(int(1e3*time.time())))
        for _ in range(1000): # warmup RNG
            self.rng.random_raw()

    def reset(self):
        self.board.fill(0)

    def to_text(self) -> str:
        result = ''
        for row in self.board:
            result += ''.join([str(x) for x in row]) + '\n'
        return result

    def to_svg(self) -> str:
        cell_size = 40
        stroke_color = '#222'
        padding = cell_size // 10
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{9 * cell_size + 2 * padding}" height="{9 * cell_size + 2 * padding}" version="1.1">\n'\
            f' <style>\n'\
            f' text {{\n'\
            f'  font-family: "Courier New", Courier, monospace;\n'\
            f'  font-size: {cell_size/1.618}px;\n'\
            f'  text-anchor: middle;\n'\
            f'  dominant-baseline: middle;\n'\
            f'  color: {stroke_color};\n'\
            f'}}\n'\
            f' </style>\n'\
            f' <g transform="translate({padding} {padding})" stroke="{stroke_color}">'\
            f'  <rect x="0" y="0" width="{9 * cell_size}" height="{9 * cell_size}" fill="white" />\n'
        for i in range(10):
            stroke_width = 2 if i % 3 == 0 else 0.5
            svg += f'  <line stroke-width="{stroke_width}" x1="{i * cell_size}" y1="0" x2="{i * cell_size}" y2="{9 * cell_size}"/>\n'\
                f'  <line stroke-width="{stroke_width}" x1="0" y1="{i * cell_size}" x2="{9 * cell_size}" y2="{i * cell_size}"/>\n'
        for row in range(9):
            for column in range(9):
                if self.board[row][column] != 0:
                    svg += f'  <text x="{(column + 0.5) * cell_size}" y="{(row + 0.5) * cell_size}">{self.board[row][column]}</text>\n'
        svg += ' </g>\n'\
            '</svg>\n'
        return svg


    def generate(self, difficulty, timeout=None):
        n_tries = 0
        while True:
            if timeout:
                if time.time() > timeout:
                    break 
            n_tries += 1
            print(f'\r{n_tries} ... ', end='', flush=True)
            n = 81 - self.min_empty_cells_for_difficulty(difficulty)
            while n > 0:
                row = self.rng.random_raw() % 9
                col = self.rng.random_raw() % 9
                num = 1 + self.rng.random_raw() % 9
                if self.number_is_valid(row, col, num):
                    self.board[row][col] = num
                    n -= 1
            solutions = [solution for solution in self.solve()]
            if len(solutions) == 1:
                print()
                return True
            self.reset()

        print("\rNo Sudoku found.", file=sys.stderr)
        return False

    # 1 = really easy, 3 = middle, 6 = devilish (lowest number possible, takes a long time to calculate)
    def min_empty_cells_for_difficulty(self, difficulty):
        empty_cells = [0, 25, 35, 45, 52, 58, 64]
        if difficulty < 1 or difficulty > len(empty_cells)-1:
            print("invalid difficulty", file=sys.stderr)
        return empty_cells[difficulty]


    # method to print the board in console
    def print(self):
        for i in range(9):
            print("".join([str(x) if x != 0 else "." for x in self.board[i]]))


    def number_is_valid(self, row, column, number):
        r = row - row % 3
        c = column - column % 3
        if np.any(self.board[:,column] == number) or \
            np.any(self.board[row,:] == number) or \
                np.any(self.board[r:r+3, c:c+3] == number):
            return False
        return True


    def solve(self):
        # find an empty cell
        for r in range(9):
            for c in range(9):
                if self.board[r][c] == 0:
                    # for every empty cell fill a valid number into it
                    for n in range(1, 10):
                        if self.number_is_valid(r, c, n):
                            self.board[r][c] = n
                            # is it solved?
                            yield from self.solve()
                            # backtrack
                            self.board[r][c] = 0
                    return False
        yield True


def main():
    args = [int(x) if x.isdecimal() else x for x in sys.argv[1:]]
    difficulty = args[0] if len(args) > 0 else 3
    loop_inifinitely = 'loop' in args
    sudoku = Sudoku()
    while True:
        ok = sudoku.generate(difficulty, timeout=None)
        if ok:
            print()
            sudoku.print()
            now = datetime.now()
            with open(f'sudoku-{now:%Y%m%dT%H%M%S}-{difficulty}.svg', 'w') as f:
                f.write(sudoku.to_svg())
            with open(f'sudoku-{now:%Y%m%dT%H%M%S}-{difficulty}.txt', 'w') as f:
                f.write(sudoku.to_text())
        if not loop_inifinitely:
            break
        sudoku.reset()


if __name__ == "__main__":
    main()
