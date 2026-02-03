#!/usr/bin/env python3
"""
Performance test suite for API optimization
Target: <2s response times with caching
"""
import time
import requests
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
import json


class PerformanceTest:
    """Performance testing for farming advisory API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_locations = [
            (40.0, -95.0, "Midwest USA"),
            (28.6139, 77.2090, "New Delhi, India"),
            (37.7749, -122.4194, "San Francisco, USA"),
            (-23.5505, -46.6333, "São Paulo, Brazil"),
            (51.5074, -0.1278, "London, UK")
        ]
    
    def test_response_times(self, endpoint: str, iterations: int = 10) -> Dict[str, Any]:
        """Test response times for a specific endpoint"""
        print(f"🚀 Testing {endpoint} performance ({iterations} iterations)")
        
        response_times = []
        cache_hits = 0
        errors = 0
        
        for i in range(iterations):
            lat, lon, location = self.test_locations[i % len(self.test_locations)]
            
            try:
                start_time = time.time()
                
                if endpoint == "quick":
                    response = requests.post(
                        f"{self.base_url}/recommendations/quick",
                        json={"latitude": lat, "longitude": lon},
                        timeout=10
                    )
                elif endpoint == "comprehensive":
                    response = requests.post(
                        f"{self.base_url}/recommendations/comprehensive",
                        json={"latitude": lat, "longitude": lon, "max_crops": 3},
                        timeout=15
                    )
                elif endpoint == "ndvi":
                    response = requests.get(
                        f"{self.base_url}/ndvi/{lat}/{lon}",
                        timeout=10
                    )
                else:
                    continue
                
                end_time = time.time()
                response_time = end_time - start_time
                
                if response.status_code == 200:
                    response_times.append(response_time)
                    
                    # Check if response was cached
                    data = response.json()
                    if self._is_cached_response(data):
                        cache_hits += 1
                    
                    print(f"   {i+1:2d}. {location:20s} - {response_time:.3f}s {'(cached)' if self._is_cached_response(data) else ''}")
                else:
                    errors += 1
                    print(f"   {i+1:2d}. {location:20s} - ERROR {response.status_code}")
                
            except Exception as e:
                errors += 1
                print(f"   {i+1:2d}. {location:20s} - EXCEPTION: {e}")
        
        if response_times:
            stats = {
                'endpoint': endpoint,
                'iterations': iterations,
                'successful_requests': len(response_times),
                'errors': errors,
                'cache_hits': cache_hits,
                'cache_hit_rate': cache_hits / len(response_times) if response_times else 0,
                'min_time': min(response_times),
                'max_time': max(response_times),
                'avg_time': statistics.mean(response_times),
                'median_time': statistics.median(response_times),
                'p95_time': self._percentile(response_times, 95),
                'under_2s': sum(1 for t in response_times if t < 2.0),
                'under_1s': sum(1 for t in response_times if t < 1.0),
                'target_compliance': sum(1 for t in response_times if t < 2.0) / len(response_times)
            }
            
            return stats
        else:
            return {'endpoint': endpoint, 'error': 'No successful requests'}
    
    def test_concurrent_load(self, max_workers: int = 5, requests_per_worker: int = 3) -> Dict[str, Any]:
        """Test concurrent load performance"""
        print(f"🔥 Testing concurrent load ({max_workers} workers, {requests_per_worker} requests each)")
        
        def make_request(worker_id: int, request_id: int) -> Dict[str, Any]:
            lat, lon, location = self.test_locations[(worker_id + request_id) % len(self.test_locations)]
            
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.base_url}/recommendations/quick",
                    json={"latitude": lat, "longitude": lon},
                    timeout=10
                )
                end_time = time.time()
                
                return {
                    'worker_id': worker_id,
                    'request_id': request_id,
                    'location': location,
                    'response_time': end_time - start_time,
                    'status_code': response.status_code,
                    'success': response.status_code == 200,
                    'cached': self._is_cached_response(response.json()) if response.status_code == 200 else False
                }
            except Exception as e:
                return {
                    'worker_id': worker_id,
                    'request_id': request_id,
                    'location': location,
                    'error': str(e),
                    'success': False
                }
        
        # Execute concurrent requests
        start_time = time.time()
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            
            for worker_id in range(max_workers):
                for request_id in range(requests_per_worker):
                    future = executor.submit(make_request, worker_id, request_id)
                    futures.append(future)
            
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                
                if result['success']:
                    cached_str = " (cached)" if result.get('cached') else ""
                    print(f"   Worker {result['worker_id']}-{result['request_id']}: {result['location']:20s} - {result['response_time']:.3f}s{cached_str}")
                else:
                    print(f"   Worker {result['worker_id']}-{result['request_id']}: {result['location']:20s} - ERROR")
        
        total_time = time.time() - start_time
        
        # Analyze results
        successful_results = [r for r in results if r['success']]
        response_times = [r['response_time'] for r in successful_results]
        
        if response_times:
            return {
                'total_requests': len(results),
                'successful_requests': len(successful_results),
                'total_time': total_time,
                'requests_per_second': len(successful_results) / total_time,
                'avg_response_time': statistics.mean(response_times),
                'max_response_time': max(response_times),
                'target_compliance': sum(1 for t in response_times if t < 2.0) / len(response_times),
                'cache_hits': sum(1 for r in successful_results if r.get('cached')),
                'cache_hit_rate': sum(1 for r in successful_results if r.get('cached')) / len(successful_results)
            }
        else:
            return {'error': 'No successful requests in concurrent test'}
    
    def test_cache_effectiveness(self) -> Dict[str, Any]:
        """Test cache effectiveness by making repeated requests"""
        print("💾 Testing cache effectiveness")
        
        lat, lon = 40.0, -95.0
        
        # First request (should miss cache)
        print("   Making first request (cache miss expected)...")
        start_time = time.time()
        response1 = requests.post(
            f"{self.base_url}/recommendations/quick",
            json={"latitude": lat, "longitude": lon}
        )
        time1 = time.time() - start_time
        
        # Second request (should hit cache)
        print("   Making second request (cache hit expected)...")
        start_time = time.time()
        response2 = requests.post(
            f"{self.base_url}/recommendations/quick",
            json={"latitude": lat, "longitude": lon}
        )
        time2 = time.time() - start_time
        
        # Third request (should hit cache)
        print("   Making third request (cache hit expected)...")
        start_time = time.time()
        response3 = requests.post(
            f"{self.base_url}/recommendations/quick",
            json={"latitude": lat, "longitude": lon}
        )
        time3 = time.time() - start_time
        
        return {
            'first_request_time': time1,
            'second_request_time': time2,
            'third_request_time': time3,
            'cache_speedup': time1 / time2 if time2 > 0 else 0,
            'consistent_caching': abs(time2 - time3) < 0.1,
            'all_successful': all(r.status_code == 200 for r in [response1, response2, response3])
        }
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get current cache statistics"""
        try:
            response = requests.get(f"{self.base_url}/cache/stats")
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': f'Cache stats request failed: {response.status_code}'}
        except Exception as e:
            return {'error': f'Cache stats request failed: {e}'}
    
    def _is_cached_response(self, data: Dict[str, Any]) -> bool:
        """Check if response indicates cached data"""
        # Check various places where cached flag might be
        if isinstance(data, dict):
            # Check top level
            if data.get('cached'):
                return True
            
            # Check in environmental conditions
            env_conditions = data.get('environmental_conditions', {})
            if any(env_conditions.get(key, {}).get('cached') for key in ['current_weather', 'soil_analysis', 'ndvi_analysis']):
                return True
            
            # Check in yield predictions
            yield_preds = data.get('crop_recommendations', {}).get('yield_predictions', {})
            if any(pred.get('cached') for pred in yield_preds.values()):
                return True
        
        return False
    
    def _percentile(self, data: List[float], percentile: float) -> float:
        """Calculate percentile"""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]


