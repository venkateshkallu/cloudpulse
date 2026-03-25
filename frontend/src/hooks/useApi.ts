import { useQuery, useMutation, useQueryClient, UseQueryOptions, UseMutationOptions } from '@tanstack/react-query';
import { apiClient, ApiError, NetworkError } from '../utils/api';
import { API_ENDPOINTS } from '../utils/constants';
import type { Metric, Service, LogEntry, SystemStatus, MetricsApiResponse, MonitoringTarget, MonitoringResult, TargetWithLatestResult, Event, RealTimeSystemMetrics, SystemMetricsSnapshot, DetailedHealth, MetricsAggregates } from '../types';
import { transformMetricsResponse } from '../types';

// Query Keys for React Query
export const QUERY_KEYS = {
  METRICS: ['metrics'] as const,
  SERVICES: ['services'] as const,
  LOGS: ['logs'] as const,
  STATUS: ['status'] as const,
  MONITORING_TARGETS: ['monitoring-targets'] as const,
  MONITORING_TARGETS_WITH_RESULTS: ['monitoring-targets-with-results'] as const,
  MONITORING_RESULTS: ['monitoring-results'] as const,
  EVENTS: ['events'] as const,
  SYSTEM_METRICS: ['system-metrics'] as const,
  METRICS_SNAPSHOTS: ['metrics-snapshots'] as const,
  HEALTH: ['health'] as const,
  AGENTS: ['agents'] as const,
  AGENT_METRICS: ['agent-metrics'] as const,
  HEALTH_SCORE: ['health-score'] as const,
} as const;

// Default query options
const DEFAULT_QUERY_OPTIONS = {
  staleTime: 30 * 1000, // 30 seconds
  gcTime: 5 * 60 * 1000, // 5 minutes (formerly cacheTime)
  retry: (failureCount: number, error: any) => {
    // Don't retry on client errors (4xx)
    if (error instanceof ApiError && error.status >= 400 && error.status < 500) {
      return false;
    }
    // Retry up to 3 times for network errors and server errors
    return failureCount < 3;
  },
  retryDelay: (attemptIndex: number) => Math.min(1000 * 2 ** attemptIndex, 30000),
};

// Metrics API hooks
export function useMetrics(options?: Partial<UseQueryOptions<Metric[], ApiError | NetworkError>>) {
  return useQuery({
    queryKey: QUERY_KEYS.METRICS,
    queryFn: async () => {
      const response = await apiClient.get<MetricsApiResponse>(API_ENDPOINTS.METRICS);
      return transformMetricsResponse(response.data);
    },
    refetchInterval: 5000, // Refetch every 5 seconds for real-time data
    ...DEFAULT_QUERY_OPTIONS,
    ...options,
  });
}

// Services API hooks
export function useServices(options?: Partial<UseQueryOptions<Service[], ApiError | NetworkError>>) {
  return useQuery({
    queryKey: QUERY_KEYS.SERVICES,
    queryFn: async () => {
      const response = await apiClient.get<Service[]>(API_ENDPOINTS.SERVICES);
      return response.data;
    },
    refetchInterval: 10000, // Refetch every 10 seconds
    ...DEFAULT_QUERY_OPTIONS,
    ...options,
  });
}

// Logs API hooks with filtering support
interface LogsParams {
  limit?: number;
  level?: string;
  service?: string;
  offset?: number;
}

// Logs API response interface to match backend
interface LogsListResponse {
  logs: LogEntry[];
  total: number;
  limit: number;
  offset: number;
}

export function useLogs(
  params: LogsParams = {},
  options?: Partial<UseQueryOptions<LogEntry[], ApiError | NetworkError>>
) {
  const queryParams = new URLSearchParams();
  
  if (params.limit) queryParams.append('limit', params.limit.toString());
  if (params.level) queryParams.append('level', params.level);
  if (params.service) queryParams.append('service', params.service);
  if (params.offset) queryParams.append('offset', params.offset.toString());
  
  const queryString = queryParams.toString();
  const endpoint = queryString ? `${API_ENDPOINTS.LOGS}?${queryString}` : API_ENDPOINTS.LOGS;

  return useQuery({
    queryKey: [...QUERY_KEYS.LOGS, params],
    queryFn: async () => {
      const response = await apiClient.get<LogsListResponse>(endpoint);
      return response.data.logs; // Extract logs array from the response
    },
    refetchInterval: 15000, // Refetch every 15 seconds
    ...DEFAULT_QUERY_OPTIONS,
    ...options,
  });
}

