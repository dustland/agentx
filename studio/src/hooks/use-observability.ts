'use client'

import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'

export function useObservability() {
  const { data: metrics, isLoading: metricsLoading } = useQuery({
    queryKey: ['metrics'],
    queryFn: api.getMetrics,
    refetchInterval: 30000, // Refresh every 30 seconds
  })

  const { data: agentPerformance } = useQuery({
    queryKey: ['agent-performance'],
    queryFn: api.getAgentPerformance,
    refetchInterval: 30000,
  })

  const { data: systemHealth } = useQuery({
    queryKey: ['system-health'],
    queryFn: api.getSystemHealth,
    refetchInterval: 10000, // Refresh every 10 seconds
  })

  return {
    metrics,
    agentPerformance,
    systemHealth,
    isLoading: metricsLoading,
  }
}