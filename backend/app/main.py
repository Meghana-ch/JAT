from fastapi import FastAPI, HTTPException
from app.db import get_db_connection
from pydantic import BaseModel
from typing import Literal
from datetime import date
from uuid import UUID

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

def job_formatter(row):
    return {
        "id": row[0],
        "companyName": row[1],
        "role": row[2],
        "status": row[3],
        "appliedDate": row[4],
        "notes": row[5],
        "createdAt": row[6]
    }

##################### fetch all jobs ####################
@app.get("/jobs")
def get_jobs():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM jobs;")
    rows = cur.fetchall()
    conn.close()

    jobs = []

    for row in rows:
        jobs.append(job_formatter(row))

    return {"data": jobs}

##################### fetch one jobs ####################
@app.get("/jobs/{job_id}")
def get_one_job(job_id: UUID):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
                SELECT * FROM jobs
                WHERE id = %s
                """, (str(job_id),))
    row = cur.fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code = 404, detail = "Job not found")
    else:
        return {"data": job_formatter(row)}

##################### create a new job ####################
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
        "data": job_formatter(new_job)
    }

##################### update a job ####################
class JobStatusUpdate(BaseModel):
    status: Literal["Applied", "Pending", "Accepted", "Rejected"]

@app.put("/jobs/{job_id}")
def update_job_status(job_id: UUID, job: JobStatusUpdate):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
                UPDATE jobs
                SET status = %s
                WHERE id = %s
                RETURNING *
                """, (job.status, str(job_id)))
    
    updated_job = cur.fetchone()
    if updated_job is None:
        conn.close()
        raise HTTPException(status_code = 404, detail = "Job not found")

    conn.commit()
    conn.close()
    return {
        "message": "Job status updated succesfully!",
        "data": job_formatter(updated_job)
    }

##################### delete a job ####################
@app.delete("/jobs/{job_id}")
def delete_job(job_id: UUID):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
                DELETE FROM jobs
                WHERE id = %s
                RETURNING *
                """, (str(job_id),))
    
    deleted_job = cur.fetchone()
    if deleted_job is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Job not found")
    
    conn.commit()
    conn.close()
    return {
        "message": "Job deleted successfully!",
        "data": job_formatter(deleted_job)
    }