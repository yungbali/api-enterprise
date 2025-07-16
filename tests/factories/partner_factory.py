"""
Partner factory for generating test partner data.
"""
import factory
from faker import Faker
from datetime import datetime, timedelta
import random
import uuid

from app.models.partner import DeliveryPartner, PartnerStatus, PartnerType, AuthType, PartnerConfig

fake = Faker()


class DeliveryPartnerFactory(factory.Factory):
    """Factory for creating test DeliveryPartner instances."""
    
    class Meta:
        model = DeliveryPartner
    
    # Basic partner info
    partner_id = factory.LazyAttribute(lambda obj: f"PARTNER-{uuid.uuid4().hex[:8].upper()}")
    name = factory.LazyAttribute(lambda obj: f"{fake.company()} Music")
    display_name = factory.LazyAttribute(lambda obj: obj.name)
    
    # Partner info
    partner_type = factory.LazyAttribute(lambda obj: random.choice(list(PartnerType)))
    description = factory.LazyAttribute(lambda obj: fake.text(max_nb_chars=300))
    website = factory.LazyAttribute(lambda obj: fake.url())
    contact_email = factory.LazyAttribute(lambda obj: fake.company_email())
    
    # API Configuration
    api_base_url = factory.LazyAttribute(lambda obj: f"https://api.{fake.domain_name()}")
    api_version = factory.LazyAttribute(lambda obj: random.choice(["v1", "v2", "v3", "2023-01", "2024-01"]))
    auth_type = factory.LazyAttribute(lambda obj: random.choice(list(AuthType)))
    
    # Delivery settings
    delivery_url = factory.LazyAttribute(lambda obj: f"{obj.api_base_url}/delivery")
    callback_url = factory.LazyAttribute(lambda obj: f"{obj.api_base_url}/callback")
    supported_formats = factory.LazyAttribute(lambda obj: random.sample([
        "mp3", "wav", "flac", "aac", "ogg", "m4a"
    ], k=random.randint(2, 4)))
    supported_territories = factory.LazyAttribute(lambda obj: random.sample([
        "US", "GB", "DE", "FR", "CA", "AU", "JP", "BR", "MX", "ES", "IT", "NL", "SE", "NO", "DK", "WW"
    ], k=random.randint(3, 8)))
    
    # Status and configuration
    status = PartnerStatus.ACTIVE
    priority = factory.LazyAttribute(lambda obj: random.randint(1, 10))
    auto_deliver = True
    
    # Rate limiting
    rate_limit_requests = factory.LazyAttribute(lambda obj: random.choice([50, 100, 200, 500, 1000]))
    rate_limit_window = 3600  # 1 hour
    
    # Timestamps
    created_at = factory.LazyAttribute(lambda obj: fake.date_time_between(start_date="-2y", end_date="now"))
    updated_at = factory.LazyAttribute(lambda obj: fake.date_time_between(start_date=obj.created_at, end_date="now"))
    last_health_check = factory.LazyAttribute(lambda obj: fake.date_time_between(start_date="-7d", end_date="now"))


class DSPPartnerFactory(DeliveryPartnerFactory):
    """Factory for Digital Service Provider partners."""
    
    partner_type = PartnerType.DSP
    name = factory.LazyAttribute(lambda obj: f"{fake.word().title()}ify")
    supported_formats = ["mp3", "aac", "flac"]
    supported_territories = ["US", "GB", "DE", "FR", "CA", "AU", "WW"]
    priority = factory.LazyAttribute(lambda obj: random.randint(7, 10))  # High priority


class AggregatorPartnerFactory(DeliveryPartnerFactory):
    """Factory for Aggregator partners."""
    
    partner_type = PartnerType.AGGREGATOR
    name = factory.LazyAttribute(lambda obj: f"{fake.word().title()} Distribution")
    supported_formats = ["mp3", "wav", "flac", "aac"]
    supported_territories = ["WW"]  # Worldwide
    priority = factory.LazyAttribute(lambda obj: random.randint(5, 8))


class DistributorPartnerFactory(DeliveryPartnerFactory):
    """Factory for Distributor partners."""
    
    partner_type = PartnerType.DISTRIBUTOR
    name = factory.LazyAttribute(lambda obj: f"{fake.word().title()} Records Distribution")
    supported_formats = ["mp3", "wav", "flac"]
    priority = factory.LazyAttribute(lambda obj: random.randint(3, 7))


class PlatformPartnerFactory(DeliveryPartnerFactory):
    """Factory for Platform partners."""
    
    partner_type = PartnerType.PLATFORM
    name = factory.LazyAttribute(lambda obj: f"{fake.word().title()} Platform")
    supported_formats = ["mp3", "aac"]
    priority = factory.LazyAttribute(lambda obj: random.randint(1, 5))


