from abc import ABC

from advent_of_code.problems import MultiLineProblem


class Dir:
    _parent: Dir

    def __init__(self) -> None:
        self._subdirs: dict[str, Dir] = {}
        self._size_of_files: int = 0

    @property
    def size(self) -> int:
        return (
            sum(subdir.size for subdir in self._subdirs.values()) + self._size_of_files
        )

    def add_dir(self, name: str) -> None:
        self._subdirs[name] = SubDir(self)

    def add_file_size(self, size: int) -> None:
        self._size_of_files += size

    def change_dir(self, dest_dir: str) -> Dir:
        if dest_dir == "..":
            return self._parent
        return self._subdirs[dest_dir]

    def total_size_1(self) -> int:
        n = sum(subdir.total_size_1() for subdir in self._subdirs.values())
        if self.size <= 100000:
            n += self.size
        return n

    def total_size_2(self, min_size: int) -> int | None:
        if self.size < min_size:
            return None
        return min(
            [self.size]
            + [
                min_subdir_size
                for subdir in self._subdirs.values()
                if (min_subdir_size := subdir.total_size_2(min_size)) is not None
            ]
        )


class SubDir(Dir):
    def __init__(self, parent: Dir):
        super().__init__()
        self._parent = parent


class Root(Dir):
    def __init__(self):
        super().__init__()
        self.add_dir("/")


class _Problem(MultiLineProblem[int], ABC):
    def __init__(self):
        self._root = Root()
        self._current_dir = self._root
        for line in self.lines:
            if line.startswith("$"):
                command = line[2:]
                if command == "ls":
                    continue
                self._current_dir = self._current_dir.change_dir(command[3:])
            else:
                first, name = line.split()
                try:
                    self._current_dir.add_file_size(int(first))
                except ValueError:
                    self._current_dir.add_dir(name)


class Problem1(_Problem):
    test_solution = 95437
    my_solution = 1182909

    def solution(self) -> int:
        return self._root.total_size_1()


class Problem2(_Problem):
    test_solution = 24933642
    my_solution = 2832508

    def solution(self) -> int:
        return self._root.total_size_2(self._root.size - 40000000)


TEST_INPUT = """
$ cd /
$ ls
dir a
14848514 b.txt
8504156 c.dat
dir d
$ cd a
$ ls
dir e
29116 f
2557 g
62596 h.lst
$ cd e
$ ls
584 i
$ cd ..
$ cd ..
$ cd d
$ ls
4060174 j
8033020 d.log
5626152 d.ext
7214296 k
"""
