import asyncio
import logging
import time
import numpy as np
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json
import redis
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp

logger = logging.getLogger(__name__)

class OptimizationType(Enum):
    CACHING = "caching"
    PARALLEL_PROCESSING = "parallel_processing"
    MEMORY_OPTIMIZATION = "memory_optimization"
    DATABASE_OPTIMIZATION = "database_optimization"
    NETWORK_OPTIMIZATION = "network_optimization"

@dataclass
class PerformanceMetrics:
    execution_time: float
    memory_usage: float
    cpu_usage: float
    throughput: float
    latency: float
    timestamp: float

@dataclass
class OptimizationResult:
    optimization_type: OptimizationType
    improvement_percentage: float
    before_metrics: PerformanceMetrics
    after_metrics: PerformanceMetrics
    description: str

class PerformanceOptimizer:
    """Service for optimizing trading system performance"""
    
    def __init__(self, redis_host: str = "localhost", redis_port: int = 6379):
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.thread_pool = ThreadPoolExecutor(max_workers=mp.cpu_count())
        self.process_pool = ProcessPoolExecutor(max_workers=mp.cpu_count())
        self.performance_history: List[PerformanceMetrics] = []
        self.optimization_history: List[OptimizationResult] = []
        
    async def optimize_strategy_execution(self, strategies: List[Any], market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize strategy execution using parallel processing"""
        start_time = time.time()
        
        # Execute strategies in parallel
        loop = asyncio.get_event_loop()
        tasks = []
        
        for strategy in strategies:
            task = loop.run_in_executor(
                self.thread_pool, 
                self._execute_strategy_sync, 
                strategy, 
                market_data
            )
            tasks.append(task)
        
        # Wait for all strategies to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        execution_time = time.time() - start_time
        
        # Cache results
        cache_key = f"strategy_results_{int(time.time())}"
        self.redis_client.setex(cache_key, 300, json.dumps(results))  # 5 minute cache
        
        return {
            "results": results,
            "execution_time": execution_time,
            "cache_key": cache_key,
            "parallel_execution": True
        }
    
    def _execute_strategy_sync(self, strategy: Any, market_data: Dict[str, Any]) -> Any:
        """Synchronous strategy execution for thread pool"""
        try:
            # Simulate strategy execution
            time.sleep(0.01)  # Simulate processing time
            return {"strategy": strategy.__class__.__name__, "status": "completed"}
        except Exception as e:
            logger.error(f"Strategy execution error: {e}")
            return {"strategy": strategy.__class__.__name__, "status": "error", "error": str(e)}
    
    async def optimize_market_data_processing(self, raw_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Optimize market data processing using vectorized operations"""
        start_time = time.time()
        
        # Convert to numpy arrays for vectorized operations
        prices = np.array([item.get('price', 0) for item in raw_data])
        volumes = np.array([item.get('volume', 0) for item in raw_data])
        timestamps = np.array([item.get('timestamp', 0) for item in raw_data])
        
        # Vectorized calculations
        price_changes = np.diff(prices)
        volume_ma = np.convolve(volumes, np.ones(20)/20, mode='valid')
        volatility = np.std(price_changes[-50:]) if len(price_changes) >= 50 else 0
        
        # Calculate technical indicators
        sma_20 = np.mean(prices[-20:]) if len(prices) >= 20 else np.mean(prices)
        sma_50 = np.mean(prices[-50:]) if len(prices) >= 50 else np.mean(prices)
        
        processing_time = time.time() - start_time
        
        # Cache processed data
        cache_key = f"processed_data_{int(time.time())}"
        processed_data = {
            "prices": prices.tolist(),
            "volumes": volumes.tolist(),
            "timestamps": timestamps.tolist(),
            "price_changes": price_changes.tolist(),
            "volume_ma": volume_ma.tolist(),
            "volatility": float(volatility),
            "sma_20": float(sma_20),
            "sma_50": float(sma_50)
        }
        
        self.redis_client.setex(cache_key, 60, json.dumps(processed_data))  # 1 minute cache
        
        return {
            "processed_data": processed_data,
            "processing_time": processing_time,
            "cache_key": cache_key,
            "vectorized": True
        }
    
    async def optimize_database_queries(self, query_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize database queries using connection pooling and query optimization"""
        start_time = time.time()
        
        # Simulate database optimization
        if query_type == "market_data":
            # Use connection pooling and prepared statements
            optimized_query = self._optimize_market_data_query(parameters)
        elif query_type == "user_portfolio":
            # Use indexing and query optimization
            optimized_query = self._optimize_portfolio_query(parameters)
        else:
            optimized_query = parameters
        
        # Cache query results
        cache_key = f"db_query_{query_type}_{hash(str(parameters))}"
        self.redis_client.setex(cache_key, 300, json.dumps(optimized_query))  # 5 minute cache
        
        query_time = time.time() - start_time
        
        return {
            "query_result": optimized_query,
            "query_time": query_time,
            "cache_key": cache_key,
            "optimized": True
        }
    
    def _optimize_market_data_query(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize market data queries"""
        # Simulate query optimization
        return {
            "query_type": "market_data",
            "use_index": True,
            "connection_pooling": True,
            "prepared_statements": True,
            "parameters": parameters
        }
    
    def _optimize_portfolio_query(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize portfolio queries"""
        # Simulate query optimization
        return {
            "query_type": "portfolio",
            "use_index": True,
            "query_optimization": True,
            "parameters": parameters
        }
    
    async def optimize_websocket_connections(self, connections: List[Any]) -> Dict[str, Any]:
        """Optimize WebSocket connections for better performance"""
        start_time = time.time()
        
        # Implement connection pooling and load balancing
        optimized_connections = []
        
        for conn in connections:
            # Optimize connection settings
            optimized_conn = {
                "connection_id": id(conn),
                "compression": True,
                "heartbeat_interval": 30,
                "max_message_size": 1024 * 1024,  # 1MB
                "connection_pool": True
            }
            optimized_connections.append(optimized_conn)
        
        # Cache connection configurations
        cache_key = "websocket_config"
        self.redis_client.setex(cache_key, 3600, json.dumps(optimized_connections))  # 1 hour cache
        
        optimization_time = time.time() - start_time
        
        return {
            "optimized_connections": optimized_connections,
            "optimization_time": optimization_time,
            "cache_key": cache_key,
            "compression_enabled": True
        }
    
    async def get_performance_metrics(self) -> PerformanceMetrics:
        """Get current performance metrics"""
        import psutil
        
        process = psutil.Process()
        memory_info = process.memory_info()
        
        metrics = PerformanceMetrics(
            execution_time=time.time(),
            memory_usage=memory_info.rss / 1024 / 1024,  # MB
            cpu_usage=psutil.cpu_percent(),
            throughput=len(self.performance_history) / max(1, time.time() - self.performance_history[0].timestamp if self.performance_history else 0),
            latency=0.001,  # Simulated latency
            timestamp=time.time()
        )
        
        self.performance_history.append(metrics)
        
        # Keep only last 1000 metrics
        if len(self.performance_history) > 1000:
            self.performance_history = self.performance_history[-1000:]
        
        return metrics
    
    async def run_performance_analysis(self) -> Dict[str, Any]:
        """Run comprehensive performance analysis"""
        start_time = time.time()
        
        # Get current metrics
        current_metrics = await self.get_performance_metrics()
        
        # Analyze performance trends
        if len(self.performance_history) > 10:
            recent_metrics = self.performance_history[-10:]
            avg_memory = np.mean([m.memory_usage for m in recent_metrics])
            avg_cpu = np.mean([m.cpu_usage for m in recent_metrics])
            
            # Identify bottlenecks
            bottlenecks = []
            if avg_memory > 500:  # 500MB threshold
                bottlenecks.append("High memory usage")
            if avg_cpu > 80:  # 80% CPU threshold
                bottlenecks.append("High CPU usage")
            
            analysis = {
                "current_metrics": current_metrics,
                "average_memory_mb": avg_memory,
                "average_cpu_percent": avg_cpu,
                "bottlenecks": bottlenecks,
                "recommendations": self._generate_recommendations(bottlenecks)
            }
        else:
            analysis = {
                "current_metrics": current_metrics,
                "insufficient_data": True
            }
        
        analysis_time = time.time() - start_time
        
        return {
            "analysis": analysis,
            "analysis_time": analysis_time,
            "timestamp": time.time()
        }
    
    def _generate_recommendations(self, bottlenecks: List[str]) -> List[str]:
        """Generate optimization recommendations based on bottlenecks"""
        recommendations = []
        
        if "High memory usage" in bottlenecks:
            recommendations.extend([
                "Implement object pooling",
                "Use lazy loading for large datasets",
                "Optimize data structures"
            ])
        
        if "High CPU usage" in bottlenecks:
            recommendations.extend([
                "Implement caching strategies",
                "Use parallel processing",
                "Optimize algorithms"
            ])
        
        return recommendations
    
    async def clear_cache(self, pattern: str = "*") -> Dict[str, Any]:
        """Clear cache entries matching pattern"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                deleted = self.redis_client.delete(*keys)
                return {"deleted_keys": deleted, "pattern": pattern, "success": True}
            else:
                return {"deleted_keys": 0, "pattern": pattern, "success": True}
        except Exception as e:
            logger.error(f"Cache clearing error: {e}")
            return {"error": str(e), "success": False}
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            info = self.redis_client.info()
            return {
                "total_connections_received": info.get("total_connections_received", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "connected_clients": info.get("connected_clients", 0)
            }
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {"error": str(e)}
