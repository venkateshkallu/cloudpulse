import { Card, CardContent } from "@/components/ui/card";
import { StatusBadge } from "@/components/StatusBadge";
import { useLogs } from "@/hooks/useApi";
import { ScrollText, AlertCircle, Loader2, RefreshCw, Filter } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { formatDistanceToNow } from "date-fns";
import { useState } from "react";

const Logs = () => {
  const [levelFilter, setLevelFilter] = useState<string>('');
  const [serviceFilter, setServiceFilter] = useState<string>('');
  
  const { 
    data: logs, 
    isLoading, 
    error,
    refetch 
  } = useLogs({ 
    limit: 50,
    level: levelFilter || undefined,
    service: serviceFilter || undefined,
  });

  const handleRefresh = () => {
    refetch();
  };

  const clearFilters = () => {
    setLevelFilter('');
    setServiceFilter('');
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <ScrollText className="h-8 w-8 text-primary" />
          <div>
            <h1 className="text-3xl font-bold text-foreground">System Logs</h1>
            <p className="text-muted-foreground">Recent activity and events from all services</p>
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

      <div className="flex items-center gap-4 p-4 bg-card border border-border rounded-lg">
        <Filter className="h-4 w-4 text-muted-foreground" />
        <div className="flex items-center gap-2">
          <label htmlFor="level-filter" className="text-sm font-medium">Level:</label>
          <Select value={levelFilter} onValueChange={setLevelFilter}>
            <SelectTrigger id="level-filter" className="w-32">
              <SelectValue placeholder="All" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All</SelectItem>
              <SelectItem value="info">Info</SelectItem>
              <SelectItem value="warning">Warning</SelectItem>
              <SelectItem value="error">Error</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="flex items-center gap-2">
          <label htmlFor="service-filter" className="text-sm font-medium">Service:</label>
          <Select value={serviceFilter} onValueChange={setServiceFilter}>
            <SelectTrigger id="service-filter" className="w-40">
              <SelectValue placeholder="All services" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All services</SelectItem>
              <SelectItem value="api-gateway">API Gateway</SelectItem>
              <SelectItem value="user-service">User Service</SelectItem>
              <SelectItem value="auth-service">Auth Service</SelectItem>
              <SelectItem value="notification-service">Notification Service</SelectItem>
              <SelectItem value="database">Database</SelectItem>
              <SelectItem value="redis-cache">Redis Cache</SelectItem>
              <SelectItem value="analytics-service">Analytics Service</SelectItem>
              <SelectItem value="payment-service">Payment Service</SelectItem>
              <SelectItem value="file-storage">File Storage</SelectItem>
            </SelectContent>
          </Select>
        </div>
        {(levelFilter || serviceFilter) && (
          <Button variant="ghost" size="sm" onClick={clearFilters}>
            Clear filters
          </Button>
        )}
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Failed to load logs: {error.message}
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

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2 text-muted-foreground">Loading logs...</span>
        </div>
      ) : (
        <>
          {logs && logs.length > 0 ? (
            <div className="space-y-3">
              {logs.map((log) => (
                <Card key={log.id} className="hover:shadow-md transition-shadow duration-200">
                  <CardContent className="p-4">
                    <div className="flex items-start gap-4">
                      <StatusBadge status={log.level} className="mt-1" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-foreground">{log.message}</p>
                        <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                          <span className="font-mono">{log.service_name}</span>
                          <span>•</span>
                          <span>{formatDistanceToNow(new Date(log.timestamp), { addSuffix: true })}</span>
                        </div>
                      </div>
                      <div className="text-xs text-muted-foreground whitespace-nowrap">
                        {new Date(log.timestamp).toLocaleTimeString()}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <>
              {!error && (
                <div className="text-center py-12 text-muted-foreground">
                  No logs found {(levelFilter || serviceFilter) ? 'matching the current filters' : ''}
                </div>
              )}
            </>
          )}
        </>
      )}
    </div>
  );
};

export default Logs;
