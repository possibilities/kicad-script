import kicad_script as k
from sexpdata import Symbol


def test_create_board():
    board = k.create_board()
    assert board[0] == Symbol("kicad_pcb")


def test_add_and_get_nets():
    board = k.create_board()
    board = k.add_net(board, "Net 1")
    board = k.add_net(board, "Net 2")

    [initial_net, added_net_1, added_net_2] = k.get_nets(board)

    assert added_net_1[1] == 1
    assert added_net_1[2] == "Net 1"
    assert added_net_2[1] == 2
    assert added_net_2[2] == "Net 2"


def test_set_and_get_edge_cut_points():
    board = k.create_board()
    board = k.set_edge_cut_points(board, ((-5, -5), (5, -5), (5, 5), (-5, 5)))
    assert k.get_edge_cut_points(board) == [(-5, -5), (5, -5), (5, 5), (-5, 5)]


def test_add_footprint():
    board = k.create_board()
    board = k.add_footprint(
        board,
        {
            "reference": "TEST_1",
            "position": [50, 60],
            "library_name": "test",
            "footprint_name": "test",
        },
    )

    [footprint] = k.get_footprints(board)

    assert footprint[0] == Symbol("footprint")
    assert footprint[1] == "test:test"

    assert k.get_value(footprint, Symbol("layer")) == "F.Cu"
    assert k.get_value(footprint, Symbol("attr")) == Symbol("through_hole")
    assert k.get_value(footprint, Symbol("tedit")) is not None
    assert k.get_value(footprint, Symbol("tstamp")) is not None
    assert k.get_values(footprint, Symbol("at")) == [50, 60]


def test_save_board():
    board = k.create_board()
    board = k.set_edge_cut_points(
        board, ((71.12, 40.64), (71.12, 78.74), (30.48, 78.74), (30.48, 40.64))
    )
    board = k.add_net(board, "Net 1")
    board = k.add_net(board, "Net 2")
    board = k.add_footprint(
        board,
        {
            "reference": "TEST_1",
            "position": [50, 60],
            "rotation": 15,
            "library_name": "test",
            "footprint_name": "test",
        },
    )
    k.save_board(board, "data", "test")
