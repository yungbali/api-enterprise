"""
Mock service framework for external API integrations.
"""
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from unittest.mock import Mock, patch, MagicMock
import random

from faker import Faker

fake = Faker()


class MockServiceManager:
    """Manager for all mock services."""
    
    def __init__(self):
        self.mocks = {}
        self.active_patches = []
    
    def register_mock(self, service_name: str, mock_instance):
        """Register a mock service."""
        self.mocks[service_name] = mock_instance
    
    def get_mock(self, service_name: str):
        """Retrieve a registered mock."""
        return self.mocks.get(service_name)
    
    def reset_all_mocks(self):
        """Reset all mocks to initial state."""
        for mock in self.mocks.values():
            if hasattr(mock, 'reset_mock'):
                mock.reset_mock()
    
    def start_patches(self):
        """Start all patches."""
        for patch_obj in self.active_patches:
            patch_obj.start()
    
    def stop_patches(self):
        """Stop all patches."""
        for patch_obj in self.active_patches:
            patch_obj.stop()
        self.active_patches.clear()
    
    def add_patch(self, patch_obj):
        """Add a patch to be managed."""
        self.active_patches.append(patch_obj)


class MusicBrainzMockService:
    """Mock service for MusicBrainz API."""
    
    def __init__(self):
        self.responses = {}
        self.call_count = 0
        self.last_request = None
    
    def setup_recording_response(self, query: str, recordings: List[Dict[str, Any]]):
        """Setup mock response for recording search."""
        self.responses[f"recording:{query}"] = {
            "recordings": recordings,
            "count": len(recordings),
            "offset": 0
        }
    
    def setup_artist_response(self, query: str, artists: List[Dict[str, Any]]):
        """Setup mock response for artist search."""
        self.responses[f"artist:{query}"] = {
            "artists": artists,
            "count": len(artists),
            "offset": 0
        }
    
    def setup_release_response(self, query: str, releases: List[Dict[str, Any]]):
        """Setup mock response for release search."""
        self.responses[f"release:{query}"] = {
            "releases": releases,
            "count": len(releases),
            "offset": 0
        }
    
    def get_recording_response(self, query: str) -> Dict[str, Any]:
        """Get mock recording response."""
        self.call_count += 1
        self.last_request = f"recording:{query}"
        
        # Return predefined response or generate default
        if f"recording:{query}" in self.responses:
            return self.responses[f"recording:{query}"]
        
        # Generate default response
        return {
            "recordings": [{
                "id": str(uuid.uuid4()),
                "title": fake.catch_phrase(),
                "artist-credit": [{"artist": {"name": fake.name()}}],
                "length": random.randint(120000, 480000),
                "isrcs": [self._generate_isrc()]
            }],
            "count": 1,
            "offset": 0
        }
    
    def get_artist_response(self, query: str) -> Dict[str, Any]:
        """Get mock artist response."""
        self.call_count += 1
        self.last_request = f"artist:{query}"
        
        if f"artist:{query}" in self.responses:
            return self.responses[f"artist:{query}"]
        
        return {
            "artists": [{
                "id": str(uuid.uuid4()),
                "name": fake.name(),
                "sort-name": fake.name(),
                "type": "Person",
                "country": fake.country_code()
            }],
            "count": 1,
            "offset": 0
        }
    
    def simulate_error(self, error_type: str = "timeout"):
        """Simulate API errors."""
        if error_type == "timeout":
            raise TimeoutError("MusicBrainz API timeout")
        elif error_type == "rate_limit":
            raise Exception("Rate limit exceeded")
        elif error_type == "not_found":
            return {"recordings": [], "count": 0, "offset": 0}
    
    def _generate_isrc(self) -> str:
        """Generate a valid ISRC code."""
        country = fake.country_code()
        registrant = fake.lexify(text="???").upper()
        year = fake.random_int(min=0, max=99)
        designation = fake.random_int(min=1, max=99999)
        return f"{country}{registrant}{year:02d}{designation:05d}"
    
    def reset(self):
        """Reset mock state."""
        self.responses.clear()
        self.call_count = 0
        self.last_request = None


