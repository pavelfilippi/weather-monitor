from fastapi import Depends
from strawberry.fastapi import BaseContext

from src.dependencies.config import Config
from src.dependencies.config import get_config
from src.dependencies.database import Database
from src.dependencies.database import get_database


class AppContext(BaseContext):
    """Custom typed context class

    https://strawberry.rocks/docs/integrations/fastapi#context_getter
    """

    def __init__(
        self,
        config: Config = Depends(get_config),
        db: Database = Depends(get_database),
    ):
        super().__init__()
        self.config = config
        self.db = db
