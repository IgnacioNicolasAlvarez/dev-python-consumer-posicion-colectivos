#!/usr/bin/env python3

from config import Settings, logger

from src.services.http_client import HttpClient
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import datetime

settings = Settings()

if __name__ == "__main__":

    start_time = datetime.datetime.now(tz=datetime.timezone.utc)
    logger.info("Start time: " + str(start_time))

    http_client = HttpClient(base_url=settings.base_url)
    gruposLineas_response = http_client.get(paths=["/gruposLineas"], is_json=True)[0]

    try:
        if gruposLineas_response["error"] == 0:
            grupo = []
            for subgrupo in gruposLineas_response["grupos"]["subGrupos"]:
                if subgrupo["subGrupos"] and subgrupo["codGrupo"] == "Urbano":
                    for linea in subgrupo["subGrupos"]:
                        for sublinea in linea["lineas"]:
                            posicion_dict = {
                                "url": str(settings.base_url)
                                + f"/posicionesBuses/{sublinea['codLinea']}",
                                "path": f"/posicionesBuses/{sublinea['codLinea']}",
                                "codLinea": sublinea["codLinea"],
                                "tipo": subgrupo["codGrupo"],
                                "codSubGrupo": linea["codGrupo"],
                                "descripcion": sublinea["descripcion"],
                            }
                            grupo.append(posicion_dict)
    except Exception as e:
        logger.error(e)
        raise "Error al obtener las posiciones de los colectivos"

    client = MongoClient(settings.mongo_dsn.__str__(), server_api=ServerApi("1"))
    collection = client.ClusterDevPosicionColectivos.posiciones

    try:
        for posicion_dict in grupo:
            if not collection.find_one({"codLinea": posicion_dict["codLinea"]}):
                collection.insert_one(posicion_dict)
    except Exception as e:
        logger.error(e)

    urls = [linea["path"] for linea in grupo]

    for posicion in http_client.generate(paths=urls):
        if posicion["response"]["error"] == 0:
            for pos in posicion["response"]["posiciones"]:
                pos["timestamp"] = datetime.datetime.now(tz=datetime.timezone.utc)
                pos["location"] = {
                    "type": "Point",
                    "coordinates": [pos["longitud"], pos["latitud"]],
                }

                match_interno_query = {
                    "url": posicion["url"],
                    "posiciones.interno": pos["interno"],
                }
                match_query = {"url": posicion["url"]}
                existing_pos = collection.find_one(match_interno_query)

                if existing_pos:
                    collection.update_one(
                        match_interno_query,
                        {
                            "$addToSet": {
                                "posiciones.$.ubicacion": {
                                    "timestamp": pos["timestamp"],
                                    "location": pos["location"],
                                    "orientacion": pos["orientacion"],
                                    "proxima_parada": pos["proximaParada"],
                                }
                            }
                        },
                    )
                else:
                    collection.update_one(
                        match_query,
                        {
                            "$addToSet": {
                                "posiciones": {
                                    "interno": pos["interno"],
                                    "ubicacion": [
                                        {
                                            "timestamp": pos["timestamp"],
                                            "location": pos["location"],
                                            "orientacion": pos["orientacion"],
                                            "proxima_parada": pos["proximaParada"],
                                        }
                                    ],
                                }
                            }
                        },
                    )

    logger.info(
        "Total time: "
        + str(datetime.datetime.now(tz=datetime.timezone.utc) - start_time)
    )
