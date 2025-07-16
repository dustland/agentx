'use client'

import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api, Message } from '@/lib/api'

export function useMessages(taskId: string) {
  const [messages, setMessages] = useState<Message[]>([])

  const { data: initialMessages, isLoading } = useQuery({
    queryKey: ['messages', taskId],
    queryFn: () => api.getMessages(taskId),
  })

  useEffect(() => {
    if (initialMessages) {
      setMessages(initialMessages)
    }
  }, [initialMessages])

  useEffect(() => {
    // Set up SSE for real-time messages
    const cleanup = api.streamMessages(taskId, (message) => {
      setMessages((prev) => [...prev, message])
    })

    return () => {
      if (cleanup && typeof cleanup === 'function') {
        cleanup()
      }
    }
  }, [taskId])

  return { messages, isLoading }
}