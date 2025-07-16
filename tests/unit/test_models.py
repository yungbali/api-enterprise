"""
Unit tests for SQLAlchemy models.
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import User, APIKey, UserRole
from app.models.release import Release, Track, ReleaseAsset, ReleaseStatus, ReleaseType, AssetType
from app.models.partner import DeliveryPartner, PartnerConfig, PartnerStatus, PartnerType, AuthType
from app.models.delivery import DeliveryStatus, DeliveryAttempt
from app.models.analytics import AnalyticsData, RevenueReport
from app.models.webhook import WebhookEndpoint, WebhookEvent
from app.models.workflow import WorkflowRule, WorkflowExecution


@pytest.mark.unit
class TestUserModel:
    """Test User model functionality."""
    
    def test_user_creation(self, db_session: Session):
        """Test basic user creation."""
        user = User(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            hashed_password="hashed_password",
            role=UserRole.VIEWER
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.full_name == "Test User"
        assert user.role == UserRole.VIEWER
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.timezone == "UTC"
        assert user.created_at is not None
        assert user.updated_at is not None
    
    def test_user_email_unique_constraint(self, db_session: Session):
        """Test that email must be unique."""
        user1 = User(email="test@example.com", hashed_password="hash1")
        user2 = User(email="test@example.com", hashed_password="hash2")
        
        db_session.add(user1)
        db_session.commit()
        
        db_session.add(user2)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_user_username_unique_constraint(self, db_session: Session):
        """Test that username must be unique."""
        user1 = User(email="test1@example.com", username="testuser", hashed_password="hash1")
        user2 = User(email="test2@example.com", username="testuser", hashed_password="hash2")
        
        db_session.add(user1)
        db_session.commit()
        
        db_session.add(user2)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_user_repr(self, db_session: Session):
        """Test user string representation."""
        user = User(
            email="test@example.com",
            role=UserRole.ADMIN,
            hashed_password="hash"
        )
        db_session.add(user)
        db_session.commit()
        
        expected = f"<User(id={user.id}, email='test@example.com', role='UserRole.ADMIN')>"
        assert repr(user) == expected
    
    def test_user_preferences_json_field(self, db_session: Session):
        """Test user preferences JSON field."""
        preferences = {"theme": "dark", "notifications": True}
        user = User(
            email="test@example.com",
            hashed_password="hash",
            preferences=preferences
        )
        db_session.add(user)
        db_session.commit()
        
        retrieved_user = db_session.query(User).filter_by(email="test@example.com").first()
        assert retrieved_user.preferences == preferences


@pytest.mark.unit
class TestAPIKeyModel:
    """Test APIKey model functionality."""
    
    def test_api_key_creation(self, db_session: Session):
        """Test basic API key creation."""
        user = User(email="test@example.com", hashed_password="hash")
        db_session.add(user)
        db_session.commit()
        
        api_key = APIKey(
            user_id=user.id,
            name="Test API Key",
            key_hash="hashed_key",
            prefix="sk_test",
            permissions=["read", "write"]
        )
        db_session.add(api_key)
        db_session.commit()
        
        assert api_key.id is not None
        assert api_key.user_id == user.id
        assert api_key.name == "Test API Key"
        assert api_key.key_hash == "hashed_key"
        assert api_key.prefix == "sk_test"
        assert api_key.permissions == ["read", "write"]
        assert api_key.is_active is True
        assert api_key.rate_limit_requests == 1000
        assert api_key.rate_limit_window == 3600
        assert api_key.usage_count == 0
    
    def test_api_key_user_relationship(self, db_session: Session):
        """Test API key to user relationship."""
        user = User(email="test@example.com", hashed_password="hash")
        api_key = APIKey(
            name="Test Key",
            key_hash="hash",
            prefix="sk_test"
        )
        user.api_keys.append(api_key)
        
        db_session.add(user)
        db_session.commit()
        
        assert len(user.api_keys) == 1
        assert user.api_keys[0].name == "Test Key"
        assert api_key.user == user
    
    def test_api_key_cascade_delete(self, db_session: Session):
        """Test that API keys are deleted when user is deleted."""
        user = User(email="test@example.com", hashed_password="hash")
        api_key = APIKey(
            name="Test Key",
            key_hash="hash",
            prefix="sk_test"
        )
        user.api_keys.append(api_key)
        
        db_session.add(user)
        db_session.commit()
        
        api_key_id = api_key.id
        db_session.delete(user)
        db_session.commit()
        
        # API key should be deleted due to cascade
        deleted_key = db_session.query(APIKey).filter_by(id=api_key_id).first()
        assert deleted_key is None


@pytest.mark.unit
class TestReleaseModel:
    """Test Release model functionality."""
    
    def test_release_creation(self, db_session: Session):
        """Test basic release creation."""
        release = Release(
            release_id="RL12345678",
            title="Test Album",
            artist="Test Artist",
            release_type=ReleaseType.ALBUM,
            status=ReleaseStatus.DRAFT
        )
        db_session.add(release)
        db_session.commit()
        
        assert release.id is not None
        assert release.release_id == "RL12345678"
        assert release.title == "Test Album"
        assert release.artist == "Test Artist"
        assert release.release_type == ReleaseType.ALBUM
        assert release.status == ReleaseStatus.DRAFT
        assert release.validation_status == "pending"
        assert release.created_at is not None
        assert release.updated_at is not None
    
    def test_release_id_unique_constraint(self, db_session: Session):
        """Test that release_id must be unique."""
        release1 = Release(
            release_id="RL12345678",
            title="Album 1",
            artist="Artist 1"
        )
        release2 = Release(
            release_id="RL12345678",
            title="Album 2",
            artist="Artist 2"
        )
        
        db_session.add(release1)
        db_session.commit()
        
        db_session.add(release2)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_release_repr(self, db_session: Session):
        """Test release string representation."""
        release = Release(
            release_id="RL12345678",
            title="Test Album",
            artist="Test Artist"
        )
        db_session.add(release)
        db_session.commit()
        
        expected = f"<Release(id={release.id}, title='Test Album', artist='Test Artist')>"
        assert repr(release) == expected
    
    def test_release_validation_errors_json_field(self, db_session: Session):
        """Test release validation_errors JSON field."""
        validation_errors = ["Missing UPC", "Invalid ISRC format"]
        release = Release(
            release_id="RL12345678",
            title="Test Album",
            artist="Test Artist",
            validation_errors=validation_errors
        )
        db_session.add(release)
        db_session.commit()
        
        retrieved_release = db_session.query(Release).filter_by(release_id="RL12345678").first()
        assert retrieved_release.validation_errors == validation_errors


@pytest.mark.unit
class TestTrackModel:
    """Test Track model functionality."""
    
    def test_track_creation(self, db_session: Session):
        """Test basic track creation."""
        release = Release(
            release_id="RL12345678",
            title="Test Album",
            artist="Test Artist"
        )
        db_session.add(release)
        db_session.commit()
        
        track = Track(
            release_id=release.id,
            title="Test Song",
            artist="Test Artist",
            track_number=1,
            duration_ms=180000,
            isrc="USRC17607839"
        )
        db_session.add(track)
        db_session.commit()
        
        assert track.id is not None
        assert track.release_id == release.id
        assert track.title == "Test Song"
        assert track.artist == "Test Artist"
        assert track.track_number == 1
        assert track.duration_ms == 180000
        assert track.isrc == "USRC17607839"
        assert track.explicit is False
        assert track.created_at is not None
        assert track.updated_at is not None
    
    def test_track_release_relationship(self, db_session: Session):
        """Test track to release relationship."""
        release = Release(
            release_id="RL12345678",
            title="Test Album",
            artist="Test Artist"
        )
        track = Track(
            title="Test Song",
            artist="Test Artist",
            track_number=1
        )
        release.tracks.append(track)
        
        db_session.add(release)
        db_session.commit()
        
        assert len(release.tracks) == 1
        assert release.tracks[0].title == "Test Song"
        assert track.release == release
    
    def test_track_isrc_unique_constraint(self, db_session: Session):
        """Test that ISRC must be unique."""
        release = Release(
            release_id="RL12345678",
            title="Test Album",
            artist="Test Artist"
        )
        db_session.add(release)
        db_session.commit()
        
        track1 = Track(
            release_id=release.id,
            title="Song 1",
            artist="Artist 1",
            track_number=1,
            isrc="USRC17607839"
        )
        track2 = Track(
            release_id=release.id,
            title="Song 2",
            artist="Artist 2",
            track_number=2,
            isrc="USRC17607839"
        )
        
        db_session.add(track1)
        db_session.commit()
        
        db_session.add(track2)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_track_cascade_delete(self, db_session: Session):
        """Test that tracks are deleted when release is deleted."""
        release = Release(
            release_id="RL12345678",
            title="Test Album",
            artist="Test Artist"
        )
        track = Track(
            title="Test Song",
            artist="Test Artist",
            track_number=1
        )
        release.tracks.append(track)
        
        db_session.add(release)
        db_session.commit()
        
        track_id = track.id
        db_session.delete(release)
        db_session.commit()
        
        # Track should be deleted due to cascade
        deleted_track = db_session.query(Track).filter_by(id=track_id).first()
        assert deleted_track is None
    
    def test_track_json_fields(self, db_session: Session):
        """Test track JSON fields for arrays."""
        release = Release(
            release_id="RL12345678",
            title="Test Album",
            artist="Test Artist"
        )
        db_session.add(release)
        db_session.commit()
        
        featured_artists = ["Artist 2", "Artist 3"]
        composers = ["Composer 1", "Composer 2"]
        publishers = ["Publisher 1"]
        
        track = Track(
            release_id=release.id,
            title="Test Song",
            artist="Test Artist",
            track_number=1,
            featured_artists=featured_artists,
            composers=composers,
            publishers=publishers
        )
        db_session.add(track)
        db_session.commit()
        
        retrieved_track = db_session.query(Track).filter_by(id=track.id).first()
        assert retrieved_track.featured_artists == featured_artists
        assert retrieved_track.composers == composers
        assert retrieved_track.publishers == publishers


@pytest.mark.unit
class TestReleaseAssetModel:
    """Test ReleaseAsset model functionality."""
    
    def test_release_asset_creation(self, db_session: Session):
        """Test basic release asset creation."""
        release = Release(
            release_id="RL12345678",
            title="Test Album",
            artist="Test Artist"
        )
        db_session.add(release)
        db_session.commit()
        
        asset = ReleaseAsset(
            release_id=release.id,
            asset_type=AssetType.ARTWORK,
            file_name="cover.jpg",
            file_url="https://example.com/cover.jpg",
            file_size=1024000,
            mime_type="image/jpeg",
            dimensions="1400x1400"
        )
        db_session.add(asset)
        db_session.commit()
        
        assert asset.id is not None
        assert asset.release_id == release.id
        assert asset.asset_type == AssetType.ARTWORK
        assert asset.file_name == "cover.jpg"
        assert asset.file_url == "https://example.com/cover.jpg"
        assert asset.file_size == 1024000
        assert asset.mime_type == "image/jpeg"
        assert asset.dimensions == "1400x1400"
        assert asset.created_at is not None
        assert asset.updated_at is not None
    
    def test_release_asset_relationship(self, db_session: Session):
        """Test release asset to release relationship."""
        release = Release(
            release_id="RL12345678",
            title="Test Album",
            artist="Test Artist"
        )
        asset = ReleaseAsset(
            asset_type=AssetType.ARTWORK,
            file_name="cover.jpg",
            file_url="https://example.com/cover.jpg"
        )
        release.assets.append(asset)
        
        db_session.add(release)
        db_session.commit()
        
        assert len(release.assets) == 1
        assert release.assets[0].file_name == "cover.jpg"
        assert asset.release == release
    
    def test_release_asset_cascade_delete(self, db_session: Session):
        """Test that assets are deleted when release is deleted."""
        release = Release(
            release_id="RL12345678",
            title="Test Album",
            artist="Test Artist"
        )
        asset = ReleaseAsset(
            asset_type=AssetType.ARTWORK,
            file_name="cover.jpg",
            file_url="https://example.com/cover.jpg"
        )
        release.assets.append(asset)
        
        db_session.add(release)
        db_session.commit()
        
        asset_id = asset.id
        db_session.delete(release)
        db_session.commit()
        
        # Asset should be deleted due to cascade
        deleted_asset = db_session.query(ReleaseAsset).filter_by(id=asset_id).first()
        assert deleted_asset is None


@pytest.mark.unit
class TestDeliveryPartnerModel:
    """Test DeliveryPartner model functionality."""
    
    def test_delivery_partner_creation(self, db_session: Session):
        """Test basic delivery partner creation."""
        partner = DeliveryPartner(
            partner_id="SPOTIFY001",
            name="Spotify",
            display_name="Spotify Music",
            partner_type=PartnerType.DSP,
            api_base_url="https://api.spotify.com",
            delivery_url="https://api.spotify.com/v1/delivery",
            auth_type=AuthType.OAUTH2,
            status=PartnerStatus.ACTIVE
        )
        db_session.add(partner)
        db_session.commit()
        
        assert partner.id is not None
        assert partner.partner_id == "SPOTIFY001"
        assert partner.name == "Spotify"
        assert partner.display_name == "Spotify Music"
        assert partner.partner_type == PartnerType.DSP
        assert partner.api_base_url == "https://api.spotify.com"
        assert partner.delivery_url == "https://api.spotify.com/v1/delivery"
        assert partner.auth_type == AuthType.OAUTH2
        assert partner.status == PartnerStatus.ACTIVE
        assert partner.priority == 0
        assert partner.auto_deliver is True
        assert partner.rate_limit_requests == 100
        assert partner.rate_limit_window == 3600
        assert partner.created_at is not None
        assert partner.updated_at is not None
    
    def test_delivery_partner_id_unique_constraint(self, db_session: Session):
        """Test that partner_id must be unique."""
        partner1 = DeliveryPartner(
            partner_id="SPOTIFY001",
            name="Spotify 1",
            api_base_url="https://api1.spotify.com",
            delivery_url="https://api1.spotify.com/delivery"
        )
        partner2 = DeliveryPartner(
            partner_id="SPOTIFY001",
            name="Spotify 2",
            api_base_url="https://api2.spotify.com",
            delivery_url="https://api2.spotify.com/delivery"
        )
        
        db_session.add(partner1)
        db_session.commit()
        
        db_session.add(partner2)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_delivery_partner_json_fields(self, db_session: Session):
        """Test delivery partner JSON fields."""
        supported_formats = ["mp3", "wav", "flac"]
        supported_territories = ["US", "CA", "GB"]
        
        partner = DeliveryPartner(
            partner_id="SPOTIFY001",
            name="Spotify",
            api_base_url="https://api.spotify.com",
            delivery_url="https://api.spotify.com/v1/delivery",
            supported_formats=supported_formats,
            supported_territories=supported_territories
        )
        db_session.add(partner)
        db_session.commit()
        
        retrieved_partner = db_session.query(DeliveryPartner).filter_by(partner_id="SPOTIFY001").first()
        assert retrieved_partner.supported_formats == supported_formats
        assert retrieved_partner.supported_territories == supported_territories


@pytest.mark.unit
class TestPartnerConfigModel:
    """Test PartnerConfig model functionality."""
    
    def test_partner_config_creation(self, db_session: Session):
        """Test basic partner config creation."""
        partner = DeliveryPartner(
            partner_id="SPOTIFY001",
            name="Spotify",
            api_base_url="https://api.spotify.com",
            delivery_url="https://api.spotify.com/v1/delivery"
        )
        db_session.add(partner)
        db_session.commit()
        
        config = PartnerConfig(
            partner_id=partner.id,
            config_key="api_key",
            config_value="encrypted_api_key_value",
            config_type="string",
            is_sensitive=True,
            is_required=True
        )
        db_session.add(config)
        db_session.commit()
        
        assert config.id is not None
        assert config.partner_id == partner.id
        assert config.config_key == "api_key"
        assert config.config_value == "encrypted_api_key_value"
        assert config.config_type == "string"
        assert config.is_sensitive is True
        assert config.is_required is True
        assert config.created_at is not None
        assert config.updated_at is not None
    
    def test_partner_config_relationship(self, db_session: Session):
        """Test partner config to partner relationship."""
        partner = DeliveryPartner(
            partner_id="SPOTIFY001",
            name="Spotify",
            api_base_url="https://api.spotify.com",
            delivery_url="https://api.spotify.com/v1/delivery"
        )
        config = PartnerConfig(
            config_key="api_key",
            config_value="encrypted_value"
        )
        partner.configs.append(config)
        
        db_session.add(partner)
        db_session.commit()
        
        assert len(partner.configs) == 1
        assert partner.configs[0].config_key == "api_key"
        assert config.partner == partner
    
    def test_partner_config_cascade_delete(self, db_session: Session):
        """Test that configs are deleted when partner is deleted."""
        partner = DeliveryPartner(
            partner_id="SPOTIFY001",
            name="Spotify",
            api_base_url="https://api.spotify.com",
            delivery_url="https://api.spotify.com/v1/delivery"
        )
        config = PartnerConfig(
            config_key="api_key",
            config_value="encrypted_value"
        )
        partner.configs.append(config)
        
        db_session.add(partner)
        db_session.commit()
        
        config_id = config.id
        db_session.delete(partner)
        db_session.commit()
        
        # Config should be deleted due to cascade
        deleted_config = db_session.query(PartnerConfig).filter_by(id=config_id).first()
        assert deleted_config is None


@pytest.mark.unit
class TestModelEnums:
    """Test model enum functionality."""
    
    def test_user_role_enum(self):
        """Test UserRole enum values."""
        assert UserRole.ADMIN.value == "admin"
        assert UserRole.MANAGER.value == "manager"
        assert UserRole.DEVELOPER.value == "developer"
        assert UserRole.VIEWER.value == "viewer"
    
    def test_release_status_enum(self):
        """Test ReleaseStatus enum values."""
        assert ReleaseStatus.DRAFT.value == "draft"
        assert ReleaseStatus.PROCESSING.value == "processing"
        assert ReleaseStatus.READY.value == "ready"
        assert ReleaseStatus.DELIVERED.value == "delivered"
        assert ReleaseStatus.LIVE.value == "live"
        assert ReleaseStatus.FAILED.value == "failed"
        assert ReleaseStatus.TAKEDOWN.value == "takedown"
    
    def test_release_type_enum(self):
        """Test ReleaseType enum values."""
        assert ReleaseType.SINGLE.value == "single"
        assert ReleaseType.ALBUM.value == "album"
        assert ReleaseType.EP.value == "ep"
        assert ReleaseType.COMPILATION.value == "compilation"
    
    def test_asset_type_enum(self):
        """Test AssetType enum values."""
        assert AssetType.ARTWORK.value == "artwork"
        assert AssetType.AUDIO.value == "audio"
        assert AssetType.VIDEO.value == "video"
        assert AssetType.DOCUMENT.value == "document"
    
    def test_partner_status_enum(self):
        """Test PartnerStatus enum values."""
        assert PartnerStatus.ACTIVE.value == "active"
        assert PartnerStatus.INACTIVE.value == "inactive"
        assert PartnerStatus.PENDING.value == "pending"
        assert PartnerStatus.SUSPENDED.value == "suspended"
    
    def test_partner_type_enum(self):
        """Test PartnerType enum values."""
        assert PartnerType.DSP.value == "dsp"
        assert PartnerType.AGGREGATOR.value == "aggregator"
        assert PartnerType.DISTRIBUTOR.value == "distributor"
        assert PartnerType.PLATFORM.value == "platform"
    
    def test_auth_type_enum(self):
        """Test AuthType enum values."""
        assert AuthType.API_KEY.value == "api_key"
        assert AuthType.OAUTH2.value == "oauth2"
        assert AuthType.BASIC_AUTH.value == "basic_auth"
        assert AuthType.BEARER_TOKEN.value == "bearer_token"
        assert AuthType.CUSTOM.value == "custom"


@pytest.mark.unit
class TestModelTimestamps:
    """Test model timestamp functionality."""
    
    def test_user_timestamps(self, db_session: Session):
        """Test user model timestamps."""
        user = User(email="test@example.com", hashed_password="hash")
        db_session.add(user)
        db_session.commit()
        
        # Check created_at and updated_at are set
        assert user.created_at is not None
        assert user.updated_at is not None
        assert user.created_at == user.updated_at
        
        # Update user and check updated_at changes
        original_updated_at = user.updated_at
        user.full_name = "Updated Name"
        db_session.commit()
        
        assert user.updated_at > original_updated_at
    
    def test_release_timestamps(self, db_session: Session):
        """Test release model timestamps."""
        release = Release(
            release_id="RL12345678",
            title="Test Album",
            artist="Test Artist"
        )
        db_session.add(release)
        db_session.commit()
        
        # Check created_at and updated_at are set
        assert release.created_at is not None
        assert release.updated_at is not None
        assert release.created_at == release.updated_at
        
        # Update release and check updated_at changes
        original_updated_at = release.updated_at
        release.title = "Updated Album"
        db_session.commit()
        
        assert release.updated_at > original_updated_at