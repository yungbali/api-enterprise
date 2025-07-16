"""
Release factory for generating test release data.
"""
import factory
from faker import Faker
from datetime import datetime, timedelta
import random
import uuid

from app.models.release import Release, ReleaseStatus, ReleaseType, Track, ReleaseAsset, AssetType

fake = Faker()


class ReleaseFactoryBase(factory.Factory):
    """Factory for creating test Release instances."""
    
    class Meta:
        model = Release
    
    # Basic release info
    release_id = factory.LazyAttribute(lambda obj: f"REL-{uuid.uuid4().hex[:8].upper()}")
    title = factory.LazyAttribute(lambda obj: fake.catch_phrase())
    artist = factory.LazyAttribute(lambda obj: fake.name())
    label = factory.LazyAttribute(lambda obj: f"{fake.word().title()} Records")
    release_type = factory.LazyAttribute(lambda obj: random.choice(list(ReleaseType)))
    release_date = factory.LazyAttribute(lambda obj: fake.date_between(start_date="-2y", end_date="+6m"))
    original_release_date = factory.LazyAttribute(lambda obj: fake.date_between(start_date="-5y", end_date=obj.release_date))
    
    # DDEX Fields
    grid = factory.LazyAttribute(lambda obj: f"A1-{fake.random_number(digits=10)}")
    upc = factory.LazyAttribute(lambda obj: fake.ean13())
    catalog_number = factory.LazyAttribute(lambda obj: f"{fake.lexify(text='???').upper()}{fake.random_number(digits=3)}")
    genre = factory.LazyAttribute(lambda obj: random.choice([
        "Electronic", "Rock", "Pop", "Hip-Hop", "Jazz", "Classical", 
        "Country", "R&B", "Reggae", "Folk", "Blues", "Punk"
    ]))
    subgenre = factory.LazyAttribute(lambda obj: random.choice([
        "House", "Techno", "Ambient", "Indie Rock", "Alternative", 
        "Trap", "Lo-Fi", "Experimental", "Acoustic", "Synthwave"
    ]))
    
    # Metadata
    description = factory.LazyAttribute(lambda obj: fake.text(max_nb_chars=500))
    copyright_text = factory.LazyAttribute(lambda obj: f"℗ {fake.year()} {obj.label}")
    producer_copyright_text = factory.LazyAttribute(lambda obj: f"© {fake.year()} {obj.label}")
    language = factory.LazyAttribute(lambda obj: random.choice(["en", "es", "fr", "de", "it", "pt"]))
    territory = factory.LazyAttribute(lambda obj: random.choice(["US", "GB", "DE", "FR", "CA", "AU", "WW"]))
    
    # Status and tracking
    status = ReleaseStatus.DRAFT
    validation_status = "pending"
    validation_errors = None
    
    # Timestamps
    created_at = factory.LazyAttribute(lambda obj: fake.date_time_between(start_date="-1y", end_date="now"))
    updated_at = factory.LazyAttribute(lambda obj: fake.date_time_between(start_date=obj.created_at, end_date="now"))


class ProcessingReleaseFactory(ReleaseFactoryBase):
    """Factory for releases in processing status."""
    
    status = ReleaseStatus.PROCESSING
    validation_status = "in_progress"


class ReadyReleaseFactory(ReleaseFactoryBase):
    """Factory for releases ready for delivery."""
    
    status = ReleaseStatus.READY
    validation_status = "passed"


class DeliveredReleaseFactory(ReleaseFactoryBase):
    """Factory for delivered releases."""
    
    status = ReleaseStatus.DELIVERED
    validation_status = "passed"


class LiveReleaseFactory(ReleaseFactoryBase):
    """Factory for live releases."""
    
    status = ReleaseStatus.LIVE
    validation_status = "passed"
    release_date = factory.LazyAttribute(lambda obj: fake.date_between(start_date="-1y", end_date="now"))


class FailedReleaseFactory(ReleaseFactoryBase):
    """Factory for failed releases."""
    
    status = ReleaseStatus.FAILED
    validation_status = "failed"
    validation_errors = factory.LazyAttribute(lambda obj: [
        "Missing required metadata",
        "Invalid audio format",
        "Artwork resolution too low"
    ])


class SingleReleaseFactory(ReleaseFactoryBase):
    """Factory for single releases."""
    
    release_type = ReleaseType.SINGLE


class AlbumReleaseFactory(ReleaseFactoryBase):
    """Factory for album releases."""
    
    release_type = ReleaseType.ALBUM


