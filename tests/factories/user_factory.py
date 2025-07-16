"""
User factory for generating test user data.
"""
import factory
from faker import Faker
from datetime import datetime, timedelta
import random

from app.models.user import User, UserRole, APIKey

fake = Faker()


class UserFactoryBase(factory.Factory):
    """Factory for creating test User instances."""
    
    class Meta:
        model = User
    
    # Basic user info
    email = factory.LazyAttribute(lambda obj: fake.email())
    username = factory.LazyAttribute(lambda obj: fake.user_name())
    full_name = factory.LazyAttribute(lambda obj: fake.name())
    
    # Authentication
    hashed_password = factory.LazyAttribute(lambda obj: fake.password(length=60))  # Simulates bcrypt hash
    is_active = True
    is_superuser = False
    role = UserRole.VIEWER
    
    # Profile
    company = factory.LazyAttribute(lambda obj: fake.company())
    phone = factory.LazyAttribute(lambda obj: fake.phone_number())
    avatar_url = factory.LazyAttribute(lambda obj: fake.image_url())
    
    # Settings
    timezone = factory.LazyAttribute(lambda obj: fake.timezone())
    preferences = factory.LazyAttribute(lambda obj: {
        "theme": random.choice(["light", "dark"]),
        "notifications": random.choice([True, False]),
        "language": random.choice(["en", "es", "fr", "de"])
    })
    
    # Timestamps
    created_at = factory.LazyAttribute(lambda obj: fake.date_time_between(start_date="-1y", end_date="now"))
    updated_at = factory.LazyAttribute(lambda obj: fake.date_time_between(start_date=obj.created_at, end_date="now"))
    last_login = factory.LazyAttribute(lambda obj: fake.date_time_between(start_date=obj.created_at, end_date="now"))


class AdminUserFactory(UserFactoryBase):
    """Factory for creating admin users."""
    
    is_superuser = True
    role = UserRole.ADMIN
    email = factory.LazyAttribute(lambda obj: f"admin.{fake.user_name()}@example.com")


class ManagerUserFactory(UserFactoryBase):
    """Factory for creating manager users."""
    
    role = UserRole.MANAGER
    email = factory.LazyAttribute(lambda obj: f"manager.{fake.user_name()}@example.com")


class DeveloperUserFactory(UserFactoryBase):
    """Factory for creating developer users."""
    
    role = UserRole.DEVELOPER
    email = factory.LazyAttribute(lambda obj: f"dev.{fake.user_name()}@example.com")


class InactiveUserFactory(UserFactoryBase):
    """Factory for creating inactive users."""
    
    is_active = False
    last_login = None


class APIKeyFactory(factory.Factory):
    """Factory for creating test API Key instances."""
    
    class Meta:
        model = APIKey
    
    # API Key info
    name = factory.LazyAttribute(lambda obj: f"{fake.word().title()} API Key")
    key_hash = factory.LazyAttribute(lambda obj: fake.sha256())
    prefix = factory.LazyAttribute(lambda obj: fake.lexify(text="ak_????????").upper())
    
    # Permissions
    is_active = True
    permissions = factory.LazyAttribute(lambda obj: random.sample([
        "read:releases", "write:releases", "delete:releases",
        "read:users", "write:users", "read:analytics",
        "manage:partners", "manage:deliveries"
    ], k=random.randint(1, 4)))
    rate_limit_requests = factory.LazyAttribute(lambda obj: random.choice([100, 500, 1000, 5000]))
    rate_limit_window = 3600  # 1 hour
    
    # Usage tracking
    last_used = factory.LazyAttribute(lambda obj: fake.date_time_between(start_date="-30d", end_date="now"))
    usage_count = factory.LazyAttribute(lambda obj: random.randint(0, 1000))
    
    # Timestamps
    created_at = factory.LazyAttribute(lambda obj: fake.date_time_between(start_date="-6m", end_date="now"))
    updated_at = factory.LazyAttribute(lambda obj: fake.date_time_between(start_date=obj.created_at, end_date="now"))
    expires_at = factory.LazyAttribute(lambda obj: fake.date_time_between(start_date="now", end_date="+1y"))


class ExpiredAPIKeyFactory(APIKeyFactory):
    """Factory for creating expired API keys."""
    
    expires_at = factory.LazyAttribute(lambda obj: fake.date_time_between(start_date="-1y", end_date="-1d"))
    is_active = False


class HighUsageAPIKeyFactory(APIKeyFactory):
    """Factory for creating high-usage API keys."""
    
    usage_count = factory.LazyAttribute(lambda obj: random.randint(5000, 50000))
    rate_limit_requests = 10000
    permissions = [
        "read:releases", "write:releases", "delete:releases",
        "read:users", "write:users", "read:analytics",
        "manage:partners", "manage:deliveries"
    ]


# Utility functions for creating users with relationships
def create_user_with_api_keys(session, user_factory=UserFactoryBase, num_keys=2):
    """Create a user with associated API keys."""
    user = user_factory()
    session.add(user)
    session.flush()  # Get the user ID
    
    api_keys = []
    for _ in range(num_keys):
        api_key = APIKeyFactory(user_id=user.id)
        session.add(api_key)
        api_keys.append(api_key)
    
    session.commit()
    return user, api_keys


def create_test_user_set(session):
    """Create a complete set of test users for comprehensive testing."""
    users = {}
    
    # Create different types of users
    users['admin'] = AdminUserFactory()
    users['manager'] = ManagerUserFactory()
    users['developer'] = DeveloperUserFactory()
    users['viewer'] = UserFactoryBase()
    users['inactive'] = InactiveUserFactory()
    
    # Add all users to session
    for user in users.values():
        session.add(user)
    
    session.commit()
    return users


def create_user_with_specific_permissions(session, permissions_list):
    """Create a user with specific API key permissions."""
    user = UserFactoryBase()
    session.add(user)
    session.flush()
    
    api_key = APIKeyFactory(
        user_id=user.id,
        permissions=permissions_list
    )
    session.add(api_key)
    session.commit()
    
    return user, api_key


class UserFactory:
    """Factory class for creating test users."""
    
    @staticmethod
    def create_user(session, email=None, password=None, is_active=True, role=UserRole.VIEWER, **kwargs):
        """Create a user with specified parameters."""
        from app.core.security import get_password_hash
        
        if email is None:
            email = fake.email()
        if password is None:
            password = "testpassword123"
        
        user_data = {
            "email": email,
            "username": kwargs.get("username", fake.user_name()),
            "full_name": kwargs.get("full_name", fake.name()),
            "hashed_password": get_password_hash(password),
            "is_active": is_active,
            "is_superuser": kwargs.get("is_superuser", False),
            "role": role,
            "company": kwargs.get("company", fake.company()),
            "phone": kwargs.get("phone", fake.phone_number()),
            "avatar_url": kwargs.get("avatar_url", fake.image_url()),
            "timezone": kwargs.get("timezone", "UTC"),
            "preferences": kwargs.get("preferences", {}),
            "created_at": fake.date_time_between(start_date="-1y", end_date="now"),
            "updated_at": fake.date_time_between(start_date="-1y", end_date="now"),
            "last_login": kwargs.get("last_login", fake.date_time_between(start_date="-30d", end_date="now"))
        }
        
        user = User(**user_data)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user