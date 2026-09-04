import json
import os
from app.pipeline.state import PipelineState
from app.config import settings
from app.utils.logging import setup_logger

logger = setup_logger(__name__)

class ProjectStore:
    def __init__(self):
        self.data_dir = settings.data_dir
        os.makedirs(os.path.join(self.data_dir, "projects"), exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, "cache"), exist_ok=True)

    def _project_path(self, project_id: str) -> str:
        return os.path.join(self.data_dir, "projects", f"{project_id}.json")

    def save_project(self, state: PipelineState) -> None:
        try:
            path = self._project_path(state.project_id)
            with open(path, "w", encoding="utf-8") as f:
                f.write(state.model_dump_json(indent=2))
            logger.debug(f"Project {state.project_id} saved.")
        except Exception as e:
            logger.error(f"Failed to save project {state.project_id}: {str(e)}")

    def load_project(self, project_id: str):
        try:
            path = self._project_path(project_id)
            if not os.path.exists(path):
                return None
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return PipelineState(**data)
        except Exception as e:
            logger.error(f"Failed to load project {project_id}: {str(e)}")
            return None

project_store = ProjectStore()
