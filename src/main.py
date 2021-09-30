from argparse import ArgumentParser
from pathlib import Path
from graphing import *
from subprocess import Popen, PIPE


def main():
    arg_parser = ArgumentParser()
    arg_parser.add_argument(
        "fsm_path",
        type=Path,
        help="Path to the state machine description"
    )
    arg_parser.add_argument(
        "--det",
        default=False,
        action="store_true",
        help="Treat this state machine as deterministic"
    )
    arg_parser.add_argument(
        "--graph-path",
        type=Path,
        default=None,
        help="Path to the graph file that describes how this state machine should be drawn"
    )
    arg_parser.add_argument(
        "--out",
        type=Path,
        default=Path("fsm.jpg"),
        help="Path for the output JPEG to be created"
    )
    args = arg_parser.parse_args()

    with open(args.fsm_path, "r") as fp:
        fsm = StateMachine.loads(fp.read(), det=args.det)

    with open(args.graph_path, "r") as fp:
        graph = Graph.loads(fsm, fp.read())

    proc = Popen(f"jgraph -P | ps2pdf - | convert -density 300 - -quality 200 {args.out}",
                 stdin=PIPE, shell=True)
    proc.communicate(input=str(graph).encode())
    proc.wait()


if __name__ == '__main__':
    main()
