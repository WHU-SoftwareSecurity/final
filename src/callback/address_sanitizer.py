from src.core import DockerInfo


def address_sanitizer_callback(stdout: str,
                               stderr: str,
                               docker_info: DockerInfo) -> bool:
    if "heap-use-after-free" in stdout or "heap-use-after-free" in stderr:
        return True
    else:
        return False
