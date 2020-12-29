from dataclasses import dataclass
from pathlib import PurePath
from typing import List, Callable, Optional, Union, Dict
# from multiprocessing import Process
from threading import Thread
import time
import subprocess

from paramiko import (SSHClient, Transport)

from .config import settings, console
from .utils import load_json

from rich.table import Table


@dataclass
class DockerInfo:
    project_name: str
    docker_name: str
    host: str
    port: int
    username: str
    password: str
    commands: List[str]
    callback: str
    upload_path: str


CallBackFunctionType = Optional[
    Callable[[str, str, DockerInfo], bool]
]


class DockerProcess(Thread):

    def __init__(self, docker_info: Union[DockerInfo, Dict]) -> None:
        super().__init__()
        if isinstance(docker_info, Dict):
            self._docker_info = DockerInfo(**docker_info)
        elif isinstance(docker_info, DockerInfo):
            self._docker_info = docker_info
        else:
            raise ValueError("not supported type!")

        console.print(f"create project: {self._docker_info.project_name}")
        self._transport = Transport(
            (self._docker_info.host, self._docker_info.port))
        self._ssh = SSHClient()
        self._ssh._transport = self._transport

        self._callback: CallBackFunctionType = None

        self._echo_on = True

    def register_callback(self, callback: CallBackFunctionType) -> None:
        self._callback = callback

    def run(self) -> None:
        self._connect_docker()

        setattr(self, "_result", False)
        for command in self._docker_info.commands:
            self._apply_command(command=command,
                                callback=self._callback)

        console.print('\n')
        console.rule(f"[bold red]{self._docker_info.project_name} result")
        if self._result:
            console.print("uaf detected!")
        else:
            console.print("no uaf!")
        console.rule(f"[bold red]{self._docker_info.project_name} result")

    def _connect_docker(self) -> None:
        console.print(f"connect to docker: {self._docker_info.docker_name}")
        self._transport.connect(username=self._docker_info.username,
                                password=self._docker_info.password)

    def _apply_command(self, *,
                       command: str,
                       callback: CallBackFunctionType = None) -> None:
        _, stdout, stderr = self._ssh.exec_command(command)
        stdout = stdout.read().decode("utf8")
        stderr = stderr.read().decode("utf8")

        if self._echo_on:
            self._display_output(stdout, stderr)

        if callback is not None:
            result = callback(stdout, stderr, self._docker_info)
            if not self._result:
                self._result = result
        else:
            raise AttributeError(
                "call `register_callback` before starting process!")

    def join(self, timeout: Optional[float] = ...) -> None:
        super().join(timeout)
        self._transport.close()

    def _display_output(self,
                        stdout: str,
                        stderr: str) -> None:
        console.print('\n')
        console.rule(f"[bold red]{self._docker_info.project_name} output")
        # 以utf-8编码对结果进行解码
        console.log(stdout)
        console.rule(f"[bold red]{self._docker_info.project_name} output")
        time.sleep(1)
        if stderr != '':
            console.print('\n')
            console.rule(
                f"[bold red]{self._docker_info.project_name} error output")
            console.log(stderr)
            console.rule(
                f"[bold red]{self._docker_info.project_name} error output")

    @property
    def docker_name(self) -> str:
        return self._docker_info.docker_name

    @property
    def project_name(self) -> str:
        return self._docker_info.project_name

    @property
    def upload_path(self) -> str:
        return self._docker_info.upload_path

    @property
    def callback_name(self) -> str:
        return self._docker_info.callback

    def get_result(self) -> Optional[bool]:
        if not hasattr(self, "_result"):
            raise AttributeError("start process before call `get_result`!")
        return getattr(self, "_result")

    def upload_file(self, local_file_path: str) -> None:
        target_path = f"{self._docker_info.docker_name}:{self._docker_info.upload_path}"

        subprocess.run(["docker", "cp", local_file_path, target_path])

    def close_echo(self):
        self._echo_on = False


def load_docker_config(config_json: Union[str, PurePath] = settings.config_docker_json) -> List[DockerInfo]:
    return load_json(config_json)


def generate_table(thread_list: List[DockerProcess]) -> None:
    table_dict = load_json(settings.config_result_table_json)

    table = Table(**table_dict["table_base"])
    for column in table_dict["table_header"]:
        table.add_column(**column)

    for i, t in enumerate(thread_list, start=1):
        if t.project_name == "HeapDetective":
            continue
        row = [str(i), t.project_name,
               "[red]Detected" if t.get_result() else "[green]Undetected"]
        table.add_row(*row)

    console.print(table)


class DockerManager:

    def __init__(self, *,
                 docker_config_path: Union[str, PurePath] = settings.config_docker_json) -> None:
        docker_config_json = load_docker_config(docker_config_path)
        
        self._docker_info_list = [
            DockerInfo(**docker_info) for docker_info in docker_config_json
        ]

        self._docker_containers = set((docker_info.docker_name for docker_info in self._docker_info_list))

    @property
    def container_list(self) -> List[str]:
        return list(self._docker_containers)

    def _do_all(self, option: str) -> None:
        for d in self._docker_containers:
            console.print(f"{option} container ", end="")
            self.execute_command([option, d])

    def start_all(self) -> None:
        self._do_all("start")

    def restart_all(self) -> None:
        self._do_all("restart")

    def stop_all(self) -> None:
        self._do_all("stop")

    @staticmethod
    def execute_command(command: List[str]) -> None:
        subprocess.run(["docker", *command])