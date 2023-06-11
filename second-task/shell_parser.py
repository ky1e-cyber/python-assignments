import ast
from dataclasses import dataclass
from textwrap import indent
from typing import List, Set, Optional, Iterator
from lexer import TokenType, Token
from types import CodeType

@dataclass
class Command:
    name: str
    args: List[str]

@dataclass
class RedirectTable:
    inp: Optional[str]
    output: Optional[str]
    output_mode: str

@dataclass
class CommandArray:
    commands: List[Command]
    redirect_table: RedirectTable

class Parser:
    def __init__(self):
        self.current_token: Optional[str] = None

    def _parse(self, tokens_iter) -> Iterator[CommandArray]:

        def _match(types: Set[TokenType]) -> bool:
            return self.current_token.token_type in types
        
        def _command_name() -> str:
            if _match({TokenType.WORD}):
                name: str = self.current_token.literal
                self.current_token = next(tokens_iter)
                return name
            ## TODO RAISE SYNTAX ERROR smh

        def _command() -> Command:
            cmd_name: str = _command_name()
            cmd = Command(cmd_name, [])
            while _match({TokenType.WORD}):
                cmd.args.append(self.current_token.literal)
                self.current_token = next(tokens_iter)
            return cmd

        def _redirect() -> (TokenType, str):
            red_type = self.current_token.token_type
            self.current_token = next(tokens_iter)
            if _match({TokenType.WORD}):
                file_name = self.current_token.literal
                self.current_token = next(tokens_iter)
                return red_type, file_name
        ## TODO RAISE SYNTAX ERROR

        def _command_arr() -> CommandArray:
            _redirect_tokens_map = {
                TokenType.REDOUT: "w",
                TokenType.DOUBLE_REDOUT: "a" 
            }

            cmd_arr = CommandArray([_command()], RedirectTable(None, None, 'w'))

            while _match({TokenType.PIPE}):
                self.current_token = next(tokens_iter)
                cmd_arr.commands.append(_command())

            while _match({TokenType.REDIN, TokenType.REDOUT, TokenType.DOUBLE_REDOUT}):
                red_token, file_name = _redirect()
                if red_token == TokenType.REDIN:
                    cmd_arr.redirect_table.inp = file_name
                else:
                    cmd_arr.redirect_table.output = file_name
                    cmd_arr.redirect_table.output_mode = _redirect_tokens_map[red_token]
            return cmd_arr

        self.current_token = next(tokens_iter)

        yield _command_arr()
        while not _match({TokenType.EOS}):
            if _match({TokenType.SEMICOLON, TokenType.NEWLINE}):
                self.current_token = next(tokens_iter)
                continue
            yield _command_arr()

        self.current_token = None
        ## TODO RAISE SYNTAX ERROR 

    def get_ast(self) -> ast.Module:
        pass
        ## TODO

    def get_code_obj(self, tokens: List[Token]) -> CodeType:
        def _parse_cmd(cmd: Command) -> str:
            return f"{cmd.name}({cmd.args})"
            ##return f"{cmd.name}(" + ", ".join(f'"{arg}"' for arg in cmd.args) + ")"


        def _get_code_blocks() -> Iterator[str]:
            for cmd_array in self._parse(tokens_iter):

                code_block: str = f"res: str = {_parse_cmd(cmd_array.commands[-1])}\n" + \
                     f"print(res, end='', file=shell_namespace.output_stream)\n"  

                for cmd in reversed(cmd_array.commands[:-1:]):
                    code_block = f"with io.StringIO({_parse_cmd(cmd)}) as shell_namespace.current_input_stream:\n" + \
                                    indent(code_block, "\t")
                
                withitems = []

                if cmd_array.redirect_table.inp:
                    withitems.append(f"open('{cmd_array.redirect_table.inp}', 'r') as shell_namespace.current_input_stream")

                if cmd_array.redirect_table.output:
                    withitems.append(
                        f"open('{cmd_array.redirect_table.output}', '{cmd_array.redirect_table.output_mode}') as shell_namespace.output_stream"
                    )

                if withitems:
                    code_block = f"with {', '.join(withitems)}:\n" + indent(code_block, "\t") 

                yield code_block

        tokens_iter = iter(tokens)

        code_string: str = "shell_namespace.current_input_stream = default_input\nshell_namespace.output_stream = default_output\n" + \
            "\n".join(_get_code_blocks())
        
        return compile(code_string, "<SHELL>", "exec")