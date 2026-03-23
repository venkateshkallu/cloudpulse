#!/usr/bin/env python3
"""
CloudPulse Agent - Lightweight monitoring agent for remote machines
Run on any machine you want to monitor
"""

import psutil
import time
import requests
import socket
import platform
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CloudPulseAgent:
    def __init__(self, api_url: str, api_key: str, interval: int = 10):
        """
        Initialize the agent
        
        Args:
            api_url: Base URL of the CloudPulse backend
            api_key: API key for authentication
            interval: Seconds between metric submissions
        """
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.interval = interval
        self.hostname = socket.gethostname()
        self.ip_address = self._get_ip_address()
        self.os_type = platform.system().lower()
        
        # For network rate calculation
        self._prev_net = None
        self._prev_time = None
        
    def _get_ip_address(self) -> str:
        """Get the primary IP address of this machine"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"
    
    def collect_metrics(self) -> Dict[str, Any]:
        """Collect system metrics using psutil"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Memory
            memory = psutil.virtual_memory()
            
            # Disk
            disk = psutil.disk_usage('/')
            
            # Network - calculate rate
            net_io = psutil.net_io_counters()
            current_time = time.time()
            
            network_sent_rate = 0.0
            network_recv_rate = 0.0
            
            if self._prev_net is not None and self._prev_time is not None:
                time_diff = current_time - self._prev_time
                if time_diff > 0:
                    network_sent_rate = (net_io.bytes_sent - self._prev_net.bytes_sent) / time_diff
                    network_recv_rate = (net_io.bytes_recv - self._prev_net.bytes_recv) / time_diff
                    network_sent_rate = max(0, network_sent_rate)
                    network_recv_rate = max(0, network_recv_rate)
            
            self._prev_net = net_io
            self._prev_time = current_time
            
            # Load average (Linux only)
            load_avg = None
            if hasattr(os, 'getloadavg'):
                import os
                load_avg = os.getloadavg()[0]
            
            return {
                "cpu_percent": round(cpu_percent, 2),
                "memory_percent": round(memory.percent, 2),
                "memory_used_mb": round(memory.used / (1024 * 1024), 2),
                "memory_total_mb": round(memory.total / (1024 * 1024), 2),
                "disk_percent": round(disk.percent, 2),
                "disk_used_gb": round(disk.used / (1024 * 1024 * 1024), 2),
                "disk_total_gb": round(disk.total / (1024 * 1024 * 1024), 2),
                "network_sent_rate": round(network_sent_rate, 2),
                "network_recv_rate": round(network_recv_rate, 2),
                "load_avg": round(load_avg, 2) if load_avg else None,
                "hostname": self.hostname,
                "ip_address": self.ip_address,
                "os_type": self.os_type
            }
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            raise
    
    def register(self) -> Dict[str, Any]:
        """Register this agent with the backend"""
        try:
            response = requests.post(
                f"{self.api_url}/api/agents/register",
                json={
                    "name": self.hostname,
                    "hostname": self.hostname,
                    "os_type": self.os_type
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            logger.info(f"Agent registered successfully: {data.get('id')}")
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to register agent: {e}")
            raise
    
    def send_heartbeat(self) -> bool:
        """Send heartbeat to backend"""
        try:
            response = requests.post(
                f"{self.api_url}/api/agents/heartbeat",
                headers={"X-API-Key": self.api_key},
                timeout=10
            )
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            logger.warning(f"Heartbeat failed: {e}")
            return False
    
    def send_metrics(self, metrics: Dict[str, Any]) -> bool:
        """Send metrics to backend"""
        try:
            response = requests.post(
                f"{self.api_url}/api/agents/submit-metrics?api_key={self.api_key}",
                json=metrics,
                timeout=10
            )
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send metrics: {e}")
            return False
    
    def run(self):
        """Main loop - collect and send metrics"""
        logger.info(f"Starting CloudPulse Agent for {self.hostname}")
        logger.info(f"API URL: {self.api_url}")
        logger.info(f"Interval: {self.interval}s")
        
        # Initial registration
        if not self.api_key:
            logger.info("No API key provided, attempting registration...")
            try:
                agent_data = self.register()
                self.api_key = agent_data.get('api_key')
                logger.info(f"Registered with ID: {agent_data.get('id')}")
            except Exception as e:
                logger.error(f"Registration failed: {e}")
                return
        
        # Main loop
        while True:
            try:
                metrics = self.collect_metrics()
                
                if self.send_metrics(metrics):
                    logger.debug(f"Metrics sent: CPU={metrics['cpu_percent']}%, "
                               f"Memory={metrics['memory_percent']}%, "
                               f"Disk={metrics['disk_percent']}%")
                else:
                    logger.warning("Failed to send metrics")
                
                # Send heartbeat occasionally
                if int(time.time()) % 60 < self.interval:
                    self.send_heartbeat()
                    
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
            
            time.sleep(self.interval)


if __name__ == "__main__":
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description="CloudPulse Monitoring Agent")
    parser.add_argument(
        "--api-url",
        default=os.environ.get("CLOUDPULSE_API_URL", "http://localhost:8000"),
        help="CloudPulse API URL"
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("CLOUDPULSE_API_KEY", ""),
        help="API key for authentication"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=10,
        help="Seconds between metric submissions"
    )
    
    args = parser.parse_args()
    
    agent = CloudPulseAgent(
        api_url=args.api_url,
        api_key=args.api_key,
        interval=args.interval
    )
    agent.run()