// System Status API hooks
export function useSystemStatus(options?: Partial<UseQueryOptions<SystemStatus, ApiError | NetworkError>>) {
  return useQuery({
    queryKey: QUERY_KEYS.STATUS,
    queryFn: async () => {
      const response = await apiClient.get<SystemStatus>(API_ENDPOINTS.STATUS);
      return response.data;
    },
    refetchInterval: 30000, // Refetch every 30 seconds
    ...DEFAULT_QUERY_OPTIONS,
    ...options,
  });
}

// Mutation hooks for future use (when we add POST/PUT/DELETE operations)
export function useCreateLog(options?: UseMutationOptions<LogEntry, ApiError | NetworkError, Partial<LogEntry>>) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (logData: Partial<LogEntry>) => {
      const response = await apiClient.post<LogEntry>(API_ENDPOINTS.LOGS, logData);
      return response.data;
    },
    onSuccess: () => {
      // Invalidate and refetch logs after creating a new one
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.LOGS });
    },
    ...options,
  });
}

export function useUpdateService(options?: UseMutationOptions<Service, ApiError | NetworkError, { id: string; data: Partial<Service> }>) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<Service> }) => {
      const response = await apiClient.put<Service>(`${API_ENDPOINTS.SERVICES}/${id}`, data);
      return response.data;
    },
    onSuccess: () => {
      // Invalidate and refetch services after updating
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.SERVICES });
    },
    ...options,
  });
}

// Utility hooks for manual refetching and cache management
export function useRefreshData() {
  const queryClient = useQueryClient();
  
  const refreshMetrics = () => queryClient.invalidateQueries({ queryKey: QUERY_KEYS.METRICS });
  const refreshServices = () => queryClient.invalidateQueries({ queryKey: QUERY_KEYS.SERVICES });
  const refreshLogs = () => queryClient.invalidateQueries({ queryKey: QUERY_KEYS.LOGS });
  const refreshStatus = () => queryClient.invalidateQueries({ queryKey: QUERY_KEYS.STATUS });
  const refreshAll = () => queryClient.invalidateQueries();
  
  return {
    refreshMetrics,
    refreshServices,
    refreshLogs,
    refreshStatus,
    refreshAll,
  };
}

// Hook for checking connection status
export function useConnectionStatus() {
  const metricsQuery = useMetrics({ enabled: false });
  const statusQuery = useSystemStatus({ enabled: false });
  
  const checkConnection = async () => {
    try {
      await apiClient.get(API_ENDPOINTS.STATUS);
      return true;
    } catch (error) {
      return false;
    }
  };
  
  return {
    isConnected: !metricsQuery.isError && !statusQuery.isError,
    checkConnection,
    lastError: metricsQuery.error || statusQuery.error,
  };
}

// Monitoring Targets API hooks
export function useMonitoringTargets(options?: Partial<UseQueryOptions<MonitoringTarget[], ApiError | NetworkError>>) {
  return useQuery({
    queryKey: QUERY_KEYS.MONITORING_TARGETS,
    queryFn: async () => {
      const response = await apiClient.get<MonitoringTarget[]>(API_ENDPOINTS.MONITORING_TARGETS);
      return response.data;
    },
    refetchInterval: 30000,
    ...DEFAULT_QUERY_OPTIONS,
    ...options,
  });
}

export function useMonitoringTargetsWithResults(options?: Partial<UseQueryOptions<TargetWithLatestResult[], ApiError | NetworkError>>) {
  return useQuery({
    queryKey: QUERY_KEYS.MONITORING_TARGETS_WITH_RESULTS,
    queryFn: async () => {
      const response = await apiClient.get<TargetWithLatestResult[]>(API_ENDPOINTS.MONITORING_TARGETS_WITH_RESULTS);
      return response.data;
    },
    refetchInterval: 30000,
    ...DEFAULT_QUERY_OPTIONS,
    ...options,
  });
}

