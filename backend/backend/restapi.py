import glob
import json
import logging
import math
import os
import re
import urllib
from typing import List

import asyncpg
from asyncpg.pool import Pool
from datetime import datetime, timedelta
import dateutil.parser
from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from backend.utils import DB_TIMEOUT, NODE_DATA_DIR

LOG = logging.getLogger(__name__)

router = APIRouter()


async def pool(request: Request) -> asyncpg.pool.Pool:
    return request.app.extra["db"]


@router.put("/update_node/{node_id}", status_code=200)
async def update_node(
        node_id: str,  # with ".olsr"
        request: Request,
        response: Response,
        pool: Pool = Depends(pool)
):
    try:
        r_json = await request.json()
    except Exception as e:
        return Response(status_code=400, content=f"Error parsing JSON: {str(e)}")

    if len(node_id) > 50:
        return Response(status_code=400, content="node_id too long")

    # make sure hostname, id, _id, ctime, mtime are in JSON file
    if "hostname" not in r_json:
        return Response(status_code=400, content="hostname missing in JSON")
    r_json["id"] = node_id
    r_json["_id"] = node_id
    f_path = f"{NODE_DATA_DIR}/{safe_file_name_from_node_id(node_id)}.json"
    if os.path.isfile(f_path):
        with open(f_path, 'r') as json_file:
            data = json_file.read()
            r_json["ctime"] = json.loads(data)["ctime"]
    else:
        r_json["ctime"] = datetime.utcnow().isoformat() + "Z"
    r_json["mtime"] = datetime.utcnow().isoformat() + "Z"

    await upsert_node_in_db(node_id, r_json["hostname"], r_json.get("latitude", None), r_json.get("longitude", None), r_json["ctime"], r_json["mtime"], pool)

    with open(f"{f_path}.new", "w") as json_file:
        data_s = json.dumps(r_json, indent=4)
        data_s = re.sub(r'\"mac\": \"..:..:XX:XX:..:..\"', '\"mac\": \"redacted\"', data_s)
        json_file.write(data_s)
    os.replace(f"{f_path}.new", f_path)

    return Response(status_code=200, content="OK")


@router.get("/view_nodes_spatial", status_code=200)
async def view_nodes_spatial(
        bbox: str = Query(..., description="Bounding box ('minLng,minLat,maxLng,maxLat')"),
        count: bool = Query(False, description="If true, return node count only instead of list containing node data"),
        pool: Pool = Depends(pool)
):
    try:
        b_coords = [float(x) for x in bbox.split(",")]
        assert len(b_coords) == 4
    except Exception as e:
        return Response(status_code=400, content=f"Error parsing bbox: {str(e)}")

    if not count:
        nodes = await pool.fetch(
            """
            SELECT * FROM nodes
            WHERE lng >= $1 AND lat >= $2 AND lng <= $3 AND lat <= $4 AND mtime > $5
            """,
            b_coords[0],
            b_coords[1],
            b_coords[2],
            b_coords[3],
            datetime.utcnow() - timedelta(days=7),
            timeout=DB_TIMEOUT
        )
        data = {"rows": [await get_node_data_from_node_row(node) for node in nodes]}
        return JSONResponse(status_code=200, content=data)
    else:
        node_count = await pool.fetchval(
            """
            SELECT count(id) FROM nodes
            WHERE lng >= $1 AND lat >= $2 AND lng <= $3 AND lat <= $4 AND mtime > $5
            """,
            b_coords[0],
            b_coords[1],
            b_coords[2],
            b_coords[3],
            datetime.utcnow() - timedelta(days=7),
            timeout=DB_TIMEOUT
        )
        data = {"count": int(node_count)}
        return JSONResponse(status_code=200, content=data)


class ViewNodesRequestData(BaseModel):
    keys: List[str] = Field(..., description="List of node IDs to return data for")


class ViewNodeInfoData(BaseModel):
    hostname: str = Field(..., description="Node hostname")
    ctime: str = Field(..., description="Creation time (ISO format)")
    mtime: str = Field(..., description="Last modified time (ISO format)")
    id: str = Field(..., description="Node ID")
    latlng: List[float] = Field(..., description="Latitude/longitude of node")


class ViewNodeResponseData(BaseModel):
    id: str = Field(..., description="Node ID")
    key: str = Field(..., description="Node ID (Couch legacy)")
    value: ViewNodeInfoData


@router.post("/view_nodes", response_model=List[ViewNodeResponseData], status_code=200)
async def view_nodes(
        view_nodes_data: ViewNodesRequestData,
        pool: Pool = Depends(pool)
):
    data = []
    for node_id in view_nodes_data.keys:
        node = await pool.fetchrow(
            """
            SELECT * FROM nodes
            WHERE id = $1
            """,
            node_id,
            timeout=DB_TIMEOUT
        )
        node_data = await get_node_data_from_node_row(node)
        data.append(node_data)
    return JSONResponse(status_code=200, content=data)


