import kicad_script as k
from sexpdata import dumps, Symbol
from pprint import pprint


def test_create_board():
    board = k.create_board()
    assert board[0] == Symbol("kicad_pcb")


def test_get_thickness():
    board = k.create_board()
    assert k.get_thickness(board) == 1.6


def test_set_thickness():
    board = k.create_board()
    board = k.set_thickness(board, 1.7)
    assert k.get_thickness(board) == 1.7
