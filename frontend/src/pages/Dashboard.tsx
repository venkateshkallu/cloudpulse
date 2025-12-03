import { MetricCard } from "@/components/MetricCard";
import { useMetrics, useSystemStatus } from "@/hooks/useApi";
import { Activity, AlertCircle, Loader2, RefreshCw } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";

const Dashboard = () => {
  const { 
    data: metrics, 
    isLoading: metricsLoading, 
    error: metricsError,
    refetch: refetchMetrics 
  } = useMetrics();
  
  const { 
    data: status, 
    isLoading: statusLoading, 
    error: statusError,
    refetch: refetchStatus 
  } = useSystemStatus();

  const isLoading = metricsLoading || statusLoading;
  const hasError = metricsError || statusError;

  const handleRefresh = () => {
    refetchMetrics();
    refetchStatus();
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
            Failed to load dashboard data: {metricsError?.message || statusError?.message || 'Unknown error'}
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

      {status && (
        <div className="bg-card border border-border rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold">System Status</h3>
              <p className="text-sm text-muted-foreground">
                {status.services_online} of {status.services_total} services online
              </p>
            </div>
            <div className={`px-3 py-1 rounded-full text-sm font-medium ${
              status.overall_status === 'healthy' 
                ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                : status.overall_status === 'warning'
                ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
            }`}>
              {status.overall_status.charAt(0).toUpperCase() + status.overall_status.slice(1)}
            </div>
          </div>
          {status.critical_alerts > 0 && (
            <p className="text-sm text-red-600 dark:text-red-400 mt-2">
              {status.critical_alerts} critical alert{status.critical_alerts !== 1 ? 's' : ''} active
            </p>
          )}
        </div>
      )}

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2 text-muted-foreground">Loading metrics...</span>
        </div>
      ) : metrics && metrics.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
          {metrics.map((metric) => (
            <MetricCard
              key={metric.name}
              name={metric.name}
              value={metric.value}
              unit={metric.unit}
              status={metric.status}
              trend={metric.trend}
            />
          ))}
        </div>
      ) : !hasError ? (
        <div className="flex items-center justify-center py-12 text-muted-foreground">
          No metrics data available
        </div>
      ) : null}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-8">
        <div className="bg-card border border-border rounded-lg p-6">
          <h3 className="text-lg font-semibold text-foreground mb-4">Performance Overview</h3>
          <div className="h-64 flex items-center justify-center text-muted-foreground">
            Chart placeholder - Ready for backend integration
          </div>
        </div>
        
        <div className="bg-card border border-border rounded-lg p-6">
          <h3 className="text-lg font-semibold text-foreground mb-4">Traffic Analysis</h3>
          <div className="h-64 flex items-center justify-center text-muted-foreground">
            Chart placeholder - Ready for backend integration
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
