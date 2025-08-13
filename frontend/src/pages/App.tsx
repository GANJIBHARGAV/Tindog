
import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'

function useHealth() {
  return useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const { data } = await api.get('/api/health')
      return data
    },
  })
}

export default function App() {
  const { data } = useHealth()
  return (
    <div style={{ fontFamily: 'system-ui', padding: 24 }}>
      <h1>SLA Breach Warning System</h1>
      <p>Status: {data?.status ?? '...'}</p>
    </div>
  )
}
