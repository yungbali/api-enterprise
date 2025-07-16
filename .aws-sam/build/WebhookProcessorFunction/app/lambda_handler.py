"""
Lambda Handler for AWS Lambda deployment
"""
from mangum import Mangum
from app.main import app

# Create Lambda handler
handler = Mangum(app, lifespan="off")