class EPReleaseFactory(ReleaseFactoryBase):
    """Factory for EP releases."""
    
    release_type = ReleaseType.EP


class TrackFactory(factory.Factory):
    """Factory for creating test Track instances."""
    
    class Meta:
        model = Track
    
    # Track info
    title = factory.LazyAttribute(lambda obj: fake.catch_phrase())
    artist = factory.LazyAttribute(lambda obj: fake.name())
    featured_artists = factory.LazyAttribute(lambda obj: [fake.name()] if random.choice([True, False]) else [])
    track_number = factory.LazyAttribute(lambda obj: random.randint(1, 20))
    duration_ms = factory.LazyAttribute(lambda obj: random.randint(120000, 480000))  # 2-8 minutes
    
    # Identifiers
    isrc = factory.LazyAttribute(lambda obj: f"US{fake.lexify(text='???').upper()}{fake.random_number(digits=8)}")
    
    # Metadata
    composers = factory.LazyAttribute(lambda obj: [fake.name() for _ in range(random.randint(1, 3))])
    publishers = factory.LazyAttribute(lambda obj: [f"{fake.word().title()} Publishing" for _ in range(random.randint(1, 2))])
    explicit = factory.LazyAttribute(lambda obj: random.choice([True, False]))
    genre = factory.LazyAttribute(lambda obj: random.choice([
        "Electronic", "Rock", "Pop", "Hip-Hop", "Jazz", "Classical"
    ]))
    language = factory.LazyAttribute(lambda obj: random.choice(["en", "es", "fr", "de"]))
    
    # Audio file info
    audio_file_url = factory.LazyAttribute(lambda obj: f"https://storage.example.com/audio/{uuid.uuid4()}.mp3")
    audio_file_format = factory.LazyAttribute(lambda obj: random.choice(["mp3", "wav", "flac"]))
    audio_file_size = factory.LazyAttribute(lambda obj: random.randint(5000000, 50000000))  # 5-50MB
    audio_bitrate = factory.LazyAttribute(lambda obj: random.choice([128, 192, 256, 320]))
    audio_sample_rate = factory.LazyAttribute(lambda obj: random.choice([44100, 48000, 96000]))
    
    # Timestamps
    created_at = factory.LazyAttribute(lambda obj: fake.date_time_between(start_date="-1y", end_date="now"))
    updated_at = factory.LazyAttribute(lambda obj: fake.date_time_between(start_date=obj.created_at, end_date="now"))


class HighQualityTrackFactory(TrackFactory):
    """Factory for high-quality audio tracks."""
    
    audio_file_format = "flac"
    audio_bitrate = 1411  # CD quality
    audio_sample_rate = 44100
    audio_file_size = factory.LazyAttribute(lambda obj: random.randint(30000000, 80000000))  # 30-80MB


class ExplicitTrackFactory(TrackFactory):
    """Factory for explicit content tracks."""
    
    explicit = True


class ReleaseAssetFactory(factory.Factory):
    """Factory for creating test ReleaseAsset instances."""
    
    class Meta:
        model = ReleaseAsset
    
    # Asset info
    asset_type = factory.LazyAttribute(lambda obj: random.choice(list(AssetType)))
    file_name = factory.LazyAttribute(lambda obj: f"{fake.word()}_{uuid.uuid4().hex[:8]}.{_get_file_extension(obj.asset_type)}")
    file_url = factory.LazyAttribute(lambda obj: f"https://storage.example.com/assets/{obj.file_name}")
    file_size = factory.LazyAttribute(lambda obj: _get_file_size_by_type(obj.asset_type))
    mime_type = factory.LazyAttribute(lambda obj: _get_mime_type_by_type(obj.asset_type))
    
    # Metadata
    title = factory.LazyAttribute(lambda obj: fake.sentence(nb_words=3))
    description = factory.LazyAttribute(lambda obj: fake.text(max_nb_chars=200))
    dimensions = factory.LazyAttribute(lambda obj: _get_dimensions_by_type(obj.asset_type))
    
    # Timestamps
    created_at = factory.LazyAttribute(lambda obj: fake.date_time_between(start_date="-1y", end_date="now"))
    updated_at = factory.LazyAttribute(lambda obj: fake.date_time_between(start_date=obj.created_at, end_date="now"))


