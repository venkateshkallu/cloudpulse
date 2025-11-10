import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { StatusBadge } from "./StatusBadge";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { cn } from "@/lib/utils";

interface MetricCardProps {
  name: string;
  value: number;
  unit: string;
  status: "healthy" | "warning" | "critical";
  trend: "up" | "down" | "stable";
}

export const MetricCard = ({ name, value, unit, status, trend }: MetricCardProps) => {
  const TrendIcon = trend === "up" ? TrendingUp : trend === "down" ? TrendingDown : Minus;

  return (
    <Card className="hover:shadow-lg transition-shadow duration-300">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">{name}</CardTitle>
        <StatusBadge status={status} />
      </CardHeader>
      <CardContent>
        <div className="flex items-end justify-between">
          <div>
            <div className="text-3xl font-bold text-foreground">
              {value}
              <span className="text-lg text-muted-foreground ml-1">{unit}</span>
            </div>
          </div>
          <div
            className={cn(
              "flex items-center gap-1 text-sm font-medium",
              trend === "up" && "text-primary",
              trend === "down" && "text-muted-foreground",
              trend === "stable" && "text-muted-foreground"
            )}
          >
            <TrendIcon className="h-4 w-4" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
