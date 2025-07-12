"""
AWS Service Clients
"""
import boto3
import json
from botocore.exceptions import ClientError
from typing import Dict, Any, Optional
import structlog

from app.core.config import settings

logger = structlog.get_logger("aws_clients")


class S3Client:
    """S3 client for file operations."""
    
    def __init__(self):
        self.client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket_name = settings.S3_BUCKET_NAME
    
    def generate_presigned_url(self, key: str, expiration: int = 3600) -> str:
        """Generate presigned URL for file upload."""
        try:
            url = self.client.generate_presigned_url(
                'put_object',
                Params={'Bucket': self.bucket_name, 'Key': key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            logger.error("Error generating presigned URL", error=str(e), key=key)
            raise
    
    def upload_file(self, file_path: str, key: str) -> bool:
        """Upload file to S3."""
        try:
            self.client.upload_file(file_path, self.bucket_name, key)
            logger.info("File uploaded successfully", key=key)
            return True
        except ClientError as e:
            logger.error("Error uploading file", error=str(e), key=key)
            return False
    
    def download_file(self, key: str, file_path: str) -> bool:
        """Download file from S3."""
        try:
            self.client.download_file(self.bucket_name, key, file_path)
            logger.info("File downloaded successfully", key=key)
            return True
        except ClientError as e:
            logger.error("Error downloading file", error=str(e), key=key)
            return False
    
    def delete_file(self, key: str) -> bool:
        """Delete file from S3."""
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=key)
            logger.info("File deleted successfully", key=key)
            return True
        except ClientError as e:
            logger.error("Error deleting file", error=str(e), key=key)
            return False
    
    def list_files(self, prefix: str = "") -> list:
        """List files in S3 bucket."""
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            files = []
            if 'Contents' in response:
                files = [obj['Key'] for obj in response['Contents']]
            return files
        except ClientError as e:
            logger.error("Error listing files", error=str(e), prefix=prefix)
            return []


class EventBridgeClient:
    """EventBridge client for event publishing."""
    
    def __init__(self):
        self.client = boto3.client(
            'events',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
    
    def publish_event(self, event_bus_name: str, source: str, detail_type: str, detail: Dict[str, Any]) -> bool:
        """Publish event to EventBridge."""
        try:
            response = self.client.put_events(
                Entries=[
                    {
                        'Source': source,
                        'DetailType': detail_type,
                        'Detail': json.dumps(detail),
                        'EventBusName': event_bus_name
                    }
                ]
            )
            
            if response['FailedEntryCount'] > 0:
                logger.error("Event publication failed", response=response)
                return False
            
            logger.info("Event published successfully", source=source, detail_type=detail_type)
            return True
            
        except ClientError as e:
            logger.error("Error publishing event", error=str(e), source=source)
            return False


class SNSClient:
    """SNS client for notifications."""
    
    def __init__(self):
        self.client = boto3.client(
            'sns',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
    
    def publish_message(self, topic_arn: str, message: str, subject: str = "") -> bool:
        """Publish message to SNS topic."""
        try:
            response = self.client.publish(
                TopicArn=topic_arn,
                Message=message,
                Subject=subject
            )
            
            logger.info("Message published successfully", topic_arn=topic_arn, message_id=response['MessageId'])
            return True
            
        except ClientError as e:
            logger.error("Error publishing message", error=str(e), topic_arn=topic_arn)
            return False


class AthenaClient:
    """Athena client for analytics queries."""
    
    def __init__(self):
        self.client = boto3.client(
            'athena',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.output_location = f"s3://{settings.S3_BUCKET_NAME}/athena-results/"
    
    def execute_query(self, query: str, database: str = "default") -> Optional[str]:
        """Execute Athena query."""
        try:
            response = self.client.start_query_execution(
                QueryString=query,
                QueryExecutionContext={'Database': database},
                ResultConfiguration={'OutputLocation': self.output_location}
            )
            
            query_execution_id = response['QueryExecutionId']
            logger.info("Query execution started", query_execution_id=query_execution_id)
            
            return query_execution_id
            
        except ClientError as e:
            logger.error("Error executing query", error=str(e), query=query)
            return None
    
    def get_query_results(self, query_execution_id: str) -> Optional[Dict[str, Any]]:
        """Get query results."""
        try:
            response = self.client.get_query_results(QueryExecutionId=query_execution_id)
            return response
            
        except ClientError as e:
            logger.error("Error getting query results", error=str(e), query_execution_id=query_execution_id)
            return None


# Create client instances
s3_client = S3Client()
eventbridge_client = EventBridgeClient()
sns_client = SNSClient()
athena_client = AthenaClient()
