import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { StatusBadge } from "@/components/StatusBadge";
import { mockServices } from "@/lib/mockData";
import { Server } from "lucide-react";
import { formatDistanceToNow } from "date-fns";

const Services = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Server className="h-8 w-8 text-primary" />
        <div>
          <h1 className="text-3xl font-bold text-foreground">Services</h1>
          <p className="text-muted-foreground">Monitor all cloud services and their status</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {mockServices.map((service) => (
          <Card key={service.id} className="hover:shadow-lg transition-shadow duration-300">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">{service.name}</CardTitle>
                <StatusBadge status={service.status} />
              </div>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Uptime</span>
                <span className="text-sm font-semibold text-foreground">{service.uptime}%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Last Checked</span>
                <span className="text-sm font-medium text-foreground">
                  {formatDistanceToNow(new Date(service.lastChecked), { addSuffix: true })}
                </span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default Services;