class ArtworkAssetFactory(ReleaseAssetFactory):
    """Factory for artwork assets."""
    
    asset_type = AssetType.ARTWORK
    file_name = factory.LazyAttribute(lambda obj: f"artwork_{uuid.uuid4().hex[:8]}.jpg")
    mime_type = "image/jpeg"
    dimensions = "3000x3000"
    file_size = factory.LazyAttribute(lambda obj: random.randint(2000000, 10000000))  # 2-10MB


class AudioAssetFactory(ReleaseAssetFactory):
    """Factory for audio assets."""
    
    asset_type = AssetType.AUDIO
    file_name = factory.LazyAttribute(lambda obj: f"audio_{uuid.uuid4().hex[:8]}.wav")
    mime_type = "audio/wav"
    file_size = factory.LazyAttribute(lambda obj: random.randint(20000000, 100000000))  # 20-100MB


class VideoAssetFactory(ReleaseAssetFactory):
    """Factory for video assets."""
    
    asset_type = AssetType.VIDEO
    file_name = factory.LazyAttribute(lambda obj: f"video_{uuid.uuid4().hex[:8]}.mp4")
    mime_type = "video/mp4"
    dimensions = "1920x1080"
    file_size = factory.LazyAttribute(lambda obj: random.randint(50000000, 500000000))  # 50-500MB


class DocumentAssetFactory(ReleaseAssetFactory):
    """Factory for document assets."""
    
    asset_type = AssetType.DOCUMENT
    file_name = factory.LazyAttribute(lambda obj: f"document_{uuid.uuid4().hex[:8]}.pdf")
    mime_type = "application/pdf"
    file_size = factory.LazyAttribute(lambda obj: random.randint(100000, 5000000))  # 100KB-5MB


# Helper functions
def _get_file_extension(asset_type):
    """Get appropriate file extension for asset type."""
    extensions = {
        AssetType.ARTWORK: random.choice(["jpg", "png", "tiff"]),
        AssetType.AUDIO: random.choice(["mp3", "wav", "flac"]),
        AssetType.VIDEO: random.choice(["mp4", "mov", "avi"]),
        AssetType.DOCUMENT: random.choice(["pdf", "doc", "txt"])
    }
    return extensions.get(asset_type, "bin")


def _get_file_size_by_type(asset_type):
    """Get realistic file size based on asset type."""
    sizes = {
        AssetType.ARTWORK: random.randint(1000000, 15000000),  # 1-15MB
        AssetType.AUDIO: random.randint(5000000, 100000000),   # 5-100MB
        AssetType.VIDEO: random.randint(50000000, 1000000000), # 50MB-1GB
        AssetType.DOCUMENT: random.randint(100000, 10000000)   # 100KB-10MB
    }
    return sizes.get(asset_type, 1000000)


def _get_mime_type_by_type(asset_type):
    """Get appropriate MIME type for asset type."""
    mime_types = {
        AssetType.ARTWORK: random.choice(["image/jpeg", "image/png", "image/tiff"]),
        AssetType.AUDIO: random.choice(["audio/mpeg", "audio/wav", "audio/flac"]),
        AssetType.VIDEO: random.choice(["video/mp4", "video/quicktime", "video/avi"]),
        AssetType.DOCUMENT: random.choice(["application/pdf", "application/msword", "text/plain"])
    }
    return mime_types.get(asset_type, "application/octet-stream")


def _get_dimensions_by_type(asset_type):
    """Get appropriate dimensions for asset type."""
    if asset_type == AssetType.ARTWORK:
        return random.choice(["3000x3000", "1400x1400", "600x600", "300x300"])
    elif asset_type == AssetType.VIDEO:
        return random.choice(["1920x1080", "1280x720", "3840x2160", "1440x1080"])
    return None


# Utility functions for creating releases with relationships
def create_single_release_with_track(session, release_factory=SingleReleaseFactory, track_factory=TrackFactory):
    """Create a single release with one track."""
    release = release_factory()
    session.add(release)
    session.flush()  # Get the release ID
    
    track = track_factory(
        release_id=release.id,
        track_number=1,
        artist=release.artist  # Match the release artist
    )
    session.add(track)
    session.commit()
    
    return release, track


def create_album_with_tracks(session, num_tracks=10, release_factory=AlbumReleaseFactory, track_factory=TrackFactory):
    """Create an album release with multiple tracks."""
    release = release_factory()
    session.add(release)
    session.flush()
    
    tracks = []
    for i in range(1, num_tracks + 1):
        track = track_factory(
            release_id=release.id,
            track_number=i,
            artist=release.artist
        )
        session.add(track)
        tracks.append(track)
    
    session.commit()
    return release, tracks


