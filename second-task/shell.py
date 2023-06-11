import io
import sys
import re
from typing import TextIO
from types import CodeType

from lexer import lexer_lines
from shell_parser import Parser

def exec_shell_code(code_obj: CodeType, default_input: TextIO, default_output: TextIO):
    import shell_namespace                                              ## 💀💀💀💀💀
    from shell_namespace import pwd, cd, mkdir, ls, cat, tac, grep      ## 💀💀💀💀💀
    exec(code_obj, locals())

def solution(default_input: TextIO, default_output: TextIO) -> None:
    lexer = lexer_lines(default_input)

    parser = Parser()

    for tokens_line in lexer:
        exec_shell_code(
            parser.get_code_obj(tokens_line), 
            default_input, 
            default_output
        )

if __name__ == '__main__':
    solution(sys.stdin, sys.stdout)