import kicad_script as k
from sexpdata import Symbol


def test_create_board():
    board = k.create_board()
    assert board[0] == Symbol("kicad_pcb")


def test_get_thickness():
    board = k.create_board()
    assert k.get_thickness(board) == 1.6


def test_get_initial_nets():
    board = k.create_board()
    [initial_net] = k.get_nets(board)
    assert initial_net.id == 0
    assert initial_net.name == ""


def test_add_and_get_nets():
    board = k.create_board()
    board = k.add_net(board, "Net 1")
    board = k.add_net(board, "Net 2")

    [initial_net, added_net_1, added_net_2] = k.get_nets(board)

    assert added_net_1.id == 1
    assert added_net_1.name == "Net 1"
    assert added_net_2.id == 2
    assert added_net_2.name == "Net 2"


def test_set_and_get_edge_cut_points():
    board = k.create_board()
    board = k.set_edge_cut_points(board, ((-5, -5), (5, -5), (5, 5), (-5, 5)))
    assert k.get_edge_cut_points(board) == [(-5, -5), (5, -5), (5, 5), (-5, 5)]


def test_add_footprint():
    board = k.create_board()
    board = k.add_footprint(
        board,
        {
            "position": [50, 60],
            "rotation": 0,
            "library_name": "test",
            "footprint_name": "test",
        },
    )

    [footprint] = k.get_footprints(board)

    assert footprint[0] == Symbol("footprint")
    assert footprint[1] == "test:test"

    assert k.get_value(footprint, Symbol("layer")) == ["F.Cu"]
    assert k.get_value(footprint, Symbol("attr")) == [Symbol("through_hole")]
    assert k.get_value(footprint, Symbol("tedit")) is not None
    assert k.get_value(footprint, Symbol("tstamp")) is not None
    assert k.get_value(footprint, Symbol("at")) == [50, 60, 0]