class InactivePartnerFactory(DeliveryPartnerFactory):
    """Factory for inactive partners."""
    
    status = PartnerStatus.INACTIVE
    auto_deliver = False
    last_health_check = factory.LazyAttribute(lambda obj: fake.date_time_between(start_date="-30d", end_date="-7d"))


class PendingPartnerFactory(DeliveryPartnerFactory):
    """Factory for pending partners."""
    
    status = PartnerStatus.PENDING
    auto_deliver = False
    last_health_check = None


class SuspendedPartnerFactory(DeliveryPartnerFactory):
    """Factory for suspended partners."""
    
    status = PartnerStatus.SUSPENDED
    auto_deliver = False


class APIKeyAuthPartnerFactory(DeliveryPartnerFactory):
    """Factory for API key authenticated partners."""
    
    auth_type = AuthType.API_KEY


class OAuth2PartnerFactory(DeliveryPartnerFactory):
    """Factory for OAuth2 authenticated partners."""
    
    auth_type = AuthType.OAUTH2


class BasicAuthPartnerFactory(DeliveryPartnerFactory):
    """Factory for Basic Auth partners."""
    
    auth_type = AuthType.BASIC_AUTH


class BearerTokenPartnerFactory(DeliveryPartnerFactory):
    """Factory for Bearer Token authenticated partners."""
    
    auth_type = AuthType.BEARER_TOKEN


class PartnerConfigFactory(factory.Factory):
    """Factory for creating test PartnerConfig instances."""
    
    class Meta:
        model = PartnerConfig
    
    # Configuration
    config_key = factory.LazyAttribute(lambda obj: random.choice([
        "api_key", "client_id", "client_secret", "username", "password",
        "webhook_secret", "encryption_key", "base_url", "timeout",
        "retry_attempts", "batch_size", "format_preference"
    ]))
    config_value = factory.LazyAttribute(lambda obj: _generate_config_value(obj.config_key))
    config_type = factory.LazyAttribute(lambda obj: _get_config_type(obj.config_key))
    
    # Metadata
    description = factory.LazyAttribute(lambda obj: f"Configuration for {obj.config_key}")
    is_sensitive = factory.LazyAttribute(lambda obj: _is_sensitive_config(obj.config_key))
    is_required = factory.LazyAttribute(lambda obj: random.choice([True, False]))
    
    # Timestamps
    created_at = factory.LazyAttribute(lambda obj: fake.date_time_between(start_date="-1y", end_date="now"))
    updated_at = factory.LazyAttribute(lambda obj: fake.date_time_between(start_date=obj.created_at, end_date="now"))


class APIKeyConfigFactory(PartnerConfigFactory):
    """Factory for API key configuration."""
    
    config_key = "api_key"
    config_value = factory.LazyAttribute(lambda obj: fake.uuid4())
    config_type = "string"
    is_sensitive = True
    is_required = True


class ClientCredentialsConfigFactory(PartnerConfigFactory):
    """Factory for OAuth2 client credentials."""
    
    config_key = factory.LazyAttribute(lambda obj: random.choice(["client_id", "client_secret"]))
    config_value = factory.LazyAttribute(lambda obj: fake.uuid4() if obj.config_key == "client_secret" else fake.lexify(text="client_????????"))
    config_type = "string"
    is_sensitive = factory.LazyAttribute(lambda obj: obj.config_key == "client_secret")
    is_required = True


class WebhookSecretConfigFactory(PartnerConfigFactory):
    """Factory for webhook secret configuration."""
    
    config_key = "webhook_secret"
    config_value = factory.LazyAttribute(lambda obj: fake.sha256())
    config_type = "string"
    is_sensitive = True
    is_required = True


class TimeoutConfigFactory(PartnerConfigFactory):
    """Factory for timeout configuration."""
    
    config_key = "timeout"
    config_value = factory.LazyAttribute(lambda obj: str(random.randint(5, 60)))
    config_type = "integer"
    is_sensitive = False
    is_required = False


class BatchSizeConfigFactory(PartnerConfigFactory):
    """Factory for batch size configuration."""
    
    config_key = "batch_size"
    config_value = factory.LazyAttribute(lambda obj: str(random.randint(1, 100)))
    config_type = "integer"
    is_sensitive = False
    is_required = False


