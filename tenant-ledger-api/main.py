from fastapi import FastAPI
from schemas import TenantCreate

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
    tenants.append(tenant)
    return {"message": "Tenant created successfully", "tenant": tenant}