from fastapi import FastAPI, Depends, HTTPException, status
from schemas import TenantCreate, UserCreate, PropertyCreate, UserLogin, ChargeCreate, PaymentCreate
from db import get_connection
from security import hash_password, verify_password, create_access_token, get_current_user, NoAccess_Exception
from fastapi.security import OAuth2PasswordRequestForm


app = FastAPI()


@app.get("/health")
def health_check():
    return {"status": "ok"}

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
def user_login(form_data: OAuth2PasswordRequestForm = Depends()):
    entered_username = form_data.username
    entered_password = form_data.password

    conn,cursor = get_connection()
    cursor.execute("""SELECT id,username,password_hash FROM users WHERE users.username=%s"""
                    ,(entered_username,)
                    )
    row = cursor.fetchone()

    if row == None:
        return {"message": "Login Failed. Invalid Username or Password"}
    
    stored_hash = row[2]

    login_status = verify_password(entered_password, stored_hash)

    if not login_status:
        return {"message": "Login Failed. Invalid Username or Password"}
    else:
        access_token = create_access_token(payload={"sub": str(row[0])})

        return {"message": "Login successful", "access_token": access_token, "token_type": "bearer"}
    


@app.post("/properties")
def create_property(property: PropertyCreate, current_user = Depends(get_current_user)):
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
def get_properties(current_user = Depends(get_current_user)):
    owner_id = current_user["sub"]
    conn, cursor = get_connection()
    cursor.execute("""SELECT * FROM properties
        WHERE owner_id = %s""", (owner_id,)  )

    rows = cursor.fetchall()
    return {"Properties list: ": rows}


@app.post("/tenants")
def create_tenant(tenant: TenantCreate, current_user = Depends(get_current_user)):

    owner_id = current_user["sub"]
    conn, cursor = get_connection()

    cursor.execute("""SELECT id FROM properties WHERE owner_id=%s AND id =%s""",
                   (owner_id, tenant.property_id))
    property_ = cursor.fetchone()

    if property_ is None:
        raise NoAccess_Exception

    cursor.execute("""INSERT INTO tenants (property_id, name, phone, monthly_rent, rent_due_day, is_active)
    VALUES (%s, %s, %s, %s,%s,%s)
    RETURNING id;
    """,
    (tenant.property_id, tenant.name, tenant.phone, tenant.monthly_rent, tenant.rent_due_day, tenant.is_active)
    )

    tenantid = cursor.fetchone()[0]
    conn.commit()

    return {"message": "Tenant created successfully", "tenant id": tenantid}

@app.get("/tenants")
def get_tenants(current_user = Depends(get_current_user)):
    owner_id = current_user["sub"]
    conn, cursor = get_connection()
    cursor.execute("""SELECT tenants.name, phone, properties.name, monthly_rent, rent_due_day, is_active
        FROM tenants
        JOIN properties
        ON tenants.property_id = properties.id
        WHERE
        properties.owner_id = %s""", (owner_id,)  )

    rows = cursor.fetchall()
    return {"Tenants list: ": rows}


@app.post("/charges")
def create_charge(charge: ChargeCreate,current_user = Depends(get_current_user)):
    owner_id = current_user["sub"]
    conn, cursor = get_connection()

    cursor.execute("""SELECT properties.id FROM properties
            JOIN tenants
            ON tenants.property_id = properties.id
            WHERE properties.owner_id=%s AND tenants.id =%s""",
                       (owner_id, charge.tenant_id))
    property_ = cursor.fetchone()
    
    if property_ is None:
        raise NoAccess_Exception
    
    cursor.execute("""INSERT INTO charges (tenant_id, charge_type, description, billing_month, amount, due_date, status)
    VALUES (%s,%s,%s,%s,%s,%s,%s)
    RETURNING id;""", (charge.tenant_id, charge.charge_type, charge.description, charge.billing_month, charge.amount,
                                       charge.due_date,charge.status))
    charge_id = cursor.fetchone()[0]
    conn.commit()
    return {"message": "charge created successfully", "charge_id": charge_id}

@app.get("/charges")
def get_charges(current_user = Depends(get_current_user)):
    owner_id = current_user["sub"]
    conn, cursor = get_connection()
    cursor.execute("""SELECT *
        FROM charges
        JOIN tenants 
        ON charges.tenant_id = tenants.id
        JOIN properties
        ON tenants.property_id = properties.id
        WHERE
        properties.owner_id = %s""", (owner_id,)  )

    rows = cursor.fetchall()
    return {"Charges list: ": rows}

@app.post("/payments")
def create_payment(payment: PaymentCreate, current_user = Depends(get_current_user)):
    owner_id = current_user["sub"]
    conn, cursor = get_connection()
    
    cursor.execute("""SELECT charges.amount FROM charges
            JOIN tenants
            ON charges.tenant_id = tenants.id
            JOIN properties
            ON tenants.property_id = properties.id
            WHERE properties.owner_id=%s AND charges.id =%s""",
                        (owner_id, payment.charge_id))
    charge_ = cursor.fetchone()
    
    if charge_ is None:
        raise NoAccess_Exception

    charge_amount = charge_[0]

    # calculate total amount paid so far
    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM payments
        WHERE charge_id = %s
    """, (payment.charge_id,))

    total_paid = float(cursor.fetchone()[0])

    if total_paid + payment.amount > charge_amount:
        raise HTTPException(
            status_code=400,
            detail="Payment exceeds remaining balance."
        )

    cursor.execute("""INSERT INTO payments (charge_id, amount, payment_method, payment_date, notes)
    VALUES (%s,%s,%s,%s,%s)
    RETURNING id;""", (payment.charge_id, payment.amount, payment.payment_method, payment.payment_date, payment.notes))

    payment_id = cursor.fetchone()[0]

    new_total_paid = total_paid + payment.amount


    # Decide new status
    if new_total_paid >= charge_amount:
        status = "PAID"
    else:
        status = "PARTIALLY_PAID"

    # Update charge
    cursor.execute("""
        UPDATE charges
        SET status = %s,
            updated_at = NOW()
        WHERE id = %s
    """, (status, payment.charge_id))


    conn.commit()
    return {
        "message": "Payment recorded successfully",
        "payment_id": payment_id,
        "total_paid": new_total_paid,
        "remaining_balance": max(float(charge_amount) - new_total_paid, 0)
    }


@app.get("/payments")
def get_payments(current_user = Depends(get_current_user)):
    owner_id = current_user["sub"]
    conn, cursor = get_connection()
    cursor.execute("""SELECT *
        FROM payments
        JOIN charges
        ON payments.charge_id = charges.id
        JOIN tenants
        ON charges.tenant_id = tenants.id
        JOIN properties
        ON tenants.property_id = properties.id
        WHERE
        properties.owner_id = %s""", (owner_id,)  )

    rows = cursor.fetchall()
    return {"Charges list: ": rows}