from fastapi import FastAPI
from app.db import get_db_connection
from pydantic import BaseModel
from typing import Literal
from datetime import date
app = FastAPI()

#First test API
@app.get("/")
def root():
    return {"message": "Job Application Tracker Successfully running!"}

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "job-application-tracker"
    }

@app.get("/jobs")
def get_jobs():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM jobs;")
    rows = cur.fetchall()
    conn.close()

    jobs = []

    for row in rows:
        jobs.append({
            "id": row[0],
            "companyName": row[1],
            "role": row[2],
            "status": row[3],
            "appliedDate": row[4],
            "notes": row[5],
            "createdAt": row[6]
        })

    return {"data": jobs}

class JobCreate(BaseModel):
    companyName: str
    role: str
    status: Literal["Applied", "Pending", "Accepted", "Rejected"]
    appliedDate: date
    notes: str

@app.post("/jobs")
def create_job(job: JobCreate):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
                INSERT INTO jobs (company_name, role, status, applied_date, notes)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING *
                """, (job.companyName, job.role, job.status, job.appliedDate, job.notes))

    new_job = cur.fetchone()
    conn.commit()
    conn.close()

    return {
        "message": "Job created successfully!",
        "data": new_job
    }