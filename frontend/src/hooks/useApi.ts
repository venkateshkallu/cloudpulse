import { useQuery, useMutation, useQueryClient, UseQueryOptions, UseMutationOptions } from '@tanstack/react-query';
import { apiClient, ApiError, NetworkError } from '../utils/api';
import { API_ENDPOINTS } from '../utils/constants';
import type { Metric, Service, LogEntry, SystemStatus, MetricsApiResponse } from '../types';
import { transformMetricsResponse } from '../types';

// Query Keys for React Query
export const QUERY_KEYS = {
  METRICS: ['metrics'] as const,
  SERVICES: ['services'] as const,
  LOGS: ['logs'] as const,
  STATUS: ['status'] as const,
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