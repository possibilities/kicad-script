import uuid
import json
from os import path, mkdir
from sexpdata import dumps, loads, Symbol
from shutil import copytree, rmtree


def create_board():
    basepath = path.dirname(__file__)
    with open(f"{basepath}/../../fixtures/initial.kicad_pcb") as f:
        initial = loads(f.read())
    return initial


def get_value(board, name):
    try:
        value = next(item for item in board if item[0] == Symbol(name))
        return value[1]
    except Exception:
        return None


def get_values(board, name):
    try:
        value = next(item for item in board if item[0] == Symbol(name))
        return value[1:]
    except Exception:
        return None


def set_values(board, name, values):
    def item_value(item):
        if isinstance(item, list) and str(item[0]) == name:
            return (item[0], *values)
        else:
            return item

    return list(map(item_value, board))


timestampable_footprint_items = ["fp_text", "pad", "gr_line", "fp_line"]


def add_timestamps(item):
    if (isinstance(item, list) or isinstance(item, tuple)) and str(
        item[0]
    ) in timestampable_footprint_items:
        item = set_values(item, "tstamp", [Symbol(uuid.uuid4())])
    return item


rotateable_footprint_items = ["fp_text", "pad"]


def add_rotations(footprint_rotation):
    def _add_rotations(item):
        if (isinstance(item, list) or isinstance(item, tuple)) and str(
            item[0]
        ) in rotateable_footprint_items:
            item_position = get_values(item, "at")

            if not item_position:
                return item

            item_position_numbers = [
                value for value in item_position if type(value) in [int, float]
            ]

            item_position_non_numbers = [
                value
                for value in item_position
                if type(value) not in [int, float]
            ]

            item_rotation = (
                item_position_numbers[2]
                if len(item_position_numbers) == 3
                and isinstance(item_position_numbers[2], int)
                else 0
            )

            item = set_values(
                item,
                "at",
                (
                    item_position_numbers[0],
                    item_position_numbers[1],
                    item_rotation + footprint_rotation,
                    *item_position_non_numbers,
                ),
            )
        return item

    return _add_rotations


def add_footprint(board, options):
    position = options["position"]
    library_name = options["library_name"]
    footprint_name = options["footprint_name"]

    with open(f"{library_name}.pretty/{footprint_name}.kicad_mod") as f:
        footprint_template = loads(f.read())

    footprint_rotation = (
        options["rotation"]
        if "rotation" in options and options["rotation"] != 0
        else 0
    )

    at = (
        [*position, footprint_rotation]
        if "rotation" in options and options["rotation"] != 0
        else position
    )

    add_rotations_at = add_rotations(footprint_rotation)

    footprint_with_timestamps = list(
        map(add_timestamps, footprint_template[2:])
    )

    footprint_with_rotations = list(
        map(add_rotations_at, footprint_with_timestamps)
    )

    footprint = [
        Symbol("footprint"),
        f"{library_name}:{footprint_name}",
        [Symbol("tstamp"), Symbol(uuid.uuid4())],
        [Symbol("at"), *at],
        *footprint_with_rotations,
    ]

    return (*board, footprint)


def get_footprints(board):
    return [item for item in board if item[0] == Symbol("footprint")]


def get_nets(board):
    return [item for item in board if item[0] == Symbol("net")]


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


def save_board(board, project_path, project_name):
    try:
        mkdir(project_path)
    except FileExistsError:
        pass

    footprints = get_footprints(board)
    footprint_library_names = []

    for footprint in footprints:
        [library_name, footprint_name] = footprint[1].split(":")
        if library_name not in footprint_library_names:
            footprint_library_names.append(library_name)

    for library_name in footprint_library_names:
        rmtree(f"data/{library_name}.pretty")
        copytree(f"{library_name}.pretty", f"data/{library_name}.pretty")

    pcb_file = open(f"{project_path}/{project_name}.kicad_pcb", "w")
    pcb_file.write(dumps(board, pretty_print=True).replace("\\.", "."))
    pcb_file.close()

    basepath = path.dirname(__file__)
    with open(f"{basepath}/../../fixtures/initial.kicad_pro") as pro_file:
        initial_kicad_pro_file = pro_file.read()

    initial_kicad_pro_file = json.loads(initial_kicad_pro_file)

    initial_kicad_pro_file = {
        **initial_kicad_pro_file,
        "meta": {"filename": f"{project_name}.kicad_pro"},
    }

    pro_file = open(f"{project_path}/{project_name}.kicad_pro", "w")
    pro_file.write(json.dumps(initial_kicad_pro_file))
    pro_file.close()
