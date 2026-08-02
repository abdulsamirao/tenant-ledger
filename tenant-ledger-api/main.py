from fastapi import FastAPI
from schemas import TenantCreate, UserCreate, PropertyCreate
from db import get_connection

app = FastAPI()


@app.post("/register")
def create_user(user: UserCreate):

    hashed_pw = hash(user.password)

    conn, cursor = get_connection()
    cursor.execute("""INSERT INTO users (name, password)
    VALUES (%s,%s)
    returning id;
    """,
    (user.username, hashed_pw)
    )
    user_id = cursor.fetchall()[0]
    conn.commit

    return {"message": "User created successfully", "user_id": user_id}

@app.post("/login")
def user_login(username: str, password:str):
    entered_username = username
    entered_pw_hash = hash(password)

    conn,cursor = get_connection()
    cursor.execute("SELECT (id,username,password_hash) FROM users WHERE users.username='entered_username'")
    rows = cursor.fetchall

    #return error message if user doesnt exist
    #return message "incorrect username or password" if password_hash != entered_pw_hash
    #else return main page to the application?


@app.post("/properties")
def property_create(owner_id: int, property: PropertyCreate):
    conn, cursor = get_connection()

    cursor.execute("""INSERT INTO properties (owner_id, name, address) VALUES (%s,%s,%s)
    RETURNING id;""",
    (owner_id, property.name, property.address)
    )
    property_id = cursor.fetchall()[0]
    conn.commit
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