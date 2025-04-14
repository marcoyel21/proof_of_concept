from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import boto3
import mysql.connector
from dotenv import load_dotenv
from typing import Optional
import os

# Load environment variables
load_dotenv()

app = FastAPI()


# Servir HTML desde /static
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

# AWS S3 config
s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)
BUCKET_NAME = os.getenv("BUCKET_NAME")

# DB connection function
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )

# Upload endpoint
@app.post("/upload")
async def upload_data(
    name: str = Form(...),
    lat: Optional[float] = Form(None),
    lng: Optional[float] = Form(None),
    image: UploadFile = File(...)
):
    # Upload image to S3
    s3.upload_fileobj(image.file, BUCKET_NAME, f"imgs/{image.filename}")

    # Insert into DB
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO concept.submissions (name, image_path, lat, lng) VALUES (%s, %s, %s, %s)",
        (name, image.filename, lat, lng)
    )
    conn.commit()
    conn.close()

    return {"message": "Upload successful"}
