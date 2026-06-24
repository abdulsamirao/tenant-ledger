from fastapi import FastAPI
from schemas import TenantCreate
from db import get_connection

app = FastAPI()

tenants = []

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/tenants")
def get_tenants():
    return tenants

@app.post("/tenants")
def create_tenant(tenant: TenantCreate):
    conn, cursor = get_connection()

    cursor.execute("""INSERT INTO tenants (name, rent)
    VALUES (%s, %s)
    RETURNING id;
    """,
    (tenant.name, tenant.rent)
    )

    tenantid = cursor.fetchone()[0]
    conn.commit()

    return {"message": "Tenant created successfully", "tenant id": tenantid}