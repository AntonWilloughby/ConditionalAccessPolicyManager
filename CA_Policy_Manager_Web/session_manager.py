#!/usr/bin/env python3
"""
Session Manager - Redis-backed session storage with in-memory fallback
Supports production scaling and development scenarios
"""

import os
import json
from typing import Optional, Dict, Any
from datetime import timedelta

class SessionManager:
    """
    Manages user sessions with Redis backend for production,
    fallback to in-memory for development.
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize session manager.
        
        Args:
            redis_url: Redis connection URL (uses env var if not provided)
        """
        self.redis_url = redis_url or os.environ.get('REDIS_URL')
        self.use_redis = self.redis_url is not None
        self.redis_client = None
        self.in_memory_sessions = {}
        self.session_ttl = 3600  # 1 hour default
        
        if self.use_redis:
            self._initialize_redis()
        else:
            print("ℹ️  Using in-memory session storage (development only)")
    
    def _initialize_redis(self):
        """Initialize Redis client"""
        try:
            import redis
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            self.redis_client.ping()
            print("✅ Connected to Redis for session management")
        except ImportError:
            print("⚠️  redis package not installed. Install with: pip install redis")
            self.use_redis = False
        except Exception as e:
            print(f"⚠️  Redis connection failed: {e}")
            print("   Falling back to in-memory session storage")
            self.use_redis = False
    
    def get_manager(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve manager data for session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Manager data or None if not found
        """
        try:
            if self.use_redis and self.redis_client:
                data = self.redis_client.get(f"manager:{session_id}")
                return json.loads(data) if data else None
            else:
                return self.in_memory_sessions.get(session_id)
        except Exception as e:
            print(f"❌ Error retrieving session {session_id}: {e}")
            return None
    
    def set_manager(self, session_id: str, manager_data: Dict[str, Any], 
                   ttl: Optional[int] = None):
        """
        Store manager data for session.
        
        Args:
            session_id: Session identifier
            manager_data: Data to store
            ttl: Time to live in seconds (uses default if not provided)
        """
        try:
            ttl = ttl or self.session_ttl
            
            if self.use_redis and self.redis_client:
                self.redis_client.setex(
                    f"manager:{session_id}",
                    ttl,
                    json.dumps(manager_data)
                )
            else:
                self.in_memory_sessions[session_id] = manager_data
        except Exception as e:
            print(f"❌ Error storing session {session_id}: {e}")
    
    def get_ai_stats(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get AI usage stats for session"""
        try:
            if self.use_redis and self.redis_client:
                data = self.redis_client.get(f"ai_stats:{session_id}")
                return json.loads(data) if data else None
            else:
                return self.in_memory_sessions.get(f"ai_stats:{session_id}")
        except Exception as e:
            print(f"❌ Error retrieving AI stats for {session_id}: {e}")
            return None
    
    def set_ai_stats(self, session_id: str, stats: Dict[str, Any], 
                    ttl: Optional[int] = None):
        """Set AI usage stats for session"""
        try:
            ttl = ttl or self.session_ttl
            
            if self.use_redis and self.redis_client:
                self.redis_client.setex(
                    f"ai_stats:{session_id}",
                    ttl,
                    json.dumps(stats)
                )
            else:
                self.in_memory_sessions[f"ai_stats:{session_id}"] = stats
        except Exception as e:
            print(f"❌ Error storing AI stats for {session_id}: {e}")
    
    def clear_session(self, session_id: str):
        """
        Clear all data for session.
        
        Args:
            session_id: Session identifier
        """
        try:
            if self.use_redis and self.redis_client:
                self.redis_client.delete(f"manager:{session_id}")
                self.redis_client.delete(f"ai_stats:{session_id}")
            else:
                self.in_memory_sessions.pop(session_id, None)
                self.in_memory_sessions.pop(f"ai_stats:{session_id}", None)
        except Exception as e:
            print(f"❌ Error clearing session {session_id}: {e}")
    
    def cleanup_expired(self):
        """Cleanup expired in-memory sessions (manual for non-Redis)"""
        if not self.use_redis:
            # In-memory sessions don't auto-expire
            # In production (Redis), expiration is automatic
            pass
