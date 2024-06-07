import os
import logging
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import logging
import logging.config

from pydantic import (
    AnyUrl,
    Field,
    HttpUrl,
)

load_dotenv()


logging.config.fileConfig("./logging.conf")

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    mongo_dsn: AnyUrl = Field(
        f'mongodb+srv://{os.environ["MONGODB_USER"]}:{os.environ["MONGODB_PASSWORD"]}@clusterdevposicioncolec.jlxfej8.mongodb.net/?retryWrites=true&w=majority&appName=ClusterDevPosicionColectivos',
    )

    base_url: HttpUrl = Field(f"{os.environ['BASE_URL']}")
