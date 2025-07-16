'use client'

import { useQuery } from '@tanstack/react-query'
import { api, Artifact } from '@/lib/api'
import { useToast } from './use-toast'

export function useArtifacts(taskId: string) {
  const { toast } = useToast()

  const { data: artifacts, isLoading } = useQuery({
    queryKey: ['artifacts', taskId],
    queryFn: () => api.getArtifacts(taskId),
    refetchInterval: 5000, // Refetch every 5 seconds
  })

  const downloadArtifact = async (artifactName: string) => {
    try {
      const blob = await api.downloadArtifact(taskId, artifactName)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = artifactName
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      
      toast({
        title: 'Download started',
        description: `Downloading ${artifactName}`,
      })
    } catch (error) {
      toast({
        title: 'Download failed',
        description: 'Failed to download artifact',
        variant: 'destructive',
      })
    }
  }

  return { artifacts, isLoading, downloadArtifact }
}