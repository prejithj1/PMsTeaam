from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from ibm_boto3 import resource
from ibm_botocore.client import Config
import io
from PyPDF2 import PdfReader
import re


app = FastAPI(
    title="ECG Summary API",
    description="API for extracting and summarizing ECG data from PDF reports",
    version="1.0.0",
    openapi_servers=[
        {"url": "http://0.0.0.0:8000", "description": "Local server"}
    ]
)

# Set up IBM COS credentials
cos = resource(
    "s3",
    ibm_api_key_id="yMT2IDJI5P9ghzPqZjG_8KZ2JXwsv5qyvtPBQlB9wsnE",
    ibm_service_instance_id="crn:v1:bluemix:public:cloud-object-storage:global:a/d969295e1cee40788ff4d1cbd1634105:d1c6ef71-b111-480d-bdb6-c6dde8e252b6:bucket:ecg-reports-bucket",
    config=Config(signature_version="oauth"),
    endpoint_url="https://s3.direct.us-south.cloud-object-storage.appdomain.cloud"
)

# List last 3 ECGs for patient X

def get_latest_ecgs():
    bucket_name = "ecg-reports-bucket"
    file_path = "ECG-Sample-Report.pdf"
    with open(file_path, "rb") as file:
     obj = file.read()
   # obj = cos.Object(bucket_name, "ECG-Sample-Report.pdf")
     #response = obj.get()
    # pdf_bytes = obj['Body'].read()
     return obj

def extract_text_from_pdf_bytes(pdf_bytes):
    # Convert bytes to a file-like object
    pdf_stream = io.BytesIO(pdf_bytes)
    print('here 1')
    # Initialize a PDF reader
    pdf_reader = PdfReader(pdf_stream)
    print('here 2')
    # Extract text from each page
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    print('here 3')
    return text
def summarize_ecg_data(ecg_text):
    summary = {}
    print('here 4')
    # Extract heart rate (bpm) using regex
    heart_rate_match = re.search(r'Heart Rate:\s*(\d+)\s*bpm', ecg_text, re.IGNORECASE)
    if heart_rate_match:
        summary['Heart Rate (bpm)'] = heart_rate_match.group(1)
    
    # Extract diagnosis (e.g., Normal, Arrhythmia)
    diagnosis_match = re.search(r'(Normal|Arrhythmia|Mild arrhythmia|Severe arrhythmia)', ecg_text, re.IGNORECASE)
    if diagnosis_match:
        summary['Diagnosis'] = diagnosis_match.group(1)
    
    # Extract any timestamps or dates
    date_match = re.search(r'Date:\s*([0-9]{2}/[0-9]{2}/[0-9]{4})', ecg_text)
    if date_match:
        summary['Date'] = date_match.group(1)
    print('here 5')
    return summary
    
@app.get("/get_last_3_ecg_reports", summary="Extract text from ECG report", response_class=PlainTextResponse)
def get_last_3_ecg_reports(patient_id):
    pdf_bytes = get_latest_ecgs()
    # Extract text from the PDF
    ecg_text = extract_text_from_pdf_bytes(pdf_bytes)

    # Print the extracted ECG report text
  #  print('ecg text '+ecg_text)

   # ecg_summary = summarize_ecg_data(ecg_text)
   # print('Summary '+ecg_summary)
    return ecg_text

# To run the FastAPI app:
# uvicorn ecg_openapi_service:app --reload

# OpenAPI documentation available at:
# - Swagger UI: http://127.0.0.1:8000/docs
# - OpenAPI JSON: http://127.0.0.1:8000/openapi.json
