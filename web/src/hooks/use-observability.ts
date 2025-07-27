"use client";

import { useQuery } from "@tanstack/react-query";
import { useApi } from "@/lib/api-client";

export function useObservability() {
  const api = useApi();

  const {
    data: systemHealth,
    isLoading,
    refetch,
  } = useQuery({
    queryKey: ["system-health"],
    queryFn: () => api.getSystemHealth(),
    refetchInterval: 10000, // Refresh every 10 seconds
  });

  return {
    systemHealth,
    isLoading,
    refetch,
  };
}
