import os, re
from pathlib import Path
from functools import partial
from typing import Tuple, List, Dict, Optional, Callable, Iterator, TextIO

current_input_stream: Optional[TextIO] = None
output_stream: Optional[TextIO] = None

def _iter_counter(i: Iterator):
    return sum(1 for _ in i)

class _BasicCommand:
    def _parse_args(args: List[str]) -> Tuple[List[str], Dict[str, Optional[str]]]:
        pos_args = []
        flag_args = dict()
        for a in args:
            if a.startswith("-"):
                flag_args[a.lstrip("-")] = None
                continue
            pos_args.append(a)
        return pos_args, flag_args
    ## if you need more complex arg parsing, you can just
    ## inherit from Command class and override _parse_args method

    def __init__(self, func: Callable):
        self.func = func

    def __call__(self, args: List[str]):

        pos_args, flag_args = _BasicCommand._parse_args(args)
        return self.func(pos_args, flag_args)

def _pwd(pos_args: List[str], flag_args: Dict[str, Optional[str]]) -> str:
    return os.getcwd()
pwd = _BasicCommand(_pwd)

def _cd(pos_args: List[str], flag_args: Dict[str, Optional[str]]) -> str:
    dir_path = Path(pos_args[0])
    os.chdir(dir_path if dir_path.is_dir() else ".")
    return ""
cd = _BasicCommand(_cd)

def _mkdir(pos_args: List[str], flag_args: Dict[str, Optional[str]]) -> str:
    dir_path = Path(pos_args[0])
    if not dir_path.is_dir():
        os.mkdir(dir_path)
        return ""
    return f"cannot create directory {pos_args[0]}: file exists\n"
mkdir = _BasicCommand(_mkdir)

def _ls(pos_args: List[str], flag_args: Dict[str, Optional[str]]) -> str:
    return " ".join(
        sorted(
            os.listdir(Path(pos_args[0]) if pos_args else os.getcwd())
        )
    ) + "\n"
ls = _BasicCommand(_ls)


def _cat(_step: int, pos_args: List[str], flag_args: Dict[str, Optional[str]]) -> str:
    def _read_stream(stream: TextIO):
        return "".join(stream.readlines()[::_step])

    def _read_file(filename: str) -> str:
        with open(filename, "r") as file:
            return _read_stream(file)

    return ("".join((_read_file(filename) for filename in pos_args[::_step])) 
                if pos_args else _read_stream(current_input_stream))

cat = _BasicCommand(partial(_cat, 1))
tac = _BasicCommand(partial(_cat, -1))

def _grep(pos_args: List[str], flag_args: Dict[str, Optional[str]]) -> str:
    def _stream_iter(stream: TextIO) -> Iterator[str]:
        for line in stream:
            if re.search(pattern, line):
                yield line

    def _file_iter(file_path: Path) -> Iterator[str]:
        with open(file_path, "r") as file_stream:
            yield from _stream_iter(file_stream)

    def _dir_iter(dir_path: Path) -> Iterator[Tuple[str, Iterator[str]]]:
        for current_dir, _, dir_files in os.walk(dir_path):
            dir_path = Path(current_dir)
            for current_file in sorted(dir_files):
                file_path = dir_path/current_file
                yield str(file_path), _file_iter(file_path)

    pattern, file_path = re.compile(pos_args[0]), Path(pos_args[1] if len(pos_args) > 1 else ".")

    if "r" in flag_args and file_path.is_dir():
        return "".join(
            "".join(
                f"{filename}:{line}" 
                for line in (line_iter if "c" not in flag_args else [str(_iter_counter(line_iter)) + "\n"])
            )
            for filename, line_iter in _dir_iter(file_path)
        )
    
    matches_iter = _file_iter(file_path) if file_path.is_file() else _stream_iter(current_input_stream)

    return "".join(matches_iter) if "c" not in flag_args else str(_iter_counter(matches_iter)) + '\n'
grep = _BasicCommand(_grep)