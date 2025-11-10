import { Card, CardContent } from "@/components/ui/card";
import { StatusBadge } from "@/components/StatusBadge";
import { mockLogs } from "@/lib/mockData";
import { ScrollText } from "lucide-react";
import { formatDistanceToNow } from "date-fns";

const Logs = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <ScrollText className="h-8 w-8 text-primary" />
        <div>
          <h1 className="text-3xl font-bold text-foreground">System Logs</h1>
          <p className="text-muted-foreground">Recent activity and events from all services</p>
        </div>
      </div>

      <div className="space-y-3">
        {mockLogs.map((log) => (
          <Card key={log.id} className="hover:shadow-md transition-shadow duration-200">
            <CardContent className="p-4">
              <div className="flex items-start gap-4">
                <StatusBadge status={log.level} className="mt-1" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-foreground">{log.message}</p>
                  <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                    <span className="font-mono">{log.source}</span>
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
    </div>
  );
};

export default Logs;