def main():
    """Run performance test suite"""
    print("🚀 API PERFORMANCE OPTIMIZATION TEST SUITE")
    print("=" * 60)
    print("Target: <2s response times with intelligent caching")
    print()
    
    tester = PerformanceTest()
    
    # Test individual endpoints
    endpoints = ["quick", "comprehensive", "ndvi"]
    results = {}
    
    for endpoint in endpoints:
        print(f"\n{'=' * 60}")
        result = tester.test_response_times(endpoint, iterations=8)
        results[endpoint] = result
        
        if 'error' not in result:
            print(f"\n📊 {endpoint.title()} Endpoint Results:")
            print(f"   Average Response Time: {result['avg_time']:.3f}s")
            print(f"   95th Percentile: {result['p95_time']:.3f}s")
            print(f"   Target Compliance (<2s): {result['target_compliance']:.1%}")
            print(f"   Cache Hit Rate: {result['cache_hit_rate']:.1%}")
            print(f"   Requests under 1s: {result['under_1s']}/{result['successful_requests']}")
    
    # Test concurrent load
    print(f"\n{'=' * 60}")
    concurrent_result = tester.test_concurrent_load()
    results['concurrent'] = concurrent_result
    
    if 'error' not in concurrent_result:
        print(f"\n📊 Concurrent Load Results:")
        print(f"   Requests per Second: {concurrent_result['requests_per_second']:.1f}")
        print(f"   Average Response Time: {concurrent_result['avg_response_time']:.3f}s")
        print(f"   Target Compliance: {concurrent_result['target_compliance']:.1%}")
        print(f"   Cache Hit Rate: {concurrent_result['cache_hit_rate']:.1%}")
    
    # Test cache effectiveness
    print(f"\n{'=' * 60}")
    cache_result = tester.test_cache_effectiveness()
    results['cache_effectiveness'] = cache_result
    
    print(f"\n📊 Cache Effectiveness Results:")
    print(f"   First Request: {cache_result['first_request_time']:.3f}s")
    print(f"   Second Request: {cache_result['second_request_time']:.3f}s")
    print(f"   Cache Speedup: {cache_result['cache_speedup']:.1f}x")
    print(f"   Consistent Caching: {'✅' if cache_result['consistent_caching'] else '❌'}")
    
    # Get cache statistics
    print(f"\n{'=' * 60}")
    cache_stats = tester.get_cache_stats()
    results['cache_stats'] = cache_stats
    
    if 'error' not in cache_stats:
        perf_stats = cache_stats.get('cache_performance', {})
        print(f"\n📊 Cache Statistics:")
        print(f"   Hit Rate: {perf_stats.get('hit_rate', 0):.1%}")
        print(f"   Total Requests: {perf_stats.get('total_requests', 0)}")
        print(f"   Cache Size: {perf_stats.get('cache_size', 0)} entries")
        print(f"   Average Response Time: {perf_stats.get('avg_response_time_ms', 0):.1f}ms")
    
    # Final assessment
    print(f"\n{'=' * 60}")
    print("🎯 PERFORMANCE ASSESSMENT")
    print("=" * 60)
    
    # Calculate overall compliance
    compliances = []
    for endpoint in endpoints:
        if endpoint in results and 'target_compliance' in results[endpoint]:
            compliances.append(results[endpoint]['target_compliance'])
    
    if compliances:
        overall_compliance = sum(compliances) / len(compliances)
        print(f"Overall <2s Compliance: {overall_compliance:.1%}")
        
        if overall_compliance >= 0.9:
            print("🎉 EXCELLENT: API meets <2s target!")
        elif overall_compliance >= 0.7:
            print("✅ GOOD: API mostly meets <2s target")
        elif overall_compliance >= 0.5:
            print("⚠️ FAIR: API partially meets <2s target")
        else:
            print("❌ POOR: API does not meet <2s target")
    
    # Save results
    with open('performance_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: performance_results.json")


if __name__ == "__main__":
    main()