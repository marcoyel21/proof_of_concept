from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import boto3
import mysql.connector

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# AWS clients
s3 = boto3.client("s3")
bucket_name = "your-bucket-name"

@app.post("/upload")
async def upload(name: str = Form(...), lat: float = Form(...), lng: float = Form(...), image: UploadFile = File(...)):
    # Upload to S3
    s3.upload_fileobj(image.file, bucket_name, image.filename)

    # Save to DB
    conn = mysql.connector.connect(
        host="your-db-host",
        user="your-user",
        password="your-password",
        database="your-database"
    )
    cursor = conn.cursor()
    cursor.execute("INSERT INTO submissions (name, image_path, lat, lng) VALUES (%s, %s, %s, %s)",
                   (name, image.filename, lat, lng))
    conn.commit()
    conn.close()

    return "Uploaded successfully"
