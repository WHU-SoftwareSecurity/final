import time

from .utils import load_json
from .config import settings, console
from .core import (DockerProcess, DockerInfo,
                   load_docker_config, generate_table)

import click

from rich.table import Table
from rich.progress import track

from src import callback


@click.group()
def cli() -> None:
    ...


@cli.command()
def info() -> None:
    """display project information"""
    table_dict = load_json(settings.config_table_json)

    # add table base config
    table = Table(**table_dict["table_base"])
    # add table header
    for column in table_dict["table_header"]:
        table.add_column(**column)
    # add table body
    for row in table_dict["table_body"]:
        table.add_row(*row)

    console.rule("[bold red]G8 Project")
    for _ in track(range(1000), description="Loading information...", refresh_per_second=1000):
        time.sleep(0.001)
    console.print("[bold]Reproduction")
    console.print("We want to reproduce the following projects, and names with checkmark are done.")
    console.print(table)
    console.rule("[bold red]G8 Project")


@cli.command()
def run() -> None:
    """running test"""
    docker_config_list = load_docker_config()

    thread_list = []
    test_idx = [0, 1, 2, 3, 5]
    for idx in test_idx:
        p = DockerProcess(docker_config_list[idx])
        p.register_callback(getattr(callback, docker_config_list[idx]["callback"]))
        thread_list.append(p)

    for t in thread_list:
        t.start()
        t.join(10)

    generate_table(thread_list)


if __name__ == '__main__':
    cli()
