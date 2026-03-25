import { useAgents, useAgentLatestMetrics } from '@/hooks/useApi';
import { Server, RefreshCw, Loader2, Activity, Monitor, CheckCircle, XCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';

const Agents = () => {
  const { data: agents, isLoading, error, refetch } = useAgents();

  const getStatusBadge = (status: string) => {
    return status === 'online' ? (
      <Badge className="bg-green-500"><CheckCircle className="h-3 w-3 mr-1" /> Online</Badge>
    ) : (
      <Badge variant="destructive"><XCircle className="h-3 w-3 mr-1" /> Offline</Badge>
    );
  };

  const formatTime = (timestamp: string | null) => {
    if (!timestamp) return 'Never';
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  if (error) {
    return (
      <div className="space-y-6">
        <Alert variant="destructive">
          <AlertDescription>Failed to load agents</AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Server className="h-8 w-8 text-primary" />
          <div>
            <h1 className="text-3xl font-bold text-foreground">Remote Agents</h1>
            <p className="text-muted-foreground">Monitor multiple machines from one dashboard</p>
          </div>
        </div>
        <Button variant="outline" size="sm" onClick={() => refetch()}>
          <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      <div className="bg-card border border-border rounded-lg p-4">
        <h3 className="font-semibold mb-2">How to add an agent</h3>
        <p className="text-sm text-muted-foreground mb-4">
          Run the CloudPulse agent on any machine you want to monitor:
        </p>
        <pre className="bg-muted p-3 rounded text-sm overflow-x-auto">
{`# Install dependencies
pip install -r agent/requirements.txt

# Run the agent
python agent/agent.py --api-url http://YOUR_SERVER:8000`}
        </pre>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2 text-muted-foreground">Loading...</span>
        </div>
      ) : agents && agents.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {agents.map((agent) => (
            <AgentCard key={agent.id} agent={agent} />
          ))}
        </div>
      ) : (
        <div className="text-center py-12 text-muted-foreground">
          <Monitor className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <p>No agents registered</p>
          <p className="text-sm">Run the agent on a remote machine to start monitoring</p>
        </div>
      )}
    </div>
  );
};

const AgentCard = ({ agent }: { agent: any }) => {
  const { data: latest } = useAgentLatestMetrics(agent.id, { enabled: agent.status === 'online' });

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="text-lg">{agent.name}</CardTitle>
            <CardDescription className="flex items-center gap-1">
              <Activity className="h-3 w-3" />
              {agent.hostname || 'Unknown'}
            </CardDescription>
          </div>
          {agent.status === 'online' ? (
            <Badge className="bg-green-500">Online</Badge>
          ) : (
            <Badge variant="destructive">Offline</Badge>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-muted-foreground">IP Address</span>
            <span className="font-medium">{agent.ip_address || '-'}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">OS</span>
            <span className="font-medium uppercase">{agent.os_type || '-'}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Last Heartbeat</span>
            <span className="font-medium">{formatTime(agent.last_heartbeat)}</span>
          </div>
        </div>
        
        {latest?.metrics && (
          <div className="mt-4 pt-4 border-t">
            <div className="grid grid-cols-3 gap-2 text-sm">
              <div>
                <div className="text-muted-foreground text-xs">CPU</div>
                <div className="font-medium">{latest.metrics.cpu_percent?.toFixed(1)}%</div>
              </div>
              <div>
                <div className="text-muted-foreground text-xs">Memory</div>
                <div className="font-medium">{latest.metrics.memory_percent?.toFixed(1)}%</div>
              </div>
              <div>
                <div className="text-muted-foreground text-xs">Disk</div>
                <div className="font-medium">{latest.metrics.disk_percent?.toFixed(1)}%</div>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default Agents;