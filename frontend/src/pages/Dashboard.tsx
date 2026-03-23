import { MetricCard } from "@/components/MetricCard";
import { useSystemMetrics, useHealth, useRecentEvents } from "@/hooks/useApi";
import { Activity, AlertCircle, Loader2, RefreshCw, AlertTriangle, Bell } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const Dashboard = () => {
  const { 
    data: systemMetrics, 
    isLoading: metricsLoading, 
    error: metricsError,
    refetch: refetchMetrics 
  } = useSystemMetrics();
  
  const { 
    data: health, 
    isLoading: healthLoading, 
    error: healthError,
    refetch: refetchHealth 
  } = useHealth();

  const { data: recentEvents } = useRecentEvents(1); // Last 1 hour

  const isLoading = metricsLoading || healthLoading;
  const hasError = metricsError || healthError;

  const handleRefresh = () => {
    refetchMetrics();
    refetchHealth();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'degraded':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      case 'critical':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getMetricStatus = (value: number, critical: number, warning: number) => {
    if (value > critical) return 'critical';
    if (value > warning) return 'warning';
    return 'healthy';
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Activity className="h-8 w-8 text-primary" />
          <div>
            <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
            <p className="text-muted-foreground">Real-time system metrics and health status</p>
          </div>
        </div>
        <Button 
          variant="outline" 
          size="sm" 
          onClick={handleRefresh}
          disabled={isLoading}
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {hasError && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Failed to load dashboard data
            <Button 
              variant="link" 
              size="sm" 
              onClick={handleRefresh}
              className="ml-2 p-0 h-auto"
            >
              Try again
            </Button>
          </AlertDescription>
        </Alert>
      )}

      {/* Real Health Status */}
      {health && (
        <div className="bg-card border border-border rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold">System Health</h3>
              <p className="text-sm text-muted-foreground">
                CPU: {health.cpu.toFixed(1)}% | Memory: {health.memory.toFixed(1)}% | Disk: {health.disk.toFixed(1)}%
              </p>
            </div>
            <div className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(health.status)}`}>
              {health.status.charAt(0).toUpperCase() + health.status.slice(1)}
            </div>
          </div>
          <div className="flex gap-4 mt-3 text-sm">
            <span className="text-muted-foreground">
              Active Events: <span className="font-medium text-foreground">{health.active_events}</span>
            </span>
            <span className="text-muted-foreground">
              Critical: <span className="font-medium text-red-500">{health.critical_events}</span>
            </span>
            <span className="text-muted-foreground">
              Failing Services: <span className="font-medium text-red-500">{health.failing_services}</span>
            </span>
          </div>
        </div>
      )}

      {/* Real System Metrics */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2 text-muted-foreground">Loading metrics...</span>
        </div>
      ) : systemMetrics ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            name="CPU Usage"
            value={systemMetrics.cpu_percent}
            unit="%"
            status={getMetricStatus(systemMetrics.cpu_percent, 80, 60)}
            trend="stable"
          />
          <MetricCard
            name="Memory Usage"
            value={systemMetrics.memory_percent}
            unit="%"
            status={getMetricStatus(systemMetrics.memory_percent, 85, 70)}
            trend="stable"
          />
          <MetricCard
            name="Disk Usage"
            value={systemMetrics.disk_percent}
            unit="%"
            status={getMetricStatus(systemMetrics.disk_percent, 90, 80)}
            trend="stable"
          />
          <MetricCard
            name="Network In"
            value={systemMetrics.network_recv_rate / 1024}
            unit="KB/s"
            status="healthy"
            trend="stable"
          />
        </div>
      ) : !hasError ? (
        <div className="flex items-center justify-center py-12 text-muted-foreground">
          No metrics data available
        </div>
      ) : null}

      {/* Memory Details */}
      {systemMetrics && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Memory Details</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Used</span>
                  <span className="font-medium">{systemMetrics.memory_used_mb.toFixed(0)} MB</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Total</span>
                  <span className="font-medium">{systemMetrics.memory_total_mb.toFixed(0)} MB</span>
                </div>
                <div className="w-full bg-secondary rounded-full h-2">
                  <div 
                    className="bg-primary h-2 rounded-full" 
                    style={{ width: `${systemMetrics.memory_percent}%` }}
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Disk Details</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Used</span>
                  <span className="font-medium">{systemMetrics.disk_used_gb.toFixed(1)} GB</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Total</span>
                  <span className="font-medium">{systemMetrics.disk_total_gb.toFixed(1)} GB</span>
                </div>
                <div className="w-full bg-secondary rounded-full h-2">
                  <div 
                    className="bg-primary h-2 rounded-full" 
                    style={{ width: `${systemMetrics.disk_percent}%` }}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Recent Events */}
      {recentEvents && recentEvents.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg flex items-center gap-2">
              <Bell className="h-5 w-5" />
              Recent Events (Last Hour)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {recentEvents.slice(0, 5).map((event) => (
                <div key={event.id} className="flex items-center gap-3 text-sm">
                  {event.severity === 'critical' && <AlertCircle className="h-4 w-4 text-red-500" />}
                  {event.severity === 'warning' && <AlertTriangle className="h-4 w-4 text-yellow-500" />}
                  {event.severity === 'info' && <Activity className="h-4 w-4 text-blue-500" />}
                  <span className="flex-1">{event.message}</span>
                  <Badge variant={event.severity === 'critical' ? 'destructive' : 'secondary'}>
                    {event.severity}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default Dashboard;