"""Generate the microservices-lab architecture diagrams.

Dev-only tool - NOT part of the running app, NOT a dependency of any
service. To regenerate the diagrams:

    pip install diagrams
    # plus the system graphviz binary (provides the `dot` executable):
    #   macOS:   brew install graphviz
    #   Debian:  apt-get install graphviz

    python3 diagram/generate_diagram.py

Renders two diagrams (before/after, mirroring the original repo's
mon.png.png / ms.png.png convention):

    data/monolith.png       Users -> Monolith (single in-process service,
                             owns both operations, no network hops)

    data/microservices.png  Users -> Gateway (BFF) -> sum-service
                                                     -> mul-service
                                                     -> history-service
                             (the monolith is intentionally NOT shown here -
                             it's the "before" baseline this diagram is
                             contrasted against, not part of the
                             microservices topology itself)
"""

from __future__ import annotations

import os

from diagrams import Diagram, Edge
from diagrams.onprem.client import Users
from diagrams.programming.framework import FastAPI

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

GRAPH_ATTR = {
    "fontsize": "14",
    "bgcolor": "white",
    "pad": "0.5",
}


def generate_monolith_diagram() -> None:
    with Diagram(
        "microservices-lab - before: monolith",
        filename=os.path.join(OUTPUT_DIR, "monolith"),
        outformat="png",
        show=False,
        graph_attr=GRAPH_ATTR,
        direction="LR",
    ):
        users = Users("Users / browser")
        monolith = FastAPI("monolith\n(sum + mul, in-process)")

        users >> Edge(label="HTTP\nPOST /sum, POST /mul") >> monolith


def generate_microservices_diagram() -> None:
    with Diagram(
        "microservices-lab - after: microservices",
        filename=os.path.join(OUTPUT_DIR, "microservices"),
        outformat="png",
        show=False,
        graph_attr=GRAPH_ATTR,
        direction="LR",
    ):
        users = Users("Users / browser")

        gateway = FastAPI("Gateway (BFF)")

        sum_service = FastAPI("sum-service")
        mul_service = FastAPI("mul-service")
        history_service = FastAPI("history-service")

        users >> Edge(label="HTTP") >> gateway

        gateway >> Edge(label="POST /sum") >> sum_service
        gateway >> Edge(label="POST /mul") >> mul_service
        gateway >> Edge(label="logs every operation") >> history_service


def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    generate_monolith_diagram()
    generate_microservices_diagram()


if __name__ == "__main__":
    main()
