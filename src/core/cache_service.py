"""
High-performance caching service for farming advisory API
Implements weather (6-12h), soil (permanent), and NDVI (weekly) caching
"""
import json
import hashlib
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, Union
import threading
from dataclasses import dataclass, asdict
from enum import Enum


class CacheType(Enum):
    """Cache types with different TTL policies"""
    WEATHER = "weather"
    SOIL = "soil" 
    NDVI = "ndvi"
    ML_PREDICTION = "ml_prediction"
    LOCATION = "location"


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    data: Dict[str, Any]
    created_at: float
    expires_at: float
    cache_type: str
    location_key: str
    access_count: int = 0
    last_accessed: float = 0.0


class HighPerformanceCache:
    """
    High-performance caching system optimized for farming advisory API
    Target: <2s response times
    """
    
    def __init__(self, cache_dir: str = "data/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory cache for hot data
        self._memory_cache: Dict[str, CacheEntry] = {}
        self._cache_lock = threading.RLock()
        
        # Cache TTL policies (in seconds)
        self.cache_policies = {
            CacheType.WEATHER: {
                'ttl': 6 * 3600,  # 6 hours
                'max_entries': 1000,
                'disk_persist': True
            },
            CacheType.SOIL: {
                'ttl': 365 * 24 * 3600,  # 1 year (permanent)
                'max_entries': 10000,
                'disk_persist': True
            },
            CacheType.NDVI: {
                'ttl': 7 * 24 * 3600,  # 7 days (weekly)
                'max_entries': 5000,
                'disk_persist': True
            },
            CacheType.ML_PREDICTION: {
                'ttl': 1 * 3600,  # 1 hour
                'max_entries': 2000,
                'disk_persist': False
            },
            CacheType.LOCATION: {
                'ttl': 365 * 24 * 3600,  # 1 year (permanent)
                'max_entries': 50000,
                'disk_persist': True
            }
        }
        
        # Performance metrics
        self.metrics = {
            'hits': 0,
            'misses': 0,
            'total_requests': 0,
            'avg_response_time': 0.0,
            'cache_size': 0
        }
        
        # Load existing cache from disk
        self._load_disk_cache()
    
    def get(self, cache_type: CacheType, location_key: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Get cached data with high performance
        
        Args:
            cache_type: Type of cache (weather, soil, ndvi, ml_prediction)
            location_key: Location identifier (lat_lon or custom key)
            **kwargs: Additional parameters for cache key generation
            
        Returns:
            Cached data if valid, None if not found or expired
        """
        start_time = time.time()
        
        try:
            # Generate cache key
            cache_key = self._generate_cache_key(cache_type, location_key, **kwargs)
            
            with self._cache_lock:
                self.metrics['total_requests'] += 1
                
                # Check memory cache first
                if cache_key in self._memory_cache:
                    entry = self._memory_cache[cache_key]
                    
                    # Check if expired
                    if time.time() > entry.expires_at:
                        del self._memory_cache[cache_key]
                        self._update_metrics('miss', start_time)
                        return None
                    
                    # Update access statistics
                    entry.access_count += 1
                    entry.last_accessed = time.time()
                    
                    self._update_metrics('hit', start_time)
                    return entry.data
                
                # Check disk cache for persistent types
                policy = self.cache_policies[cache_type]
                if policy['disk_persist']:
                    disk_data = self._load_from_disk(cache_key)
                    if disk_data:
                        # Add to memory cache
                        self._memory_cache[cache_key] = disk_data
                        self._update_metrics('hit', start_time)
                        return disk_data.data
                
                self._update_metrics('miss', start_time)
                return None
                
        except Exception as e:
            print(f"Cache get error: {e}")
            self._update_metrics('miss', start_time)
            return None
    
    def set(self, cache_type: CacheType, location_key: str, data: Dict[str, Any], **kwargs) -> bool:
        """
        Set cached data with automatic expiration and persistence
        
        Args:
            cache_type: Type of cache
            location_key: Location identifier
            data: Data to cache
            **kwargs: Additional parameters for cache key generation
            
        Returns:
            True if successfully cached
        """
        try:
            cache_key = self._generate_cache_key(cache_type, location_key, **kwargs)
            policy = self.cache_policies[cache_type]
            
            # Create cache entry
            current_time = time.time()
            entry = CacheEntry(
                data=data,
                created_at=current_time,
                expires_at=current_time + policy['ttl'],
                cache_type=cache_type.value,
                location_key=location_key,
                last_accessed=current_time
            )
            
            with self._cache_lock:
                # Add to memory cache
                self._memory_cache[cache_key] = entry
                
                # Enforce memory cache size limits
                self._enforce_cache_limits(cache_type)
                
                # Persist to disk if required
                if policy['disk_persist']:
                    self._save_to_disk(cache_key, entry)
                
                self.metrics['cache_size'] = len(self._memory_cache)
                return True
                
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def invalidate(self, cache_type: CacheType, location_key: str = None, **kwargs) -> int:
        """
        Invalidate cache entries
        
        Args:
            cache_type: Type of cache to invalidate
            location_key: Specific location (None for all)
            **kwargs: Additional parameters
            
        Returns:
            Number of entries invalidated
        """
        invalidated = 0
        
        try:
            with self._cache_lock:
                keys_to_remove = []
                
                for key, entry in self._memory_cache.items():
                    if entry.cache_type == cache_type.value:
                        if location_key is None or entry.location_key == location_key:
                            keys_to_remove.append(key)
                
                # Remove from memory
                for key in keys_to_remove:
                    del self._memory_cache[key]
                    invalidated += 1
                    
                    # Remove from disk
                    self._remove_from_disk(key)
                
                self.metrics['cache_size'] = len(self._memory_cache)
                
        except Exception as e:
            print(f"Cache invalidation error: {e}")
        
        return invalidated
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        with self._cache_lock:
            hit_rate = 0.0
            if self.metrics['total_requests'] > 0:
                hit_rate = self.metrics['hits'] / self.metrics['total_requests']
            
            return {
                'hit_rate': hit_rate,
                'total_requests': self.metrics['total_requests'],
                'cache_hits': self.metrics['hits'],
                'cache_misses': self.metrics['misses'],
                'cache_size': self.metrics['cache_size'],
                'avg_response_time_ms': self.metrics['avg_response_time'] * 1000,
                'memory_entries': len(self._memory_cache),
                'cache_types': {
                    cache_type.value: sum(1 for entry in self._memory_cache.values() 
                                        if entry.cache_type == cache_type.value)
                    for cache_type in CacheType
                }
            }
    
    def cleanup_expired(self) -> int:
        """Remove expired entries from cache"""
        removed = 0
        current_time = time.time()
        
        try:
            with self._cache_lock:
                keys_to_remove = []
                
                for key, entry in self._memory_cache.items():
                    if current_time > entry.expires_at:
                        keys_to_remove.append(key)
                
                for key in keys_to_remove:
                    del self._memory_cache[key]
                    self._remove_from_disk(key)
                    removed += 1
                
                self.metrics['cache_size'] = len(self._memory_cache)
                
        except Exception as e:
            print(f"Cache cleanup error: {e}")
        
        return removed
    
    def _generate_cache_key(self, cache_type: CacheType, location_key: str, **kwargs) -> str:
        """Generate unique cache key"""
        # Create deterministic key from parameters
        key_parts = [cache_type.value, location_key]
        
        # Add sorted kwargs for consistency
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}:{v}")
        
        key_string = "|".join(key_parts)
        
        # Hash for consistent length and avoid filesystem issues
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _update_metrics(self, result: str, start_time: float):
        """Update performance metrics"""
        response_time = time.time() - start_time
        
        if result == 'hit':
            self.metrics['hits'] += 1
        else:
            self.metrics['misses'] += 1
        
        # Update rolling average response time
        total = self.metrics['hits'] + self.metrics['misses']
        if total > 1:
            self.metrics['avg_response_time'] = (
                (self.metrics['avg_response_time'] * (total - 1) + response_time) / total
            )
        else:
            self.metrics['avg_response_time'] = response_time
    
    def _enforce_cache_limits(self, cache_type: CacheType):
        """Enforce cache size limits using LRU eviction"""
        policy = self.cache_policies[cache_type]
        max_entries = policy['max_entries']
        
        # Count entries of this type
        type_entries = [(k, v) for k, v in self._memory_cache.items() 
                       if v.cache_type == cache_type.value]
        
        if len(type_entries) > max_entries:
            # Sort by last accessed time (LRU)
            type_entries.sort(key=lambda x: x[1].last_accessed)
            
            # Remove oldest entries
            to_remove = len(type_entries) - max_entries
            for i in range(to_remove):
                key = type_entries[i][0]
                del self._memory_cache[key]
                self._remove_from_disk(key)
    
    def _save_to_disk(self, cache_key: str, entry: CacheEntry):
        """Save cache entry to disk"""
        try:
            cache_file = self.cache_dir / f"{cache_key}.json"
            with open(cache_file, 'w') as f:
                json.dump(asdict(entry), f, default=str)
        except Exception as e:
            print(f"Disk save error: {e}")
    
    def _load_from_disk(self, cache_key: str) -> Optional[CacheEntry]:
        """Load cache entry from disk"""
        try:
            cache_file = self.cache_dir / f"{cache_key}.json"
            if cache_file.exists():
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                
                entry = CacheEntry(**data)
                
                # Check if expired
                if time.time() > entry.expires_at:
                    cache_file.unlink()  # Remove expired file
                    return None
                
                return entry
        except Exception as e:
            print(f"Disk load error: {e}")
        
        return None
    
    def _remove_from_disk(self, cache_key: str):
        """Remove cache entry from disk"""
        try:
            cache_file = self.cache_dir / f"{cache_key}.json"
            if cache_file.exists():
                cache_file.unlink()
        except Exception as e:
            print(f"Disk remove error: {e}")
    
    def _load_disk_cache(self):
        """Load existing cache from disk on startup"""
        try:
            cache_files = list(self.cache_dir.glob("*.json"))
            loaded = 0
            
            for cache_file in cache_files:
                try:
                    with open(cache_file, 'r') as f:
                        data = json.load(f)
                    
                    entry = CacheEntry(**data)
                    
                    # Check if expired
                    if time.time() <= entry.expires_at:
                        cache_key = cache_file.stem
                        self._memory_cache[cache_key] = entry
                        loaded += 1
                    else:
                        cache_file.unlink()  # Remove expired
                        
                except Exception:
                    cache_file.unlink()  # Remove corrupted files
            
            self.metrics['cache_size'] = len(self._memory_cache)
            print(f"✅ Loaded {loaded} cache entries from disk")
            
        except Exception as e:
            print(f"Cache initialization error: {e}")


# Global cache instance
_cache_instance = None
_cache_lock = threading.Lock()


def get_cache() -> HighPerformanceCache:
    """Get global cache instance (singleton)"""
    global _cache_instance
    
    if _cache_instance is None:
        with _cache_lock:
            if _cache_instance is None:
                _cache_instance = HighPerformanceCache()
    
    return _cache_instance


def cache_weather(lat: float, lon: float, data: Dict[str, Any]) -> bool:
    """Cache weather data (6-12 hour TTL)"""
    cache = get_cache()
    location_key = f"{lat:.4f}_{lon:.4f}"
    return cache.set(CacheType.WEATHER, location_key, data)


def get_cached_weather(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """Get cached weather data"""
    cache = get_cache()
    location_key = f"{lat:.4f}_{lon:.4f}"
    return cache.get(CacheType.WEATHER, location_key)


def cache_soil(lat: float, lon: float, data: Dict[str, Any]) -> bool:
    """Cache soil data (permanent)"""
    cache = get_cache()
    location_key = f"{lat:.4f}_{lon:.4f}"
    return cache.set(CacheType.SOIL, location_key, data)


def get_cached_soil(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """Get cached soil data"""
    cache = get_cache()
    location_key = f"{lat:.4f}_{lon:.4f}"
    return cache.get(CacheType.SOIL, location_key)


def cache_ndvi(lat: float, lon: float, data: Dict[str, Any]) -> bool:
    """Cache NDVI data (weekly TTL)"""
    cache = get_cache()
    location_key = f"{lat:.4f}_{lon:.4f}"
    return cache.set(CacheType.NDVI, location_key, data)


def get_cached_ndvi(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """Get cached NDVI data"""
    cache = get_cache()
    location_key = f"{lat:.4f}_{lon:.4f}"
    return cache.get(CacheType.NDVI, location_key)


def cache_ml_prediction(crop: str, lat: float, lon: float, data: Dict[str, Any]) -> bool:
    """Cache ML prediction (1 hour TTL)"""
    cache = get_cache()
    location_key = f"{crop}_{lat:.4f}_{lon:.4f}"
    return cache.set(CacheType.ML_PREDICTION, location_key, data)


def get_cached_ml_prediction(crop: str, lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """Get cached ML prediction"""
    cache = get_cache()
    location_key = f"{crop}_{lat:.4f}_{lon:.4f}"
    return cache.get(CacheType.ML_PREDICTION, location_key)


def cache_location(lat: float, lon: float, data: Dict[str, Any]) -> bool:
    """Cache location data (permanent)"""
    cache = get_cache()
    location_key = f"{lat:.4f}_{lon:.4f}"
    return cache.set(CacheType.LOCATION, location_key, data)


def get_cached_location(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """Get cached location data"""
    cache = get_cache()
    location_key = f"{lat:.4f}_{lon:.4f}"
    return cache.get(CacheType.LOCATION, location_key)