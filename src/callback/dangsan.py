from src.core import DockerInfo

from typing import Optional


def dangsan_callback(stdout: str,
                     stderr: str,
                     docker_info: DockerInfo) -> Optional[bool]:
    if "G8 UAF NO!" in stdout:
        return False
    else:
        return True


