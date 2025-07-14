import { useState, useEffect } from 'react'

export function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(false)

  useEffect(() => {
    const mediaQuery = window.matchMedia(query)
    const handleChange = () => setMatches(mediaQuery.matches)
    
    // Set initial value
    handleChange()
    
    // Listen for changes
    mediaQuery.addEventListener('change', handleChange)
    
    // Cleanup
    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [query])

  return matches
}