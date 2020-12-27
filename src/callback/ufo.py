from src.core import DockerInfo


def ufo_callback(stdout: str,
                 stderr: str,
                 docker_info: DockerInfo) -> bool:
    if 'candidateUafLs' in stdout:
        return True
    else:
        return False