def create_release_with_assets(session, release_factory=ReleaseFactoryBase, num_assets=3):
    """Create a release with various assets."""
    release = release_factory()
    session.add(release)
    session.flush()
    
    assets = []
    
    # Always include artwork
    artwork = ArtworkAssetFactory(release_id=release.id)
    session.add(artwork)
    assets.append(artwork)
    
    # Add additional random assets
    asset_factories = [AudioAssetFactory, VideoAssetFactory, DocumentAssetFactory]
    for _ in range(num_assets - 1):
        factory_class = random.choice(asset_factories)
        asset = factory_class(release_id=release.id)
        session.add(asset)
        assets.append(asset)
    
    session.commit()
    return release, assets


def create_complete_release(session, num_tracks=5, num_assets=4):
    """Create a complete release with tracks and assets."""
    release = AlbumReleaseFactory()
    session.add(release)
    session.flush()
    
    # Create tracks
    tracks = []
    for i in range(1, num_tracks + 1):
        track = TrackFactory(
            release_id=release.id,
            track_number=i,
            artist=release.artist
        )
        session.add(track)
        tracks.append(track)
    
    # Create assets
    assets = []
    
    # Artwork (required)
    artwork = ArtworkAssetFactory(release_id=release.id)
    session.add(artwork)
    assets.append(artwork)
    
    # Additional assets
    for _ in range(num_assets - 1):
        asset_type = random.choice([AudioAssetFactory, VideoAssetFactory, DocumentAssetFactory])
        asset = asset_type(release_id=release.id)
        session.add(asset)
        assets.append(asset)
    
    session.commit()
    return release, tracks, assets


def create_release_test_set(session):
    """Create a comprehensive set of releases for testing."""
    releases = {}
    
    # Different status releases
    releases['draft'] = ReleaseFactory()
    releases['processing'] = ProcessingReleaseFactory()
    releases['ready'] = ReadyReleaseFactory()
    releases['delivered'] = DeliveredReleaseFactory()
    releases['live'] = LiveReleaseFactory()
    releases['failed'] = FailedReleaseFactory()
    
    # Different type releases
    releases['single'] = SingleReleaseFactory()
    releases['album'] = AlbumReleaseFactory()
    releases['ep'] = EPReleaseFactory()
    
    # Add all releases to session
    for release in releases.values():
        session.add(release)
    
    session.commit()
    return releases


class ReleaseFactory:
    """Factory class for creating test releases."""
    
    @staticmethod
    def create_release(session, title=None, artist=None, **kwargs):
        """Create a release with specified parameters."""
        import uuid
        
        if title is None:
            title = fake.catch_phrase()
        if artist is None:
            artist = fake.name()
        
        release_data = {
            "release_id": f"REL-{uuid.uuid4().hex[:8].upper()}",
            "title": title,
            "artist": artist,
            "label": kwargs.get("label", f"{fake.word().title()} Records"),
            "release_type": kwargs.get("release_type", ReleaseType.SINGLE),
            "release_date": kwargs.get("release_date", fake.date_between(start_date="-2y", end_date="+6m")),
            "original_release_date": kwargs.get("original_release_date"),
            "grid": kwargs.get("grid", f"A1-{fake.random_number(digits=10)}"),
            "upc": kwargs.get("upc", fake.ean13()),
            "catalog_number": kwargs.get("catalog_number", f"{fake.lexify(text='???').upper()}{fake.random_number(digits=3)}"),
            "genre": kwargs.get("genre", random.choice(["Electronic", "Rock", "Pop", "Hip-Hop", "Jazz"])),
            "subgenre": kwargs.get("subgenre"),
            "description": kwargs.get("description"),
            "copyright_text": kwargs.get("copyright_text"),
            "producer_copyright_text": kwargs.get("producer_copyright_text"),
            "language": kwargs.get("language", "en"),
            "territory": kwargs.get("territory", "US"),
            "status": kwargs.get("status", ReleaseStatus.DRAFT),
            "validation_status": kwargs.get("validation_status", "pending"),
            "validation_errors": kwargs.get("validation_errors"),
            "created_at": fake.date_time_between(start_date="-1y", end_date="now"),
            "updated_at": fake.date_time_between(start_date="-1y", end_date="now")
        }
        
        release = Release(**release_data)
        session.add(release)
        session.commit()
        session.refresh(release)
        return release