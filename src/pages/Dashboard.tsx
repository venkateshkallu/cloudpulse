import { MetricCard } from "@/components/MetricCard";
import { mockMetrics } from "@/lib/mockData";
import { Activity } from "lucide-react";

const Dashboard = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Activity className="h-8 w-8 text-primary" />
        <div>
          <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
          <p className="text-muted-foreground">Real-time system metrics and health status</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
        {mockMetrics.map((metric) => (
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