class AWSServiceMockService:
    """Mock service for AWS services."""
    
    def __init__(self):
        self.s3_mock = self._create_s3_mock()
        self.sqs_mock = self._create_sqs_mock()
        self.lambda_mock = self._create_lambda_mock()
        self.call_logs = []
    
    def _create_s3_mock(self) -> Mock:
        """Create S3 mock."""
        mock = Mock()
        
        # Upload operations
        mock.upload_fileobj.return_value = None
        mock.upload_file.return_value = None
        mock.put_object.return_value = {
            'ETag': f'"{fake.md5()}"',
            'VersionId': str(uuid.uuid4())
        }
        
        # Download operations
        mock.download_fileobj.return_value = None
        mock.download_file.return_value = None
        mock.get_object.return_value = {
            'Body': Mock(read=lambda: b'fake file content'),
            'ContentLength': random.randint(1000, 100000000),
            'LastModified': fake.date_time(),
            'ETag': f'"{fake.md5()}"'
        }
        
        # Metadata operations
        mock.head_object.return_value = {
            'ContentLength': random.randint(1000, 100000000),
            'LastModified': fake.date_time(),
            'ETag': f'"{fake.md5()}"',
            'ContentType': 'audio/mpeg'
        }
        
        # List operations
        mock.list_objects_v2.return_value = {
            'Contents': [
                {
                    'Key': f'audio/track_{i}.mp3',
                    'Size': random.randint(5000000, 50000000),
                    'LastModified': fake.date_time(),
                    'ETag': f'"{fake.md5()}"'
                }
                for i in range(5)
            ],
            'KeyCount': 5,
            'IsTruncated': False
        }
        
        # Delete operations
        mock.delete_object.return_value = {'DeleteMarker': True}
        mock.delete_objects.return_value = {
            'Deleted': [{'Key': f'file_{i}.mp3'} for i in range(3)]
        }
        
        return mock
    
    def _create_sqs_mock(self) -> Mock:
        """Create SQS mock."""
        mock = Mock()
        
        # Send message
        mock.send_message.return_value = {
            'MessageId': str(uuid.uuid4()),
            'MD5OfBody': fake.md5(),
            'MD5OfMessageAttributes': fake.md5()
        }
        
        # Receive messages
        mock.receive_message.return_value = {
            'Messages': [
                {
                    'MessageId': str(uuid.uuid4()),
                    'ReceiptHandle': fake.uuid4(),
                    'Body': json.dumps({
                        'release_id': str(uuid.uuid4()),
                        'action': 'process_delivery',
                        'timestamp': datetime.utcnow().isoformat()
                    }),
                    'Attributes': {
                        'SentTimestamp': str(int(datetime.utcnow().timestamp() * 1000))
                    }
                }
            ]
        }
        
        # Delete message
        mock.delete_message.return_value = {}
        
        return mock
    
    def _create_lambda_mock(self) -> Mock:
        """Create Lambda mock."""
        mock = Mock()
        
        # Invoke function
        mock.invoke.return_value = {
            'StatusCode': 200,
            'Payload': Mock(read=lambda: json.dumps({
                'statusCode': 200,
                'body': json.dumps({'result': 'success'})
            }).encode())
        }
        
        return mock
    
    def setup_s3_error(self, operation: str, error_type: str = "NoSuchKey"):
        """Setup S3 error simulation."""
        from botocore.exceptions import ClientError
        
        error = ClientError(
            error_response={
                'Error': {
                    'Code': error_type,
                    'Message': f'Mock {error_type} error'
                }
            },
            operation_name=operation
        )
        
        if operation == "upload_fileobj":
            self.s3_mock.upload_fileobj.side_effect = error
        elif operation == "get_object":
            self.s3_mock.get_object.side_effect = error
        elif operation == "head_object":
            self.s3_mock.head_object.side_effect = error
    
    def log_call(self, service: str, operation: str, **kwargs):
        """Log service call."""
        self.call_logs.append({
            'service': service,
            'operation': operation,
            'timestamp': datetime.utcnow(),
            'params': kwargs
        })
    
    def get_call_count(self, service: str, operation: str = None) -> int:
        """Get call count for service/operation."""
        calls = [log for log in self.call_logs if log['service'] == service]
        if operation:
            calls = [log for log in calls if log['operation'] == operation]
        return len(calls)
    
    def reset(self):
        """Reset mock state."""
        self.call_logs.clear()
        self.s3_mock.reset_mock()
        self.sqs_mock.reset_mock()
        self.lambda_mock.reset_mock()


