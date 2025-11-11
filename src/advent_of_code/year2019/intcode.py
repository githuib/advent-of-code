from abc import ABC
from enum import IntEnum
from typing import TYPE_CHECKING

from more_itertools import last

from advent_of_code.problems import OneLineProblem

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator


class ParamMode(IntEnum):
    POSITION = 0
    IMMEDIATE = 1
    RELATIVE = 2


class OpCode(IntEnum):
    ADD = 1
    MUL = 2
    IN = 3
    OUT = 4
    JT = 5
    JF = 6
    LT = 7
    EQ = 8
    REL = 9
    STOP = 99


class StopError(Exception):
    pass


instruction_lengths = {
    OpCode.ADD: 3,
    OpCode.MUL: 3,
    OpCode.IN: 1,
    OpCode.OUT: 1,
    OpCode.JT: 2,
    OpCode.JF: 2,
    OpCode.LT: 3,
    OpCode.EQ: 3,
    OpCode.REL: 1,
}


class IntcodeComputer:
    def __init__(self, program: Iterable[int]) -> None:
        self.program = list(program)
        self.memory: list[int] = []
        self.inputs: list[int] = []
        self._relative_base = 0

    @classmethod
    def from_str(cls, s: str) -> IntcodeComputer:
        return cls(int(c) for c in s.split(","))

    def __copy__(self) -> IntcodeComputer:
        return IntcodeComputer(self.program)

    def _read(self, address: int, param_mode: ParamMode) -> int:
        if param_mode == ParamMode.IMMEDIATE:
            return address
        if param_mode == ParamMode.RELATIVE:
            address = self._relative_base + address

        if address < 0:
            raise IndexError(address)

        try:
            return self.memory[address]
        except IndexError:
            return 0

    def _write(self, address: int, value: int, param_mode: ParamMode) -> None:
        if param_mode == ParamMode.IMMEDIATE:
            raise ValueError(param_mode)
        if param_mode == ParamMode.RELATIVE:
            address = self._relative_base + address

        if address < 0:
            raise IndexError(address)

        try:
            self.memory[address] = value
        except IndexError:
            # Extend memory so it can store the value at the given address.
            # Fill up the addresses in between with zeros.
            self.memory += [0] * (address - len(self.memory)) + [value]

    def _execute_next_instruction(self, ptr: int) -> tuple[int, int | None]:
        output = None
        op_code_str = f"{self.memory[ptr]:05d}"
        op_code = OpCode(int(op_code_str[-2:]))
        param_modes = [ParamMode(int(c)) for c in reversed(op_code_str[:-2])]

        if op_code == OpCode.STOP:
            raise StopError

        num_params = instruction_lengths[op_code]
        pointer = ptr + 1
        params = self.memory[pointer : pointer + num_params]

        if num_params == 1:
            param, *_ = params
            param_mode, *_ = param_modes

            if op_code == OpCode.IN:
                self._write(param, self.inputs.pop(0), param_mode)

            elif op_code == OpCode.OUT:
                output = self._read(param, param_mode)

            else:  # op_code == OpCode.REL
                self._relative_base += self._read(param, param_mode)

        elif num_params == 2:
            param, new_ip = params
            param_mode1, param_mode2, *_ = param_modes
            param = self._read(param, param_mode1)
            new_pointer = self._read(new_ip, param_mode2)

            if (op_code == OpCode.JT and param) or (op_code == OpCode.JF and not param):
                return new_pointer, output

        else:  # num_params == 3:
            op1, op2, to_address = params
            param_mode1, param_mode2, param_mode3 = param_modes
            op1 = self._read(op1, param_mode1)
            op2 = self._read(op2, param_mode2)

            self._write(
                to_address,
                {
                    OpCode.ADD: op1 + op2,
                    OpCode.MUL: op1 * op2,
                    OpCode.LT: int(op1 < op2),
                    OpCode.EQ: int(op1 == op2),
                }[OpCode(op_code)],
                param_mode3,
            )

        return pointer + num_params, output

    def run_to_next_output(self, *input_: int) -> Iterator[int]:
        self.inputs = list(input_)
        self.memory = self.program[:]

        pointer = 0
        while pointer < len(self.memory):
            try:
                pointer, output = self._execute_next_instruction(pointer)
            except StopError:
                break
            if output is None:
                continue
            yield output

    def run(self, *input_: int) -> int:
        return last(self.run_to_next_output(*input_), default=0)


class IntcodeProblem[T](OneLineProblem[T], ABC):
    computer: IntcodeComputer

    def process_input(self) -> None:
        super().process_input()
        self.computer = IntcodeComputer.from_str(self.line)
