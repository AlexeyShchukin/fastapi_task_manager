from src.db.models import Task
from src.repositories.base_repository import Repository


class TaskRepository(Repository):
    model = Task
