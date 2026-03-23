import { useState } from 'react';
import { useMonitoringTargetsWithResults, useCreateMonitoringTarget, useDeleteMonitoringTarget, useTriggerMonitoringCheck } from '@/hooks/useApi';
import { Activity, Plus, Trash2, RefreshCw, CheckCircle, XCircle, Loader2, ExternalLink } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import type { MonitoringTarget } from '@/types';

const Monitoring = () => {
  const [showAddForm, setShowAddForm] = useState(false);
  const [newTarget, setNewTarget] = useState({
    name: '',
    target_url: '',
    target_type: 'http' as const,
    check_interval: 60,
    timeout: 10,
    is_active: true,
  });

  const { data: targets, isLoading, error, refetch } = useMonitoringTargetsWithResults();
  const createTarget = useCreateMonitoringTarget();
  const deleteTarget = useDeleteMonitoringTarget();
  const triggerCheck = useTriggerMonitoringCheck();

  const handleCreateTarget = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createTarget.mutateAsync(newTarget);
      setShowAddForm(false);
      setNewTarget({
        name: '',
        target_url: '',
        target_type: 'http',
        check_interval: 60,
        timeout: 10,
        is_active: true,
      });
    } catch (err) {
      console.error('Failed to create target:', err);
    }
  };

  const handleDelete = async (id: number) => {
    if (confirm('Are you sure you want to delete this target?')) {
      await deleteTarget.mutateAsync(id);
    }
  };

  const handleCheck = async (id: number) => {
    await triggerCheck.mutateAsync(id);
    refetch();
  };

  const getStatusBadge = (isUp: boolean | undefined) => {
    if (isUp === undefined) {
      return <Badge variant="secondary">Unknown</Badge>;
    }
    return isUp ? (
      <Badge className="bg-green-500">Online</Badge>
    ) : (
      <Badge variant="destructive">Offline</Badge>
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Activity className="h-8 w-8 text-primary" />
          <div>
            <h1 className="text-3xl font-bold text-foreground">Endpoint Monitoring</h1>
            <p className="text-muted-foreground">Monitor external URLs, IPs, and services</p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => refetch()}>
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Button size="sm" onClick={() => setShowAddForm(!showAddForm)}>
            <Plus className="h-4 w-4 mr-2" />
            Add Target
          </Button>
        </div>
      </div>

      {showAddForm && (
        <Card>
          <CardHeader>
            <CardTitle>Add New Monitoring Target</CardTitle>
            <CardDescription>Configure an endpoint to monitor</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleCreateTarget} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="name">Name</Label>
                  <Input
                    id="name"
                    value={newTarget.name}
                    onChange={(e) => setNewTarget({ ...newTarget, name: e.target.value })}
                    placeholder="My API"
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="target_url">URL / IP Address</Label>
                  <Input
                    id="target_url"
                    value={newTarget.target_url}
                    onChange={(e) => setNewTarget({ ...newTarget, target_url: e.target.value })}
                    placeholder="https://api.example.com or 8.8.8.8"
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="target_type">Type</Label>
                  <Select
                    value={newTarget.target_type}
                    onValueChange={(value: 'http' | 'https' | 'ping' | 'dns') => 
                      setNewTarget({ ...newTarget, target_type: value })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="http">HTTP</SelectItem>
                      <SelectItem value="https">HTTPS</SelectItem>
                      <SelectItem value="ping">Ping</SelectItem>
                      <SelectItem value="dns">DNS</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="timeout">Timeout (seconds)</Label>
                  <Input
                    id="timeout"
                    type="number"
                    value={newTarget.timeout}
                    onChange={(e) => setNewTarget({ ...newTarget, timeout: parseInt(e.target.value) })}
                    min={1}
                    max={60}
                  />
                </div>
              </div>
              <div className="flex gap-2">
                <Button type="submit" disabled={createTarget.isPending}>
                  {createTarget.isPending ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : null}
                  Create Target
                </Button>
                <Button type="button" variant="outline" onClick={() => setShowAddForm(false)}>
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {error && (
        <Alert variant="destructive">
          <AlertDescription>Failed to load monitoring targets</AlertDescription>
        </Alert>
      )}

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2 text-muted-foreground">Loading...</span>
        </div>
      ) : targets && targets.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {targets.map((item) => (
            <Card key={item.target.id}>
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-lg">{item.target.name}</CardTitle>
                    <CardDescription className="flex items-center gap-1 mt-1">
                      <ExternalLink className="h-3 w-3" />
                      {item.target.target_url}
                    </CardDescription>
                  </div>
                  {getStatusBadge(item.latest_result?.is_up)}
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Type</span>
                    <span className="font-medium uppercase">{item.target.target_type}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Response Time</span>
                    <span className="font-medium">
                      {item.latest_result?.response_time_ms 
                        ? `${item.latest_result.response_time_ms}ms` 
                        : '-'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Status Code</span>
                    <span className="font-medium">
                      {item.latest_result?.status_code || '-'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Uptime (24h)</span>
                    <span className="font-medium">
                      {item.uptime_percentage !== null 
                        ? `${item.uptime_percentage}%` 
                        : '-'}
                    </span>
                  </div>
                  {item.latest_result?.error_message && (
                    <div className="mt-2 p-2 bg-red-50 dark:bg-red-900/20 rounded text-xs text-red-600 dark:text-red-400">
                      {item.latest_result.error_message}
                    </div>
                  )}
                </div>
                <div className="flex gap-2 mt-4">
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={() => handleCheck(item.target.id)}
                    disabled={triggerCheck.isPending}
                  >
                    <RefreshCw className={`h-3 w-3 mr-1 ${triggerCheck.isPending ? 'animate-spin' : ''}`} />
                    Check
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={() => handleDelete(item.target.id)}
                    disabled={deleteTarget.isPending}
                    className="text-red-500 hover:text-red-700"
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 text-muted-foreground">
          <Activity className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <p>No monitoring targets configured</p>
          <p className="text-sm">Click "Add Target" to start monitoring external endpoints</p>
        </div>
      )}
    </div>
  );
};

export default Monitoring;