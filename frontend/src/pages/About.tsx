import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Info, Activity, Shield, Zap, Github, ExternalLink } from "lucide-react";
import { Button } from "@/components/ui/button";

const About = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Info className="h-8 w-8 text-primary" />
        <div>
          <h1 className="text-3xl font-bold text-foreground">About CloudPulse Monitor</h1>
          <p className="text-muted-foreground">System monitoring and observability platform</p>
        </div>
      </div>

      <div className="grid gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              Application Information
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 className="font-semibold text-sm text-muted-foreground">Version</h4>
                <p className="text-lg">1.0.0</p>
              </div>
              <div>
                <h4 className="font-semibold text-sm text-muted-foreground">Build</h4>
                <p className="text-lg">Production</p>
              </div>
              <div>
                <h4 className="font-semibold text-sm text-muted-foreground">Last Updated</h4>
                <p className="text-lg">{new Date().toLocaleDateString()}</p>
              </div>
              <div>
                <h4 className="font-semibold text-sm text-muted-foreground">Status</h4>
                <Badge variant="default" className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                  Operational
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Zap className="h-5 w-5" />
              Features
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <h4 className="font-semibold">Real-time Monitoring</h4>
                <p className="text-sm text-muted-foreground">
                  Monitor system metrics, services, and logs in real-time
                </p>
              </div>
              <div className="space-y-2">
                <h4 className="font-semibold">Service Health Tracking</h4>
                <p className="text-sm text-muted-foreground">
                  Track the health and uptime of all your services
                </p>
              </div>
              <div className="space-y-2">
                <h4 className="font-semibold">Log Aggregation</h4>
                <p className="text-sm text-muted-foreground">
                  Centralized logging with filtering and search capabilities
                </p>
              </div>
              <div className="space-y-2">
                <h4 className="font-semibold">Performance Metrics</h4>
                <p className="text-sm text-muted-foreground">
                  CPU, memory, network, and custom application metrics
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5" />
              Technology Stack
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <h4 className="font-semibold mb-2">Frontend</h4>
                <div className="space-y-1 text-sm text-muted-foreground">
                  <p>React 18</p>
                  <p>TypeScript</p>
                  <p>Tailwind CSS</p>
                  <p>Vite</p>
                  <p>React Query</p>
                </div>
              </div>
              <div>
                <h4 className="font-semibold mb-2">Backend</h4>
                <div className="space-y-1 text-sm text-muted-foreground">
                  <p>FastAPI</p>
                  <p>Python 3.11</p>
                  <p>SQLAlchemy</p>
                  <p>PostgreSQL</p>
                  <p>Alembic</p>
                </div>
              </div>
              <div>
                <h4 className="font-semibold mb-2">Infrastructure</h4>
                <div className="space-y-1 text-sm text-muted-foreground">
                  <p>Docker</p>
                  <p>Docker Compose</p>
                  <p>Nginx</p>
                  <p>AWS ECS Ready</p>
                  <p>Health Checks</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Resources</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-wrap gap-2">
              <Button variant="outline" size="sm" asChild>
                <a href="#" target="_blank" rel="noopener noreferrer">
                  <Github className="h-4 w-4 mr-2" />
                  Source Code
                </a>
              </Button>
              <Button variant="outline" size="sm" asChild>
                <a href="#" target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="h-4 w-4 mr-2" />
                  Documentation
                </a>
              </Button>
              <Button variant="outline" size="sm" asChild>
                <a href="/api/docs" target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="h-4 w-4 mr-2" />
                  API Docs
                </a>
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>License & Credits</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <p className="text-sm text-muted-foreground">
              CloudPulse Monitor is built with modern web technologies and follows best practices 
              for monitoring and observability.
            </p>
            <p className="text-sm text-muted-foreground">
              © 2024 CloudPulse Monitor. All rights reserved.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default About;