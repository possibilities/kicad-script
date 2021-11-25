import uuid
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


def add_net(board, name):
    next_id = len(get_nets(board))
    return (*board, (Symbol("net"), next_id, name))


def set_edge_cut_points(board, points, width=0.1):
    return (
        *board,
        *[
            (
                Symbol("gr_line"),
                (Symbol("start"), point[0], point[1]),
                (
                    Symbol("end"),
                    points[index + 1 if index < (len(points) - 1) else 0][0],
                    points[index + 1 if index < (len(points) - 1) else 0][1],
                ),
                (Symbol("layer"), "Edge.Cuts"),
                (Symbol("width"), width),
                (Symbol("tstamp"), Symbol(uuid.uuid4())),
            )
            for index, point in enumerate(points)
        ],
    )


def get_edge_cut_points(board):
    return [
        item[1][1:]
        for item in board
        if item[0] == Symbol("gr_line") and item[3][1] == "Edge.Cuts"
    ]