export function useMonitoringResults(
  targetId?: number,
  options?: Partial<UseQueryOptions<MonitoringResult[], ApiError | NetworkError>>
) {
  const endpoint = targetId 
    ? `${API_ENDPOINTS.MONITORING_RESULTS}?target_id=${targetId}`
    : API_ENDPOINTS.MONITORING_RESULTS;
  
  return useQuery({
    queryKey: [...QUERY_KEYS.MONITORING_RESULTS, targetId],
    queryFn: async () => {
      const response = await apiClient.get<{ results: MonitoringResult[]; total: number }>(endpoint);
      return response.data.results;
    },
    refetchInterval: 30000,
    ...DEFAULT_QUERY_OPTIONS,
    ...options,
  });
}

export function useCreateMonitoringTarget(options?: UseMutationOptions<MonitoringTarget, ApiError | NetworkError, Omit<MonitoringTarget, 'id' | 'created_at' | 'updated_at'>>) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (targetData: Omit<MonitoringTarget, 'id' | 'created_at' | 'updated_at'>) => {
      const response = await apiClient.post<MonitoringTarget>(API_ENDPOINTS.MONITORING_TARGETS, targetData);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.MONITORING_TARGETS });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.MONITORING_TARGETS_WITH_RESULTS });
    },
    ...options,
  });
}

