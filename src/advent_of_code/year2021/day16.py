from abc import ABC
from math import prod

from advent_of_code.problems import MultiLineProblem


class Packet:
    def __init__(self, bits: str) -> None:
        self._bits = bits
        self.packets: list[Packet] = []
        self._version = int(bits[:3], 2)
        self._type_id = int(bits[3:6], 2)
        self._value = 0

    def parse(self) -> str:
        rest = self._bits[6:]

        if self._type_id == 4:
            n = ""
            while rest:
                keep_reading = int(rest[0], 2)
                n += rest[1:5]
                rest = rest[5:]
                if not keep_reading:
                    break
            self._value = int(n, 2)
            return rest

        length_type_id = int(rest[0], 2)
        if length_type_id:
            sub_packets_amount = int(rest[1:12], 2)
            rest = rest[12:]
            for _ in range(sub_packets_amount):
                packet = Packet(rest)
                rest = packet.parse()
                self.packets.append(packet)
            return rest

        sub_packets_length = int(rest[1:16], 2)
        rest = rest[16:]
        sub_packets = rest[:sub_packets_length]
        while sub_packets:
            packet = Packet(sub_packets)
            sub_packets = packet.parse()
            self.packets.append(packet)
        return rest[sub_packets_length:]

    @property
    def value(self) -> int:
        values = [p.value for p in self.packets]

        match self._type_id:
            case 0:
                result = sum(values)
            case 1:
                result = prod(values)
            case 2:
                result = min(values)
            case 3:
                result = max(values)
            case 4:
                result = self._value
            case 5:
                v1, v2 = values
                result = int(v1 > v2)
            case 6:
                v1, v2 = values
                result = int(v1 < v2)
            case 7:
                v1, v2 = values
                result = int(v1 == v2)
            case _:
                raise ValueError
        return result

    @property
    def version_sum(self) -> int:
        return self._version + sum(p.version_sum for p in self.packets)


class _Problem(MultiLineProblem[int], ABC):
    def __init__(self) -> None:
        self.packet = Packet("".join(f"{int(c, 16):04b}" for c in (self.lines[0])))
        self.packet.parse()


class Problem1(_Problem):
    def solution(self) -> int:
        return self.packet.version_sum


class Problem2(_Problem):
    def solution(self) -> int:
        return self.packet.value


TEST_INPUT = """
9C0141080250320F1802104A08
D2FE28
38006F45291200
EE00D40C823060
8A004A801A8002F478
620080001611562C8802118E34
C0015000016115A2E0802F182340
A0016C880162017C3686B18A3D4780
"""
