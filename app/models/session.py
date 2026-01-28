"""Session data models."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import secrets


@dataclass
class SessionData:
    """Data stored in a user session."""
    # API Keys (stored encrypted in production)
    openai_api_key: Optional[str] = None
    wordpress_credentials: Optional[Dict[str, str]] = None

    # User preferences
    preferred_categories: List[str] = field(default_factory=list)
    default_ranking_weights: Optional[Dict[str, float]] = None

    # State
    selected_articles: List[str] = field(default_factory=list)
    last_scrape_time: Optional[datetime] = None
    last_publish_time: Optional[datetime] = None

    # Cost tracking
    session_cost: float = 0.0
    articles_published: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'has_openai_key': bool(self.openai_api_key),
            'has_wordpress': bool(self.wordpress_credentials),
            'preferred_categories': self.preferred_categories,
            'default_ranking_weights': self.default_ranking_weights,
            'selected_articles': self.selected_articles,
            'last_scrape_time': self.last_scrape_time.isoformat() if self.last_scrape_time else None,
            'last_publish_time': self.last_publish_time.isoformat() if self.last_publish_time else None,
            'session_cost': self.session_cost,
            'articles_published': self.articles_published,
        }

    def add_cost(self, cost: float) -> None:
        """Add to session cost."""
        self.session_cost += cost

    def add_published(self) -> None:
        """Increment published count."""
        self.articles_published += 1
        self.last_publish_time = datetime.now()

    def select_article(self, article_id: str) -> None:
        """Add article to selection."""
        if article_id not in self.selected_articles:
            self.selected_articles.append(article_id)

    def deselect_article(self, article_id: str) -> None:
        """Remove article from selection."""
        if article_id in self.selected_articles:
            self.selected_articles.remove(article_id)

    def clear_selection(self) -> None:
        """Clear all selected articles."""
        self.selected_articles.clear()


@dataclass
class UserSession:
    """User session container."""
    id: str = field(default_factory=lambda: secrets.token_urlsafe(32))
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    data: SessionData = field(default_factory=SessionData)

    # Session settings
    timeout_minutes: int = 60

    def __post_init__(self):
        if not self.expires_at:
            self.expires_at = self.created_at + timedelta(minutes=self.timeout_minutes)

    @property
    def is_expired(self) -> bool:
        """Check if session has expired."""
        return datetime.now() > self.expires_at

    @property
    def is_authenticated(self) -> bool:
        """Check if session has necessary credentials."""
        return bool(self.data.openai_api_key)

    def touch(self) -> None:
        """Update last activity and extend expiration."""
        self.last_activity = datetime.now()
        self.expires_at = datetime.now() + timedelta(minutes=self.timeout_minutes)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_expired': self.is_expired,
            'is_authenticated': self.is_authenticated,
            'data': self.data.to_dict(),
        }


@dataclass
class SessionStore:
    """In-memory session store."""
    sessions: Dict[str, UserSession] = field(default_factory=dict)
    max_sessions: int = 1000

    def create(self, timeout_minutes: int = 60) -> UserSession:
        """Create a new session."""
        self._cleanup_expired()

        if len(self.sessions) >= self.max_sessions:
            # Remove oldest session
            oldest = min(self.sessions.values(), key=lambda s: s.last_activity)
            del self.sessions[oldest.id]

        session = UserSession(timeout_minutes=timeout_minutes)
        self.sessions[session.id] = session
        return session

    def get(self, session_id: str) -> Optional[UserSession]:
        """Get session by ID."""
        session = self.sessions.get(session_id)
        if session and not session.is_expired:
            session.touch()
            return session
        elif session:
            # Remove expired session
            del self.sessions[session_id]
        return None

    def delete(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

    def _cleanup_expired(self) -> int:
        """Remove expired sessions."""
        expired = [sid for sid, s in self.sessions.items() if s.is_expired]
        for sid in expired:
            del self.sessions[sid]
        return len(expired)

    def active_count(self) -> int:
        """Get count of active sessions."""
        self._cleanup_expired()
        return len(self.sessions)
