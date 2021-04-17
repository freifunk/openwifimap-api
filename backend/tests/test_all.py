import json
import logging

from backend.utils import NODE_DATA_DIR

LOG = logging.getLogger(__name__)


async def test_all(
        test_app, database
):
    LOG.info("**** PUTing node info")
    data = {
        "type": "node",
        "hostname": "test_node",
        "latitude": 52.520791,
        "longitude": 13.40951,
        "links": [{"id": "other_node.olsr", "quality": 1}]
    }
    resp = await test_app.put("/update_node/test_node.olsr", json=data)
    assert resp.status_code == 200

    LOG.info("**** PUTing node info again")
    resp = await test_app.put("/update_node/test_node.olsr", json=data)
    assert resp.status_code == 200

    LOG.info("**** Testing view_nodes_spatial")
    resp = await test_app.get("/view_nodes_spatial?bbox=12.9,52.27,14.12,52.7")
    assert resp.status_code == 200
    assert len(resp.json()["rows"]) == 1
    assert len(resp.json()["rows"][0]["value"]["links"]) == 1

    LOG.info("**** Testing view_nodes_spatial, count only")
    resp = await test_app.get("/view_nodes_spatial?bbox=12.9,52.27,14.12,52.7&count=true")
    assert resp.status_code == 200
    assert resp.json()["count"] == 1

    LOG.info("**** Testing view_nodes")
    resp = await test_app.post("/view_nodes", json={"keys": ["test_node.olsr", "unknown.olsr"]})
    assert resp.status_code == 200
    assert resp.json()["rows"][0]["id"] == "test_node.olsr"

    LOG.info("**** Testing view_nodes_coarse")
    resp = await test_app.post("/view_nodes_coarse", json={"keys": [[8, 137, 83]]})
    assert resp.status_code == 200
    assert len(resp.json()["rows"]) == 1

    LOG.info("**** Testing getting detailed node info")
    resp = await test_app.get("/db/test_node.olsr")
    assert resp.status_code == 200
    assert resp.json()["hostname"] == "test_node"

    LOG.info("**** Testing removing node data")
    with open(f"{NODE_DATA_DIR}/test_node%2Eolsr.json", "r") as f:
        data_str = f.read()
    del data["latitude"]
    del data["longitude"]
    resp = await test_app.put("/update_node/test_node.olsr", json=data)
    assert resp.status_code == 200

    LOG.info("**** Testing node is gone")
    resp = await test_app.get("/view_nodes_spatial?bbox=12.9,52.27,14.12,52.7")
    assert resp.status_code == 200
    assert len(resp.json()["rows"]) == 0

    LOG.info("**** Testing syncing db from disk")
    with open(f"{NODE_DATA_DIR}/test_node%2Eolsr.json", "w") as f:
        f.write(data_str)
    resp = await test_app.post("/sync_db_from_disk")
    assert resp.json()["total_nodes"] > 0

    LOG.info("**** Testing view_nodes_spatial, count only")
    resp = await test_app.get("/view_nodes_spatial?bbox=12.9,52.27,14.12,52.7&count=true")
    assert resp.status_code == 200
    assert resp.json()["count"] > 0
