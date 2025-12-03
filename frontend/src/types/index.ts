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