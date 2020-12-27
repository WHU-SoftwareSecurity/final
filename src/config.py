from pydantic import BaseSettings

from pathlib import PurePath

from rich.console import Console


class Settings(BaseSettings):
    root_dir: PurePath = PurePath(__file__).parent.parent
    source_dir: PurePath = root_dir / "src"
    config_dir: PurePath = root_dir / "config"

    config_table_json: PurePath = config_dir / "table.json"
    config_docker_json: PurePath = config_dir / "docker.json"
    config_result_table_json: PurePath = config_dir / "result_table.json"


settings = Settings()

console = Console()