# Helper functions
def _generate_config_value(config_key):
    """Generate appropriate config value based on key."""
    value_generators = {
        "api_key": lambda: fake.uuid4(),
        "client_id": lambda: fake.lexify(text="client_????????"),
        "client_secret": lambda: fake.uuid4(),
        "username": lambda: fake.user_name(),
        "password": lambda: fake.password(),
        "webhook_secret": lambda: fake.sha256(),
        "encryption_key": lambda: fake.sha256(),
        "base_url": lambda: fake.url(),
        "timeout": lambda: str(random.randint(5, 60)),
        "retry_attempts": lambda: str(random.randint(1, 5)),
        "batch_size": lambda: str(random.randint(1, 100)),
        "format_preference": lambda: random.choice(["mp3", "wav", "flac"])
    }
    
    generator = value_generators.get(config_key, lambda: fake.word())
    return generator()


def _get_config_type(config_key):
    """Get appropriate config type based on key."""
    type_mapping = {
        "timeout": "integer",
        "retry_attempts": "integer",
        "batch_size": "integer",
        "format_preference": "string",
        "base_url": "string"
    }
    return type_mapping.get(config_key, "string")


def _is_sensitive_config(config_key):
    """Determine if config key contains sensitive data."""
    sensitive_keys = [
        "api_key", "client_secret", "password", "webhook_secret", 
        "encryption_key", "private_key", "token"
    ]
    return any(sensitive in config_key.lower() for sensitive in sensitive_keys)


# Utility functions for creating partners with relationships
def create_partner_with_configs(session, partner_factory=DeliveryPartnerFactory, num_configs=3):
    """Create a partner with associated configurations."""
    partner = partner_factory()
    session.add(partner)
    session.flush()  # Get the partner ID
    
    configs = []
    
    # Always add required configs based on auth type
    if partner.auth_type == AuthType.API_KEY:
        api_key_config = APIKeyConfigFactory(partner_id=partner.id)
        session.add(api_key_config)
        configs.append(api_key_config)
    elif partner.auth_type == AuthType.OAUTH2:
        client_id_config = ClientCredentialsConfigFactory(partner_id=partner.id, config_key="client_id")
        client_secret_config = ClientCredentialsConfigFactory(partner_id=partner.id, config_key="client_secret")
        session.add(client_id_config)
        session.add(client_secret_config)
        configs.extend([client_id_config, client_secret_config])
    elif partner.auth_type == AuthType.BASIC_AUTH:
        username_config = PartnerConfigFactory(partner_id=partner.id, config_key="username")
        password_config = PartnerConfigFactory(partner_id=partner.id, config_key="password")
        session.add(username_config)
        session.add(password_config)
        configs.extend([username_config, password_config])
    
    # Add additional configs
    additional_configs = ["webhook_secret", "timeout", "batch_size"]
    for config_key in additional_configs[:num_configs - len(configs)]:
        config = PartnerConfigFactory(partner_id=partner.id, config_key=config_key)
        session.add(config)
        configs.append(config)
    
    session.commit()
    return partner, configs


def create_complete_partner_set(session):
    """Create a comprehensive set of partners for testing."""
    partners = {}
    
    # Different types of partners
    partners['dsp'] = DSPPartnerFactory()
    partners['aggregator'] = AggregatorPartnerFactory()
    partners['distributor'] = DistributorPartnerFactory()
    partners['platform'] = PlatformPartnerFactory()
    
    # Different status partners
    partners['active'] = DeliveryPartnerFactory()
    partners['inactive'] = InactivePartnerFactory()
    partners['pending'] = PendingPartnerFactory()
    partners['suspended'] = SuspendedPartnerFactory()
    
    # Different auth types
    partners['api_key_auth'] = APIKeyAuthPartnerFactory()
    partners['oauth2_auth'] = OAuth2PartnerFactory()
    partners['basic_auth'] = BasicAuthPartnerFactory()
    partners['bearer_auth'] = BearerTokenPartnerFactory()
    
    # Add all partners to session
    for partner in partners.values():
        session.add(partner)
    
    session.commit()
    return partners


