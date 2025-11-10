import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Settings as SettingsIcon } from "lucide-react";
import { useState } from "react";
import { useToast } from "@/hooks/use-toast";

const Settings = () => {
  const { toast } = useToast();
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshRate, setRefreshRate] = useState("30");
  const [darkMode, setDarkMode] = useState(false);

  const handleRefreshRateChange = (value: string) => {
    setRefreshRate(value);
    toast({
      title: "Settings Updated",
      description: `Refresh rate set to ${value} seconds`,
    });
  };

  const handleAutoRefreshToggle = (checked: boolean) => {
    setAutoRefresh(checked);
    toast({
      title: "Settings Updated",
      description: checked ? "Auto-refresh enabled" : "Auto-refresh disabled",
    });
  };

  const handleDarkModeToggle = (checked: boolean) => {
    setDarkMode(checked);
    document.documentElement.classList.toggle("dark", checked);
    toast({
      title: "Theme Updated",
      description: checked ? "Dark mode enabled" : "Light mode enabled",
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <SettingsIcon className="h-8 w-8 text-primary" />
        <div>
          <h1 className="text-3xl font-bold text-foreground">Settings</h1>
          <p className="text-muted-foreground">Configure your monitoring preferences</p>
        </div>
      </div>

      <div className="grid gap-6 max-w-2xl">
        <Card>
          <CardHeader>
            <CardTitle>Display Settings</CardTitle>
            <CardDescription>Customize how you view your monitoring data</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label htmlFor="dark-mode">Dark Mode</Label>
                <div className="text-sm text-muted-foreground">
                  Toggle between light and dark themes
                </div>
              </div>
              <Switch
                id="dark-mode"
                checked={darkMode}
                onCheckedChange={handleDarkModeToggle}
              />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Refresh Settings</CardTitle>
            <CardDescription>Control how frequently data is updated</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label htmlFor="auto-refresh">Auto Refresh</Label>
                <div className="text-sm text-muted-foreground">
                  Automatically update metrics
                </div>
              </div>
              <Switch
                id="auto-refresh"
                checked={autoRefresh}
                onCheckedChange={handleAutoRefreshToggle}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="refresh-rate">Refresh Rate</Label>
              <Select value={refreshRate} onValueChange={handleRefreshRateChange}>
                <SelectTrigger id="refresh-rate">
                  <SelectValue placeholder="Select refresh rate" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="10">10 seconds</SelectItem>
                  <SelectItem value="30">30 seconds</SelectItem>
                  <SelectItem value="60">1 minute</SelectItem>
                  <SelectItem value="300">5 minutes</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Settings;
