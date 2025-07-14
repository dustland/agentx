'use client'

import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { FileText, Download, ExternalLink } from 'lucide-react'
import { useArtifacts } from '@/lib/hooks/use-artifacts'
import { formatBytes } from '@/lib/utils'

interface TaskArtifactsProps {
  taskId: string
}

export function TaskArtifacts({ taskId }: TaskArtifactsProps) {
  const { artifacts, isLoading, downloadArtifact } = useArtifacts(taskId)

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (!artifacts || artifacts.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-96 text-center">
        <FileText className="h-12 w-12 text-muted-foreground mb-4" />
        <p className="text-muted-foreground">No artifacts generated yet</p>
      </div>
    )
  }

  return (
    <ScrollArea className="h-[600px]">
      <div className="space-y-4">
        {artifacts.map((artifact: any) => (
          <Card key={artifact.name} className="p-4">
            <div className="flex items-start justify-between">
              <div className="flex-1 space-y-1">
                <div className="flex items-center gap-2">
                  <FileText className="h-4 w-4 text-muted-foreground" />
                  <h4 className="text-sm font-medium">{artifact.name}</h4>
                </div>
                
                <div className="flex items-center gap-4 text-xs text-muted-foreground">
                  <span>{formatBytes(artifact.size)}</span>
                  <span>•</span>
                  <span>{new Date(artifact.created_at).toLocaleString()}</span>
                </div>
                
                <Badge variant="outline" className="text-xs">
                  {artifact.content_type}
                </Badge>
              </div>
              
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => window.open(artifact.url, '_blank')}
                >
                  <ExternalLink className="h-3 w-3 mr-1" />
                  View
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => downloadArtifact(artifact.name)}
                >
                  <Download className="h-3 w-3 mr-1" />
                  Download
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </ScrollArea>
  )
}