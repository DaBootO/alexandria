from api_endpoints import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Server is Running"}

# def test_list_databases_endpoint():
#     response = client.get("/listDatabases")
#     assert response.status_code == 200
#     assert "success" in response.json()

# def test_create_database_endpoint():
#     response = client.post("/createDatabase", json={
#         "db_name": "test_db",
#         # "cluster": "cluster1",
#         # "engine": "mysql",
#         "comment": "Test database"
#     })
#     assert response.status_code == 200
#     assert "success" in response.json()
#     assert response.json()["success"] == "Database created: test_db"