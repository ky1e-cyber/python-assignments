import io
import os
import shell
import shutil

SANDBOX = "sandbox"


def check(test_number: int):
    os.chdir(f"./tests/{test_number}")
    try:
        with open(f"input.txt", "r") as inp:
            with open(f"output.txt", "r", encoding="utf-8") as out:
                initial_dir = os.getcwd()
                shutil.copytree("filesys", SANDBOX)
                os.chdir(SANDBOX)
                try:
                    result = io.StringIO("")
                    shell.solution(inp, result)

                    result.seek(0)
                    for expected_line in out:
                        real_line = result.readline()
                        assert real_line.strip() == expected_line.strip()
                finally:
                    os.chdir(initial_dir)
                    shutil.rmtree(SANDBOX)
    finally:
        os.chdir("../..")


def test1():
    check(1)


def test2():
    check(2)


def test3():
    check(3)


def test4():
    check(4)


def test5():
    check(5)


def test6():
    check(6)


# def test7():
#     check(7)


def test8():
    check(8)


def test9():
    check(9)


def test10():
    check(10)


def test11():
    check(11)