async def get_node_data_from_node_row(node):
    node_data = {
        "id": node["id"],
        "key": node["id"],
        "value": {
            "hostname": node["hostname"],
            "ctime": node["ctime"].isoformat() + "Z",
            "mtime": node["mtime"].isoformat() + "Z",
            "id": node["id"],
            "latlng": [node["lat"], node["lng"]]
        }
    }
    return node_data


class ViewNodesCoarseRequestData(BaseModel):
    keys: List[List[int]] = Field(..., description="List of [zoom, x, y] Slippy Map tile IDs to return node counts for")


class VncCoarseTileResponseData(BaseModel):
    key: List[int] = Field(..., description="Slippy Map tile ID")
    value: int = Field(..., description="Number of active nodes in this tile")


class ViewNodesCoarseResponseData(BaseModel):
    rows: List[VncCoarseTileResponseData]


@router.post("/view_nodes_coarse", response_model=ViewNodesCoarseResponseData, status_code=200)
async def view_nodes_coarse(
        view_nodes_coarse_data: ViewNodesCoarseRequestData,
        pool: Pool = Depends(pool)
):
    def num2deg(zoom, x_tile, y_tile):
        n = 2.0 ** zoom
        lon_deg = x_tile / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y_tile / n)))
        lat_deg = math.degrees(lat_rad)
        return lat_deg, lon_deg

    data = []
    for key in view_nodes_coarse_data.keys:
        if len(key) != 3:
            return Response(status_code=400, content="Invalid Slippy Map tile ID")
        nw = num2deg(key[0], key[1], key[2])
        se = num2deg(key[0], key[1] + 1, key[2] + 1)
        node_count = await pool.fetchval(
            """
            SELECT count(id) FROM nodes
            WHERE lng >= $1 AND lat >= $2 AND lng <= $3 AND lat <= $4 AND mtime > $5
            """,
            nw[1],
            se[0],
            se[1],
            nw[0],
            datetime.utcnow() - timedelta(days=7),
            timeout=DB_TIMEOUT
        )
        if node_count > 0:
            data.append({"key": key, "value": node_count})

    return JSONResponse(status_code=200, content={"rows": data})


@router.get("/db/{node_id}", status_code=200)
async def get_node_by_id(
        node_id: str
):
    f_path = f"{NODE_DATA_DIR}/{safe_file_name_from_node_id(node_id)}.json"
    return FileResponse(f_path)


@router.post("/sync_db_from_disk", status_code=200)
async def sync_db_from_disk(
        request: Request,
        pool: Pool = Depends(pool)
):
    if request.client.host != "127.0.0.1":
        return Response(status_code=403, content="Only localhost is allowed to do this")
    q_total_nodes = 0
    q_nodes_with_latlng = 0
    errors = []
    async with pool.acquire() as connection:
        async with connection.transaction():
            await connection.execute("TRUNCATE nodes")
            node_files = glob.glob(f"{NODE_DATA_DIR}/*.json")
            for node_file in node_files:
                try:
                    with open(node_file, 'r') as json_file:
                        data = json_file.read()
                        r_json = json.loads(data)
                    n_lat = r_json.get("latitude", None)
                    n_lng = r_json.get("longitude", None)
                    q_total_nodes += 1
                    if n_lat is not None and n_lng is not None:
                        q_nodes_with_latlng += 1
                    await upsert_node_in_db(r_json["id"], r_json["hostname"], n_lat, n_lng, r_json["ctime"], r_json["mtime"], connection)
                except Exception as e:
                    LOG.exception(f"Exception reading {node_file}")
                    errors.append({"node_file": node_file, "Exception": str(e)})
    return JSONResponse(
        status_code=200,
        content={"total_nodes": q_total_nodes, "nodes_with_latlng": q_nodes_with_latlng, "errors": errors}
    )


def safe_file_name_from_node_id(node_id: str) -> str:
    return urllib.parse.quote_plus(node_id).replace(".", "%2E")


async def upsert_node_in_db(node_id: str, hostname: str, lat: float, lng: float, c_time: str, m_time: str, pool):
    c_time_dt = dateutil.parser.parse(c_time[:-1])
    m_time_dt = dateutil.parser.parse(m_time[:-1])
    if lat is not None and lng is not None:
        assert await pool.execute(
            """
            INSERT INTO nodes (id, lat, lng, hostname, ctime, mtime)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (id) DO
            UPDATE SET lat = $2, lng = $3, hostname = $4, ctime = $5, mtime = $6;
            """,
            node_id,
            lat,
            lng,
            hostname,
            c_time_dt,
            m_time_dt,
            timeout=DB_TIMEOUT
        ) == "INSERT 0 1"
    else:
        await pool.execute(
            """
            DELETE FROM nodes
            WHERE id = $1
            """,
            node_id
        )
