from fastapi import FastAPI, Depends
from schemas import TenantCreate, UserCreate, PropertyCreate, UserLogin
from db import get_connection
from security import hash_password, verify_password, create_access_token, get_current_user

app = FastAPI()


@app.post("/register")
def create_user(user: UserCreate):

    hashed_pw = hash_password(user.password)

    conn, cursor = get_connection()
    cursor.execute("""INSERT INTO users (username, password_hash)
    VALUES (%s,%s)
    returning id;
    """,
    (user.username, hashed_pw)
    )
    user_id = cursor.fetchone()[0]
    conn.commit()

    return {"message": "User created successfully", "user_id": user_id}

@app.post("/login")
def user_login(user: UserLogin):
    entered_username = user.username

    conn,cursor = get_connection()
    cursor.execute("""SELECT id,username,password_hash FROM users WHERE users.username=%s"""
                    ,(entered_username,)
                    )
    row = cursor.fetchone()

    if row == None:
        return {"message": "Login Failed. Invalid Username or Password"}
    
    stored_hash = row[2]

    login_status = verify_password(user.password, stored_hash)

    if not login_status:
        return {"message": "Login Failed. Invalid Username or Password"}
    else:
        access_token = create_access_token(payload={"sub": str(row[0])})

        return {"message": "Login successful", "access_token": access_token, "token_type": "bearer"}
    


@app.post("/properties")
def property_create(property: PropertyCreate, current_user = Depends(get_current_user)):
    owner_id = current_user["sub"]
    conn, cursor = get_connection()

    cursor.execute("""INSERT INTO properties (owner_id, name, address) VALUES (%s,%s,%s)
    RETURNING id;""",
    (owner_id, property.name, property.address)
    )
    property_id = cursor.fetchone()[0]
    conn.commit()
    return {"message": "property created successfully", "property_id": property_id}

@app.get("/properties")
def get_property(i: int):
    conn, cursor = get_connection()
    cursor.execute("SELECT (id,name,address) FROM properties")
    rows = cursor.fetchall()
    return {"Property info: ": rows[i-1]}



@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/tenants")
def get_tenants(i: int):
    conn, cursor = get_connection()
    cursor.execute("SELECT (id,name,rent) FROM tenants")
    rows = cursor.fetchall()
    conn.commit()
    return {"Tenant info: ": rows[i-1]}

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