class PartnerAPIMockService:
    """Mock service for partner API integrations."""
    
    def __init__(self):
        self.partner_responses = {}
        self.delivery_statuses = {}
        self.call_logs = []
    
    def setup_partner_response(self, partner_id: str, success: bool = True, 
                             delivery_id: str = None, error_code: str = None):
        """Setup mock response for partner API."""
        if not delivery_id:
            delivery_id = str(uuid.uuid4())
        
        if success:
            response = {
                'status': 'success',
                'delivery_id': delivery_id,
                'message': 'Release delivered successfully',
                'timestamp': datetime.utcnow().isoformat(),
                'tracking_url': f'https://partner.example.com/delivery/{delivery_id}'
            }
        else:
            response = {
                'status': 'error',
                'error_code': error_code or 'VALIDATION_FAILED',
                'message': 'Delivery failed due to validation errors',
                'timestamp': datetime.utcnow().isoformat(),
                'details': {
                    'missing_fields': ['artwork', 'isrc'],
                    'invalid_fields': ['release_date']
                }
            }
        
        self.partner_responses[partner_id] = response
        return response
    
    def setup_delivery_status(self, delivery_id: str, status: str = "delivered"):
        """Setup delivery status response."""
        self.delivery_statuses[delivery_id] = {
            'delivery_id': delivery_id,
            'status': status,
            'updated_at': datetime.utcnow().isoformat(),
            'metadata': {
                'platform_id': fake.uuid4(),
                'live_date': fake.date_time().isoformat() if status == 'live' else None
            }
        }
    
    def get_delivery_response(self, partner_id: str, release_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get mock delivery response."""
        self.log_call('delivery', partner_id, release_data)
        
        if partner_id in self.partner_responses:
            return self.partner_responses[partner_id]
        
        # Default success response
        return {
            'status': 'success',
            'delivery_id': str(uuid.uuid4()),
            'message': 'Release delivered successfully',
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def get_status_response(self, delivery_id: str) -> Dict[str, Any]:
        """Get mock status response."""
        self.log_call('status_check', delivery_id)
        
        if delivery_id in self.delivery_statuses:
            return self.delivery_statuses[delivery_id]
        
        # Default status response
        return {
            'delivery_id': delivery_id,
            'status': random.choice(['processing', 'delivered', 'live', 'failed']),
            'updated_at': datetime.utcnow().isoformat()
        }
    
    def simulate_webhook(self, delivery_id: str, status: str = "live") -> Dict[str, Any]:
        """Simulate webhook payload."""
        return {
            'event': 'delivery_status_changed',
            'delivery_id': delivery_id,
            'status': status,
            'timestamp': datetime.utcnow().isoformat(),
            'data': {
                'platform_id': fake.uuid4(),
                'live_date': datetime.utcnow().isoformat() if status == 'live' else None,
                'error_message': 'Validation failed' if status == 'failed' else None
            }
        }
    
    def simulate_rate_limit(self, partner_id: str):
        """Simulate rate limiting."""
        self.partner_responses[partner_id] = {
            'status': 'error',
            'error_code': 'RATE_LIMIT_EXCEEDED',
            'message': 'Too many requests',
            'retry_after': 3600,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def log_call(self, operation: str, *args, **kwargs):
        """Log API call."""
        self.call_logs.append({
            'operation': operation,
            'args': args,
            'kwargs': kwargs,
            'timestamp': datetime.utcnow()
        })
    
    def get_call_count(self, operation: str = None) -> int:
        """Get call count."""
        if operation:
            return len([log for log in self.call_logs if log['operation'] == operation])
        return len(self.call_logs)
    
    def reset(self):
        """Reset mock state."""
        self.partner_responses.clear()
        self.delivery_statuses.clear()
        self.call_logs.clear()


class CeleryMockService:
    """Mock service for Celery task execution."""
    
    def __init__(self):
        self.task_results = {}
        self.task_calls = []
        self.task_states = {}
    
    def setup_task_result(self, task_name: str, result: Any = None, 
                         status: str = "SUCCESS", task_id: str = None):
        """Setup mock task result."""
        if not task_id:
            task_id = str(uuid.uuid4())
        
        self.task_results[task_name] = {
            'id': task_id,
            'status': status,
            'result': result or {'message': 'Task completed successfully'},
            'traceback': None if status == "SUCCESS" else "Mock traceback",
            'date_done': datetime.utcnow().isoformat()
        }
        
        return task_id
    
    def create_mock_task(self, task_name: str):
        """Create a mock Celery task."""
        mock_task = Mock()
        
        def delay_side_effect(*args, **kwargs):
            self.log_task_call(task_name, args, kwargs)
            
            # Get or create task result
            if task_name in self.task_results:
                result_data = self.task_results[task_name]
            else:
                result_data = self.setup_task_result(task_name)
            
            # Create mock AsyncResult
            mock_result = Mock()
            mock_result.id = result_data['id']
            mock_result.status = result_data['status']
            mock_result.result = result_data['result']
            mock_result.successful.return_value = result_data['status'] == "SUCCESS"
            mock_result.failed.return_value = result_data['status'] == "FAILURE"
            mock_result.ready.return_value = True
            mock_result.get.return_value = result_data['result']
            
            return mock_result
        
        mock_task.delay.side_effect = delay_side_effect
        mock_task.apply_async.side_effect = delay_side_effect
        
        return mock_task
    
    def log_task_call(self, task_name: str, args: tuple, kwargs: dict):
        """Log task call."""
        self.task_calls.append({
            'task_name': task_name,
            'args': args,
            'kwargs': kwargs,
            'timestamp': datetime.utcnow()
        })
    
    def get_task_call_count(self, task_name: str = None) -> int:
        """Get task call count."""
        if task_name:
            return len([call for call in self.task_calls if call['task_name'] == task_name])
        return len(self.task_calls)
    
    def simulate_task_failure(self, task_name: str, error_message: str = "Task failed"):
        """Simulate task failure."""
        self.setup_task_result(
            task_name=task_name,
            result={'error': error_message},
            status="FAILURE"
        )
    
    def reset(self):
        """Reset mock state."""
        self.task_results.clear()
        self.task_calls.clear()
        self.task_states.clear()


class EmailMockService:
    """Mock service for email notifications."""
    
    def __init__(self):
        self.sent_emails = []
        self.email_templates = {}
    
    def setup_template(self, template_name: str, subject: str, body: str):
        """Setup email template."""
        self.email_templates[template_name] = {
            'subject': subject,
            'body': body
        }
    
    def send_email(self, to: str, subject: str, body: str, 
                  template: str = None, **kwargs) -> str:
        """Mock send email."""
        email_id = str(uuid.uuid4())
        
        email_data = {
            'id': email_id,
            'to': to,
            'subject': subject,
            'body': body,
            'template': template,
            'timestamp': datetime.utcnow(),
            'status': 'sent',
            'kwargs': kwargs
        }
        
        self.sent_emails.append(email_data)
        return email_id
    
    def get_sent_emails(self, to: str = None, template: str = None) -> List[Dict[str, Any]]:
        """Get sent emails with optional filtering."""
        emails = self.sent_emails
        
        if to:
            emails = [email for email in emails if email['to'] == to]
        
        if template:
            emails = [email for email in emails if email['template'] == template]
        
        return emails
    
    def get_email_count(self, to: str = None, template: str = None) -> int:
        """Get count of sent emails."""
        return len(self.get_sent_emails(to, template))
    
    def simulate_delivery_failure(self, email_id: str):
        """Simulate email delivery failure."""
        for email in self.sent_emails:
            if email['id'] == email_id:
                email['status'] = 'failed'
                email['error'] = 'Delivery failed'
                break
    
    def reset(self):
        """Reset mock state."""
        self.sent_emails.clear()
        self.email_templates.clear()


# Global mock service manager instance
mock_service_manager = MockServiceManager()

# Pre-configured mock services
musicbrainz_mock = MusicBrainzMockService()
aws_mock = AWSServiceMockService()
partner_api_mock = PartnerAPIMockService()
celery_mock = CeleryMockService()
email_mock = EmailMockService()

# Register all mock services
mock_service_manager.register_mock('musicbrainz', musicbrainz_mock)
mock_service_manager.register_mock('aws', aws_mock)
mock_service_manager.register_mock('partner_api', partner_api_mock)
mock_service_manager.register_mock('celery', celery_mock)
mock_service_manager.register_mock('email', email_mock)


# Convenience functions for common mock setups
def setup_successful_musicbrainz_response(query: str, title: str = None, artist: str = None):
    """Setup successful MusicBrainz response."""
    recording = {
        "id": str(uuid.uuid4()),
        "title": title or fake.catch_phrase(),
        "artist-credit": [{"artist": {"name": artist or fake.name()}}],
        "length": random.randint(120000, 480000),
        "isrcs": [f"US{fake.lexify(text='???').upper()}{fake.random_number(digits=8)}"]
    }
    musicbrainz_mock.setup_recording_response(query, [recording])
    return recording


def setup_successful_partner_delivery(partner_id: str, delivery_id: str = None):
    """Setup successful partner delivery response."""
    return partner_api_mock.setup_partner_response(
        partner_id=partner_id,
        success=True,
        delivery_id=delivery_id
    )


def setup_failed_partner_delivery(partner_id: str, error_code: str = "VALIDATION_FAILED"):
    """Setup failed partner delivery response."""
    return partner_api_mock.setup_partner_response(
        partner_id=partner_id,
        success=False,
        error_code=error_code
    )


def reset_all_mocks():
    """Reset all mock services."""
    mock_service_manager.reset_all_mocks()
    musicbrainz_mock.reset()
    aws_mock.reset()
    partner_api_mock.reset()
    celery_mock.reset()
    email_mock.reset()