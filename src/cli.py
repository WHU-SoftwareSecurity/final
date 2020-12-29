import time
import subprocess

from pydantic.fields import Required

from .utils import load_json
from .config import settings, console
from .core import (DockerProcess, DockerManager,
                   load_docker_config, generate_table)
from src import callback


import click

from rich.table import Table
from rich.progress import track


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
@click.option("-f", "--file", type=str, required=False,
              default="", help="test file path")
@click.option("-e", "--echo", type=bool, required=False,
                default=True, help="whether echo detect info")
def run(file, echo) -> None:
    """running test"""
    docker_config_list = load_docker_config()

    thread_list = []
    for docker_config in docker_config_list:
        p = DockerProcess(docker_config)
        p.register_callback(getattr(callback, p.callback_name))

        if not echo:
            p.close_echo()

        if len(file):
            console.print(f"uploading file: `{file}` to docker: `{p.docker_name}:{p.upload_path}`")
            p.upload_file(file)
        thread_list.append(p)

    for t in thread_list:
        t.start()
        t.join(10)

    generate_table(thread_list)


@cli.command(context_settings={"ignore_unknown_options": True})
@click.option("-a", "--all_", type=click.Choice(["start", "restart", "stop"], case_sensitive=False),
              required=False, help="apply same option for all containers")
@click.argument("command", nargs=-1, required=False)
def docker(all_, command) -> None:
    """passing command to docker"""
    if all_ is not None:
        docker_manager = DockerManager()
        getattr(docker_manager, f"{all_}_all")()
    else:
        if len(command):
            DockerManager.execute_command(command)
        
