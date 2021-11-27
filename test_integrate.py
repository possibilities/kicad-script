import os
import kicad_script as k
from sexpdata import dumps
from shutil import copyfile


def test_integrate():
    board = k.create_board()
    board = k.set_edge_cut_points(
        board, ((71.12, 40.64), (71.12, 78.74), (30.48, 78.74), (30.48, 40.64))
    )
    board = k.add_net(board, "Net 1")
    board = k.add_net(board, "Net 2")
    board = k.add_footprint(
        board,
        {
            "id": 1,
            "position": [50, 60],
            "rotation": 15,
            "library_name": "test",
            "footprint_name": "test",
        },
    )

    [footprint] = k.get_footprints(board)

    try:
        os.mkdir("data")
    except:
        pass

    copyfile("fixtures/initial.kicad_pro", "data/test_add_footprint.kicad_pro")
    f = open("data/test_add_footprint.kicad_pcb", "w")
    f.write(dumps(board, pretty_print=True).replace("\\.", "."))
    f.close()
