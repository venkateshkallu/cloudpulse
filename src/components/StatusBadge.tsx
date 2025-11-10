import { cn } from "@/lib/utils";

interface StatusBadgeProps {
  status: "healthy" | "warning" | "critical" | "online" | "degraded" | "offline" | "info" | "error";
  className?: string;
}

const statusConfig = {
  healthy: {
    label: "Healthy",
    className: "bg-success text-success-foreground",
  },
  warning: {
    label: "Warning",
    className: "bg-warning text-warning-foreground",
  },
  critical: {
    label: "Critical",
    className: "bg-critical text-critical-foreground",
  },
  online: {
    label: "Online",
    className: "bg-success text-success-foreground",
  },
  degraded: {
    label: "Degraded",
    className: "bg-warning text-warning-foreground",
  },
  offline: {
    label: "Offline",
    className: "bg-critical text-critical-foreground",
  },
  info: {
    label: "Info",
    className: "bg-primary text-primary-foreground",
  },
  error: {
    label: "Error",
    className: "bg-critical text-critical-foreground",
  },
};

export const StatusBadge = ({ status, className }: StatusBadgeProps) => {
  const config = statusConfig[status];

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold transition-all",
        config.className,
        className
      )}
    >
      <span className="mr-1.5 h-1.5 w-1.5 rounded-full bg-current animate-pulse" />
      {config.label}
    </span>
  );
};
