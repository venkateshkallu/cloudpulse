import { useState } from 'react';
import { useEvents, useEventCounts, useResolveEvent } from '@/hooks/useApi';
import { AlertTriangle, AlertCircle, Info, CheckCircle, RefreshCw, Trash2, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import type { Event } from '@/types';

const Events = () => {
  const [severityFilter, setSeverityFilter] = useState<string | undefined>();
  const [unresolvedOnly, setUnresolvedOnly] = useState(false);
  
  const { data: events, isLoading, error, refetch } = useEvents(severityFilter, unresolvedOnly);
  const { data: counts } = useEventCounts();
  const resolveEvent = useResolveEvent();

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
      default:
        return <Info className="h-5 w-5 text-blue-500" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      case 'warning':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      default:
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
    }
  };

  const handleResolve = async (eventId: number) => {
    await resolveEvent.mutateAsync(eventId);
    refetch();
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Events & Alerts</h1>
          <p className="text-muted-foreground">System events, alerts, and threshold violations</p>
        </div>
        <Button variant="outline" size="sm" onClick={() => refetch()}>
          <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Summary Cards */}
      {counts && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Total Events</CardDescription>
              <CardTitle className="text-2xl">{counts.total}</CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Unresolved</CardDescription>
              <CardTitle className="text-2xl text-orange-500">{counts.unresolved}</CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Critical</CardDescription>
              <CardTitle className="text-2xl text-red-500">{counts.by_severity?.critical || 0}</CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Warnings</CardDescription>
              <CardTitle className="text-2xl text-yellow-500">{counts.by_severity?.warning || 0}</CardTitle>
            </CardHeader>
          </Card>
        </div>
      )}

      {/* Filters */}
      <div className="flex gap-2">
        <Button
          variant={!severityFilter ? "default" : "outline"}
          size="sm"
          onClick={() => setSeverityFilter(undefined)}
        >
          All
        </Button>
        <Button
          variant={severityFilter === "critical" ? "destructive" : "outline"}
          size="sm"
          onClick={() => setSeverityFilter("critical")}
        >
          Critical
        </Button>
        <Button
          variant={severityFilter === "warning" ? "default" : "outline"}
          size="sm"
          onClick={() => setSeverityFilter("warning")}
        >
          Warning
        </Button>
        <Button
          variant={severityFilter === "info" ? "default" : "outline"}
          size="sm"
          onClick={() => setSeverityFilter("info")}
        >
          Info
        </Button>
        <div className="flex-1" />
        <Button
          variant={unresolvedOnly ? "default" : "outline"}
          size="sm"
          onClick={() => setUnresolvedOnly(!unresolvedOnly)}
        >
          Unresolved Only
        </Button>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>Failed to load events</AlertDescription>
        </Alert>
      )}

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2 text-muted-foreground">Loading...</span>
        </div>
      ) : events && events.length > 0 ? (
        <div className="space-y-2">
          {events.map((event) => (
            <Card key={event.id} className={event.is_resolved ? "opacity-60" : ""}>
              <CardContent className="py-4">
                <div className="flex items-start gap-4">
                  {getSeverityIcon(event.severity)}
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold">{event.event_type}</span>
                      <Badge className={getSeverityColor(event.severity)}>
                        {event.severity}
                      </Badge>
                      {event.is_resolved && (
                        <Badge variant="outline" className="bg-green-50">
                          <CheckCircle className="h-3 w-3 mr-1" />
                          Resolved
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm mt-1">{event.message}</p>
                    <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                      <span>Source: {event.source || 'system'}</span>
                      <span>{formatTimestamp(event.created_at)}</span>
                    </div>
                  </div>
                  {!event.is_resolved && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleResolve(event.id)}
                      disabled={resolveEvent.isPending}
                    >
                      Resolve
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 text-muted-foreground">
          <Info className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <p>No events to display</p>
        </div>
      )}
    </div>
  );
};

export default Events;