export function useDeleteMonitoringTarget(options?: UseMutationOptions<void, ApiError | NetworkError, number>) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (targetId: number) => {
      await apiClient.delete(`${API_ENDPOINTS.MONITORING_TARGETS}/${targetId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.MONITORING_TARGETS });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.MONITORING_TARGETS_WITH_RESULTS });
    },
    ...options,
  });
}

export function useTriggerMonitoringCheck(options?: UseMutationOptions<MonitoringResult, ApiError | NetworkError, number>) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (targetId: number) => {
      const response = await apiClient.post<MonitoringResult>(`${API_ENDPOINTS.MONITORING_TARGETS}/${targetId}/check`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.MONITORING_RESULTS });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.MONITORING_TARGETS_WITH_RESULTS });
    },
    ...options,
  });
}
// Events API hooks
export function useEvents(
  severity?: string,
  unresolvedOnly: boolean = false,
  options?: Partial<UseQueryOptions<Event[], ApiError | NetworkError>>
) {
  const queryParams = new URLSearchParams();
  if (severity) queryParams.append('severity', severity);
  if (unresolvedOnly) queryParams.append('unresolved_only', 'true');
  
  const endpoint = queryParams.toString() 
    ? `${API_ENDPOINTS.EVENTS}?${queryParams.toString()}`
    : API_ENDPOINTS.EVENTS;
  
  return useQuery({
    queryKey: [...QUERY_KEYS.EVENTS, severity, unresolvedOnly],
    queryFn: async () => {
      const response = await apiClient.get<{ events: Event[]; total: number }>(endpoint);
      return response.data.events;
    },
    refetchInterval: 10000,
    ...DEFAULT_QUERY_OPTIONS,
    ...options,
  });
}

export function useRecentEvents(
  hours: number = 24,
  options?: Partial<UseQueryOptions<Event[], ApiError | NetworkError>>
) {
  return useQuery({
    queryKey: [...QUERY_KEYS.EVENTS, 'recent', hours],
    queryFn: async () => {
      const response = await apiClient.get<{ events: Event[]; total: number }>(
        `${API_ENDPOINTS.EVENTS}/recent?hours=${hours}`
      );
      return response.data.events;
    },
    refetchInterval: 10000,
    ...DEFAULT_QUERY_OPTIONS,
    ...options,
  });
}

export function useEventCounts(options?: Partial<UseQueryOptions<any, ApiError | NetworkError>>) {
  return useQuery({
    queryKey: [...QUERY_KEYS.EVENTS, 'counts'],
    queryFn: async () => {
      const response = await apiClient.get(`${API_ENDPOINTS.EVENTS}/counts`);
      return response.data;
    },
    refetchInterval: 30000,
    ...DEFAULT_QUERY_OPTIONS,
    ...options,
  });
}

export function useResolveEvent(options?: UseMutationOptions<void, ApiError | NetworkError, number>) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (eventId: number) => {
      await apiClient.post(`${API_ENDPOINTS.EVENTS}/${eventId}/resolve`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.EVENTS });
    },
    ...options,
  });
}

// Real-time system metrics hooks
export function useSystemMetrics(options?: Partial<UseQueryOptions<RealTimeSystemMetrics, ApiError | NetworkError>>) {
  return useQuery({
    queryKey: QUERY_KEYS.SYSTEM_METRICS,
    queryFn: async () => {
      const response = await apiClient.get<RealTimeSystemMetrics>(`${API_ENDPOINTS.METRICS}/system`);
      return response.data;
    },
    refetchInterval: 5000, // Refresh every 5 seconds
    ...DEFAULT_QUERY_OPTIONS,
    ...options,
  });
}

export function useMetricsSnapshots(
  limit: number = 100,
  options?: Partial<UseQueryOptions<SystemMetricsSnapshot[], ApiError | NetworkError>>
) {
  return useQuery({
    queryKey: [...QUERY_KEYS.METRICS_SNAPSHOTS, limit],
    queryFn: async () => {
      const response = await apiClient.get<{ snapshots: SystemMetricsSnapshot[]; total: number }>(
        `${API_ENDPOINTS.METRICS}/snapshots?limit=${limit}`
      );
      return response.data.snapshots;
    },
    refetchInterval: 30000,
    ...DEFAULT_QUERY_OPTIONS,
    ...options,
  });
}

export function useMetricsAggregates(
  hours: number = 24,
  options?: Partial<UseQueryOptions<MetricsAggregates, ApiError | NetworkError>>
) {
  return useQuery({
    queryKey: [...QUERY_KEYS.METRICS, 'aggregates', hours],
    queryFn: async () => {
      const response = await apiClient.get<MetricsAggregates>(
        `${API_ENDPOINTS.METRICS}/aggregates?hours=${hours}`
      );
      return response.data;
    },
    refetchInterval: 60000,
    ...DEFAULT_QUERY_OPTIONS,
    ...options,
  });
}

// Health check hooks
export function useHealth(options?: Partial<UseQueryOptions<DetailedHealth, ApiError | NetworkError>>) {
  return useQuery({
    queryKey: QUERY_KEYS.HEALTH,
    queryFn: async () => {
      const response = await apiClient.get<DetailedHealth>(`${API_ENDPOINTS.STATUS}/health`);
      return response.data;
    },
    refetchInterval: 10000,
    ...DEFAULT_QUERY_OPTIONS,
    ...options,
  });
}
// Agent API hooks
export function useAgents(options?: Partial<UseQueryOptions<Agent[], ApiError | NetworkError>>) {
  return useQuery({
    queryKey: QUERY_KEYS.AGENTS,
    queryFn: async () => {
      const response = await apiClient.get<{ agents: Agent[]; total: number }>(API_ENDPOINTS.AGENTS);
      return response.data.agents;
    },
    refetchInterval: 30000,
    ...DEFAULT_QUERY_OPTIONS,
    ...options,
  });
}

export function useAgentMetrics(
  agentId: number,
  limit: number = 100,
  options?: Partial<UseQueryOptions<AgentMetrics[], ApiError | NetworkError>>
) {
  return useQuery({
    queryKey: [...QUERY_KEYS.AGENT_METRICS, agentId, limit],
    queryFn: async () => {
      const response = await apiClient.get<{ metrics: AgentMetrics[]; total: number }>(
        `${API_ENDPOINTS.AGENTS}/${agentId}/metrics?limit=${limit}`
      );
      return response.data.metrics;
    },
    refetchInterval: 30000,
    ...DEFAULT_QUERY_OPTIONS,
    ...options,
  });
}

export function useAgentLatestMetrics(
  agentId: number,
  options?: Partial<UseQueryOptions<any, ApiError | NetworkError>>
) {
  return useQuery({
    queryKey: [...QUERY_KEYS.AGENT_METRICS, agentId, 'latest'],
    queryFn: async () => {
      const response = await apiClient.get(`${API_ENDPOINTS.AGENTS}/${agentId}/latest`);
      return response.data;
    },
    refetchInterval: 15000,
    ...DEFAULT_QUERY_OPTIONS,
    ...options,
  });
}

export function useHealthScore(options?: Partial<UseQueryOptions<HealthScore, ApiError | NetworkError>>) {
  return useQuery({
    queryKey: QUERY_KEYS.HEALTH_SCORE,
    queryFn: async () => {
      const response = await apiClient.get<HealthScore>(`${API_ENDPOINTS.STATUS}/health-score`);
      return response.data;
    },
    refetchInterval: 30000,
    ...DEFAULT_QUERY_OPTIONS,
    ...options,
  });
}