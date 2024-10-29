"use client"

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Link, ListFilter, Network } from 'lucide-react'
import RelationshipsTable from './relationships-table'
import NetworkGraph from './network-graph'
import { PopulatedRelationship, NetworkGraphNode } from './types'

export default function RelationshipsPage() {
  const [relationships, setRelationships] = useState<PopulatedRelationship[]>([])
  const [networkGraphRelationships, setNetworkGraphRelationships] = useState<NetworkGraphNode[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true)
        const response = await fetch('/api/relationships')
        const data = await response.json()
        setRelationships(data)
        const relationshipsFormatted = data.map((rel: PopulatedRelationship) => ({
          source: rel.source,
          target: rel.target,
          type: rel.type,
          connection_type: rel.connection_type,
          strength: rel.strength
        }))
        setNetworkGraphRelationships(relationshipsFormatted)
      } catch (error) {
        console.error('Error fetching data:', error)
      } finally {
        setLoading(false)
      }
    }
  
    fetchData()
  }, [])

  if (loading && !relationships.length) {
    return (
      <div className="p-8">
        <div>Loading...</div>
      </div>
    )
  }

  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <div className="flex items-center space-x-4">
          <Link className="w-8 h-8" />
          <h1 className="text-3xl font-bold">Relationships</h1>
        </div>

        <Tabs defaultValue="network" className="w-full">
          <TabsList className="grid w-full grid-cols-2 max-w-[400px]">
            <TabsTrigger value="network" className="flex items-center gap-2">
              <Network className="h-4 w-4" />
              Network View
            </TabsTrigger>
            <TabsTrigger value="list" className="flex items-center gap-2">
              <ListFilter className="h-4 w-4" />
              List View
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="network">
            <Card>
              <CardHeader>
                <CardTitle>Relationship Network</CardTitle>
              </CardHeader>
              <CardContent className="h-[600px]">
                <NetworkGraph relationships={networkGraphRelationships} />
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="list">
            <Card>
              <CardHeader>
                <CardTitle>Relationship List</CardTitle>
              </CardHeader>
              <CardContent>
                <RelationshipsTable relationships={networkGraphRelationships} />
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}