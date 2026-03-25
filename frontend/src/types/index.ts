// Shared types for CloudPulse Monitor

export interface Metric {
  name: string;
  value: number;
  unit: string;
  status: 'healthy' | 'warning' | 'critical';
  trend: 'up' | 'down' | 'stable';
  timestamp?: string;
}

// API Metrics Response (matches backend design)
export interface MetricsApiResponse {
  cpu_usage: number;
  memory_usage: number;
  network_traffic: number;
  container_count: number;
  overall_health: number;
  timestamp: string;
}

export interface Service {
  id: string;
  name: string;
  uptime: number;
  status: 'online' | 'degraded' | 'offline';
  last_checked: string;
}

export interface LogEntry {
  id: string;
  timestamp: string;
  level: 'info' | 'warning' | 'error';
  message: string;
  service_name: string;
}

export interface SystemStatus {
  overall_status: 'healthy' | 'warning' | 'critical';
  services_online: number;
  services_total: number;
  critical_alerts: number;
  last_updated: string;
}

// Helper function to determine metric status
function getMetricStatus(value: number, criticalThreshold: number, warningThreshold: number): 'healthy' | 'warning' | 'critical' {
  if (value > criticalThreshold) return 'critical';
  if (value > warningThreshold) return 'warning';
  return 'healthy';
}

function getHealthStatus(value: number): 'healthy' | 'warning' | 'critical' {
  if (value > 90) return 'healthy';
  if (value > 70) return 'warning';
  return 'critical';
}

// Utility function to transform API response to UI metrics
export function transformMetricsResponse(apiResponse: MetricsApiResponse): Metric[] {
  return [
    {
      name: 'CPU Usage',
      value: apiResponse.cpu_usage,
      unit: '%',
      status: getMetricStatus(apiResponse.cpu_usage, 80, 60),
      trend: 'stable',
      timestamp: apiResponse.timestamp,
    },
    {
      name: 'Memory Usage',
      value: apiResponse.memory_usage,
      unit: '%',
      status: getMetricStatus(apiResponse.memory_usage, 85, 70),
      trend: 'stable',
      timestamp: apiResponse.timestamp,
    },
    {
      name: 'Network Traffic',
      value: apiResponse.network_traffic,
      unit: 'MB/s',
      status: apiResponse.network_traffic > 1000 ? 'warning' : 'healthy',
      trend: 'stable',
      timestamp: apiResponse.timestamp,
    },
    {
      name: 'Container Count',
      value: apiResponse.container_count,
      unit: 'containers',
      status: 'healthy',
      trend: 'stable',
      timestamp: apiResponse.timestamp,
    },
    {
      name: 'Overall Health',
      value: apiResponse.overall_health,
      unit: '%',
      status: getHealthStatus(apiResponse.overall_health),
      trend: 'stable',
      timestamp: apiResponse.timestamp,
    },
  ];
}

export interface ApiError {
  error: {
    code: string;
    message: string;
    details?: Record<string, any>;
    timestamp: string;
  };
}

// Monitoring types for external endpoint monitoring
export interface MonitoringTarget {
  id: number;
  name: string;
  target_url: string;
  target_type: 'http' | 'https' | 'ping' | 'dns';
  check_interval: number;
  timeout: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface MonitoringResult {
  id: number;
  target_id: number;
  status_code: number | null;
  response_time_ms: number | null;
  is_up: boolean;
  error_message: string | null;
  dns_resolution: string | null;
  timestamp: string;
}

export interface TargetWithLatestResult {
  target: MonitoringTarget;
  latest_result: MonitoringResult | null;
  uptime_percentage: number | null;
}

// Event types
export interface Event {
  id: number;
  event_type: string;
  message: string;
  severity: 'info' | 'warning' | 'critical';
  source: string | null;
  metadata: string | null;
  is_resolved: boolean;
  created_at: string;
  resolved_at: string | null;
}

// Real-time system metrics
export interface RealTimeSystemMetrics {
  cpu_percent: number;
  memory_percent: number;
  memory_used_mb: number;
  memory_total_mb: number;
  disk_percent: number;
  disk_used_gb: number;
  disk_total_gb: number;
  network_sent_rate: number;
  network_recv_rate: number;
  timestamp: string;
}

// System metrics snapshot
export interface SystemMetricsSnapshot {
  id: number;
  cpu_percent: number;
  memory_percent: number;
  memory_used_mb: number | null;
  memory_total_mb: number | null;
  disk_percent: number | null;
  disk_used_gb: number | null;
  disk_total_gb: number | null;
  bytes_sent: number | null;
  bytes_recv: number | null;
  network_sent_rate: number | null;
  network_recv_rate: number | null;
  timestamp: string;
}

// Detailed health response
export interface DetailedHealth {
  status: 'healthy' | 'degraded' | 'critical';
  cpu: number;
  memory: number;
  disk: number;
  active_events: number;
  critical_events: number;
  failing_services: number;
  timestamp: string;
}

// Metrics aggregates
export interface MetricsAggregates {
  cpu: { avg: number; min: number; max: number };
  memory: { avg: number; min: number; max: number };
  disk: { avg: number; min: number; max: number };
  network_sent_rate: { avg: number };
  network_recv_rate: { avg: number };
}

// Agent types
export interface Agent {
  id: number;
  name: string;
  hostname: string | null;
  ip_address: string | null;
  os_type: string | null;
  status: 'online' | 'offline';
  api_key: string;
  last_heartbeat: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AgentMetrics {
  id: number;
  agent_id: number;
  cpu_percent: number | null;
  memory_percent: number | null;
  memory_used_mb: number | null;
  memory_total_mb: number | null;
  disk_percent: number | null;
  disk_used_gb: number | null;
  disk_total_gb: number | null;
  network_sent_rate: number | null;
  network_recv_rate: number | null;
  load_avg: number | null;
  timestamp: string;
}

export interface HealthScore {
  score: number;
  grade: string;
  factors: Record<string, number>;
  details: {
    cpu_percent: number;
    memory_percent: number;
    disk_percent: number;
    active_events: number;
    critical_events: number;
    offline_services: number;
    total_services: number;
  };
  timestamp: string;
}