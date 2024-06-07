import logging
import logging.config
import os

import pytz
from dotenv import load_dotenv
from pydantic import AnyUrl, Field, HttpUrl
from pydantic_settings import BaseSettings

load_dotenv()


logging.config.fileConfig("./logging.conf")

logger = logging.getLogger(__name__)

LOCAL_TIMEZONE = pytz.timezone("America/Argentina/Salta")


class Settings(BaseSettings):
    mongo_dsn: AnyUrl = Field(
        f'mongodb+srv://{os.environ["MONGODB_USER"]}:{os.environ["MONGODB_PASSWORD"]}@clusterdevposicioncolec.jlxfej8.mongodb.net/?retryWrites=true&w=majority&appName=ClusterDevPosicionColectivos',
    )

    base_url: HttpUrl = Field(f"{os.environ['BASE_URL']}")
