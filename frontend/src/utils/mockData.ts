export interface Metric {
  name: string;
  value: number;
  unit: string;
  status: "healthy" | "warning" | "critical";
  trend: "up" | "down" | "stable";
}

export interface Service {
  id: string;
  name: string;
  uptime: number;
  status: "online" | "degraded" | "offline";
  lastChecked: string;
}

export interface LogEntry {
  id: string;
  timestamp: string;
  level: "info" | "warning" | "error";
  message: string;
  source: string;
}

export const mockMetrics: Metric[] = [
  {
    name: "CPU Usage",
    value: 45.2,
    unit: "%",
    status: "healthy",
    trend: "stable",
  },
  {
    name: "Memory Usage",
    value: 68.7,
    unit: "%",
    status: "warning",
    trend: "up",
  },
  {
    name: "Network Traffic",
    value: 342.5,
    unit: "MB/s",
    status: "healthy",
    trend: "up",
  },
  {
    name: "Running Containers",
    value: 24,
    unit: "containers",
    status: "healthy",
    trend: "stable",
  },
  {
    name: "Overall Health",
    value: 92,
    unit: "%",
    status: "healthy",
    trend: "stable",
  },
];

export const mockServices: Service[] = [
  {
    id: "1",
    name: "API Gateway",
    uptime: 99.98,
    status: "online",
    lastChecked: new Date(Date.now() - 1000 * 30).toISOString(),
  },
  {
    id: "2",
    name: "Database Cluster",
    uptime: 99.95,
    status: "online",
    lastChecked: new Date(Date.now() - 1000 * 45).toISOString(),
  },
  {
    id: "3",
    name: "Cache Layer",
    uptime: 98.2,
    status: "degraded",
    lastChecked: new Date(Date.now() - 1000 * 60).toISOString(),
  },
  {
    id: "4",
    name: "Load Balancer",
    uptime: 100,
    status: "online",
    lastChecked: new Date(Date.now() - 1000 * 15).toISOString(),
  },
  {
    id: "5",
    name: "Message Queue",
    uptime: 99.99,
    status: "online",
    lastChecked: new Date(Date.now() - 1000 * 20).toISOString(),
  },
  {
    id: "6",
    name: "Storage Service",
    uptime: 97.5,
    status: "degraded",
    lastChecked: new Date(Date.now() - 1000 * 90).toISOString(),
  },
];

export const mockLogs: LogEntry[] = [
  {
    id: "1",
    timestamp: new Date(Date.now() - 1000 * 60 * 2).toISOString(),
    level: "info",
    message: "System health check completed successfully",
    source: "health-monitor",
  },
  {
    id: "2",
    timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
    level: "warning",
    message: "Memory usage approaching threshold (68%)",
    source: "resource-monitor",
  },
  {
    id: "3",
    timestamp: new Date(Date.now() - 1000 * 60 * 8).toISOString(),
    level: "info",
    message: "Container deployment completed: api-service-v2.1",
    source: "orchestrator",
  },
  {
    id: "4",
    timestamp: new Date(Date.now() - 1000 * 60 * 12).toISOString(),
    level: "error",
    message: "Failed to connect to backup database node",
    source: "database-cluster",
  },
  {
    id: "5",
    timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
    level: "info",
    message: "Auto-scaling triggered: +2 instances",
    source: "auto-scaler",
  },
  {
    id: "6",
    timestamp: new Date(Date.now() - 1000 * 60 * 20).toISOString(),
    level: "warning",
    message: "SSL certificate expires in 30 days",
    source: "security-monitor",
  },
  {
    id: "7",
    timestamp: new Date(Date.now() - 1000 * 60 * 25).toISOString(),
    level: "info",
    message: "Backup completed successfully (2.4 GB)",
    source: "backup-service",
  },
  {
    id: "8",
    timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    level: "info",
    message: "Load balancer health check passed",
    source: "load-balancer",
  },
];