def create_partner_with_full_config(session, partner_type=PartnerType.DSP, auth_type=AuthType.API_KEY):
    """Create a partner with complete configuration set."""
    if partner_type == PartnerType.DSP:
        partner = DSPPartnerFactory(auth_type=auth_type)
    elif partner_type == PartnerType.AGGREGATOR:
        partner = AggregatorPartnerFactory(auth_type=auth_type)
    elif partner_type == PartnerType.DISTRIBUTOR:
        partner = DistributorPartnerFactory(auth_type=auth_type)
    else:
        partner = PlatformPartnerFactory(auth_type=auth_type)
    
    session.add(partner)
    session.flush()
    
    # Create comprehensive config set
    configs = []
    
    # Auth-specific configs
    if auth_type == AuthType.API_KEY:
        configs.append(APIKeyConfigFactory(partner_id=partner.id))
    elif auth_type == AuthType.OAUTH2:
        configs.append(ClientCredentialsConfigFactory(partner_id=partner.id, config_key="client_id"))
        configs.append(ClientCredentialsConfigFactory(partner_id=partner.id, config_key="client_secret"))
    elif auth_type == AuthType.BASIC_AUTH:
        configs.append(PartnerConfigFactory(partner_id=partner.id, config_key="username"))
        configs.append(PartnerConfigFactory(partner_id=partner.id, config_key="password"))
    elif auth_type == AuthType.BEARER_TOKEN:
        configs.append(PartnerConfigFactory(partner_id=partner.id, config_key="bearer_token"))
    
    # Common configs
    configs.append(WebhookSecretConfigFactory(partner_id=partner.id))
    configs.append(TimeoutConfigFactory(partner_id=partner.id))
    configs.append(BatchSizeConfigFactory(partner_id=partner.id))
    
    # Add all configs to session
    for config in configs:
        session.add(config)
    
    session.commit()
    return partner, configs


def create_high_priority_partners(session, count=3):
    """Create high-priority partners for testing delivery prioritization."""
    partners = []
    
    for i in range(count):
        partner = DSPPartnerFactory(
            priority=random.randint(8, 10),
            auto_deliver=True,
            status=PartnerStatus.ACTIVE
        )
        session.add(partner)
        partners.append(partner)
    
    session.commit()
    return partners


def create_partners_by_territory(session, territory="US"):
    """Create partners that support a specific territory."""
    partners = []
    
    # Create different types of partners supporting the territory
    for partner_type in [PartnerType.DSP, PartnerType.AGGREGATOR, PartnerType.DISTRIBUTOR]:
        if partner_type == PartnerType.DSP:
            partner = DSPPartnerFactory(supported_territories=[territory, "WW"])
        elif partner_type == PartnerType.AGGREGATOR:
            partner = AggregatorPartnerFactory(supported_territories=[territory, "WW"])
        else:
            partner = DistributorPartnerFactory(supported_territories=[territory, "WW"])
        
        session.add(partner)
        partners.append(partner)
    
    session.commit()
    return partners


class PartnerFactory:
    """Factory class for creating test partners."""
    
    @staticmethod
    def create_partner(session, name=None, partner_type=PartnerType.DSP, **kwargs):
        """Create a partner with specified parameters."""
        import uuid
        
        if name is None:
            name = f"{fake.company()} Music"
        
        partner_data = {
            "partner_id": f"PARTNER-{uuid.uuid4().hex[:8].upper()}",
            "name": name,
            "display_name": kwargs.get("display_name", name),
            "partner_type": partner_type,
            "description": kwargs.get("description", fake.text(max_nb_chars=300)),
            "website": kwargs.get("website", fake.url()),
            "contact_email": kwargs.get("contact_email", fake.company_email()),
            "api_base_url": kwargs.get("api_base_url", f"https://api.{fake.domain_name()}"),
            "api_version": kwargs.get("api_version", random.choice(["v1", "v2", "v3"])),
            "auth_type": kwargs.get("auth_type", random.choice(list(AuthType))),
            "delivery_url": kwargs.get("delivery_url"),
            "callback_url": kwargs.get("callback_url"),
            "supported_formats": kwargs.get("supported_formats", ["mp3", "wav", "flac"]),
            "supported_territories": kwargs.get("supported_territories", ["US", "GB", "WW"]),
            "status": kwargs.get("status", PartnerStatus.ACTIVE),
            "priority": kwargs.get("priority", random.randint(1, 10)),
            "auto_deliver": kwargs.get("auto_deliver", True),
            "rate_limit_requests": kwargs.get("rate_limit_requests", 100),
            "rate_limit_window": kwargs.get("rate_limit_window", 3600),
            "created_at": fake.date_time_between(start_date="-2y", end_date="now"),
            "updated_at": fake.date_time_between(start_date="-2y", end_date="now"),
            "last_health_check": fake.date_time_between(start_date="-7d", end_date="now")
        }
        
        # Set delivery_url and callback_url if not provided
        if not partner_data["delivery_url"]:
            partner_data["delivery_url"] = f"{partner_data['api_base_url']}/delivery"
        if not partner_data["callback_url"]:
            partner_data["callback_url"] = f"{partner_data['api_base_url']}/callback"
        
        partner = DeliveryPartner(**partner_data)
        session.add(partner)
        session.commit()
        session.refresh(partner)
        return partner