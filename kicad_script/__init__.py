from pprint import pprint
from sexpdata import loads, Symbol
from types import SimpleNamespace


def create_board():
    with open("./fixtures/initial.kicad_pcb") as f:
        initial = loads(f.read())
    return initial


def get_thickness(board):
    general = next(item for item in board if item[0] == Symbol("general"))
    thickness = next(item for item in general if item[0] == Symbol("thickness"))
    return thickness[1]


def set_thickness(board, thickness):
    def _set_thickness(item):
        return [Symbol("thickness"), thickness]

    def _set_general(settings):
        return [
            Symbol("general"),
            *map(
                lambda item: _set_thickness(item)
                if item[0] == Symbol("thickness")
                else item,
                settings[1:],
            ),
        ]

    board = map(
        lambda item: _set_general(item)
        if item[0] == Symbol("general")
        else item,
        board,
    )
    return board


def get_nets(board):
    return [
        SimpleNamespace(**{"id": item[1], "name": item[2]})
        for item in board
        if item[0] == Symbol("net")
    ]
