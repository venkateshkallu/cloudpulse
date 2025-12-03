import { createRoot } from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import App from "@/App.tsx";
import "@/index.css";

// Ensure the correct title is set and maintained
document.title = "CloudPulse Monitor";

// Override any attempts to change the title
const originalTitleSetter = Object.getOwnPropertyDescriptor(Document.prototype, 'title')?.set;
if (originalTitleSetter) {
  Object.defineProperty(document, 'title', {
    set: function(newTitle: string) {
      // Only allow our title or similar variations
      if (newTitle.includes('CloudPulse') || newTitle === 'CloudPulse Monitor') {
        originalTitleSetter.call(this, newTitle);
      } else {
        originalTitleSetter.call(this, 'CloudPulse Monitor');
      }
    },
    get: function() {
      return 'CloudPulse Monitor';
    },
    configurable: true
  });
}

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30 * 1000, // 30 seconds
      gcTime: 5 * 60 * 1000, // 5 minutes
      retry: (failureCount, error) => {
        // Don't retry on 4xx errors
        if (error && typeof error === 'object' && 'status' in error) {
          const status = error.status as number;
          if (status >= 400 && status < 500) {
            return false;
          }
        }
        return failureCount < 3;
      },
    },
  },
});

createRoot(document.getElementById("root")!).render(
  <QueryClientProvider client={queryClient}>
    <App />
  </QueryClientProvider>
);
