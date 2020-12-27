from src.core import DockerInfo


def heap_detective_callback(stdout: str,
                            stderr: str,
                            docker_info: DockerInfo) -> bool:
    return False
