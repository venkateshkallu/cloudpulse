import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Info, Activity, Shield, Zap } from "lucide-react";

const About = () => {
  const features = [
    {
      icon: Activity,
      title: "Real-time Monitoring",
      description: "Track your cloud infrastructure with live metrics and instant updates.",
    },
    {
      icon: Shield,
      title: "Reliable & Secure",
      description: "Enterprise-grade security with end-to-end encryption and compliance.",
    },
    {
      icon: Zap,
      title: "Performance Optimized",
      description: "Lightning-fast dashboard with minimal resource overhead.",
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Info className="h-8 w-8 text-primary" />
        <div>
          <h1 className="text-3xl font-bold text-foreground">About CloudPulse</h1>
          <p className="text-muted-foreground">Professional cloud monitoring solution</p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>What is CloudPulse Monitor?</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4 text-muted-foreground">
          <p>
            CloudPulse Monitor is a modern, real-time cloud monitoring dashboard designed to help
            you track system health, service status, and performance metrics across your entire
            infrastructure.
          </p>
          <p>
            Built with cutting-edge web technologies, CloudPulse provides an intuitive interface
            for monitoring your cloud services, analyzing logs, and maintaining optimal system
            performance.
          </p>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {features.map((feature) => (
          <Card key={feature.title} className="hover:shadow-lg transition-shadow duration-300">
            <CardHeader>
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                  <feature.icon className="h-5 w-5 text-primary" />
                </div>
                <CardTitle className="text-lg">{feature.title}</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">{feature.description}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Technology Stack</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div className="p-4 bg-muted rounded-lg">
              <p className="font-semibold text-foreground">React</p>
              <p className="text-xs text-muted-foreground">Frontend Framework</p>
            </div>
            <div className="p-4 bg-muted rounded-lg">
              <p className="font-semibold text-foreground">Vite</p>
              <p className="text-xs text-muted-foreground">Build Tool</p>
            </div>
            <div className="p-4 bg-muted rounded-lg">
              <p className="font-semibold text-foreground">TailwindCSS</p>
              <p className="text-xs text-muted-foreground">Styling</p>
            </div>
            <div className="p-4 bg-muted rounded-lg">
              <p className="font-semibold text-foreground">TypeScript</p>
              <p className="text-xs text-muted-foreground">Type Safety</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Version Information</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-muted-foreground">Version:</span>
            <span className="font-medium text-foreground">1.0.0</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Build:</span>
            <span className="font-medium text-foreground">2024.01</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">License:</span>
            <span className="font-medium text-foreground">MIT</span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default About;
