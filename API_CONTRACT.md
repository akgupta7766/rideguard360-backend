# RideGuard 360 — API Contract

## Base URL

/api

---

# Authentication

## POST /api/auth/login

### Purpose

Authenticate an Admin, Driver or Parent.

### Request

{
    "email": "admin@school.com",
    "password": "password123"
}

### Success Response — 200

{
    "access_token": "JWT_TOKEN",
    "token_type": "bearer",
    "user": {
        "id": "USER_ID",
        "name": "Transport Admin",
        "email": "admin@school.com",
        "role": "admin"
    }
}

### Errors

401 — Invalid email or password

403 — User account inactive

---

# Buses

GET /api/buses

GET /api/buses/{id}

GET /api/buses/{id}/details

POST /api/buses

PUT /api/buses/{id}

DELETE /api/buses/{id}

---

# Drivers

GET /api/drivers

GET /api/drivers/{id}

POST /api/drivers

PUT /api/drivers/{id}

---

# Students

GET /api/students

GET /api/students/{id}

POST /api/students

PUT /api/students/{id}

---

# Parents

GET /api/parents

GET /api/parents/{id}

---

# Routes

GET /api/routes

GET /api/routes/{id}

POST /api/routes

PUT /api/routes/{id}

---

# Stops

GET /api/routes/{route_id}/stops

POST /api/routes/{route_id}/stops

PUT /api/stops/{id}

---

# Trips

GET /api/trips

GET /api/trips/{id}

POST /api/trips/start

POST /api/trips/{id}/end

---

# Boarding

GET /api/boarding/stop/{stop_id}

POST /api/boarding

GET /api/boarding/trip/{trip_id}

---

# GPS

POST /api/gps/update

GET /api/gps/bus/{bus_id}

---

# Emergencies

POST /api/emergencies

GET /api/emergencies/active

GET /api/emergencies/{id}

POST /api/emergencies/{id}/resolve

---

# Notifications

GET /api/notifications

POST /api/notifications/{id}/read