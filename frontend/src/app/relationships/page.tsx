"use client"

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { 
  Sheet,
  SheetContent, 
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet'
import { Link, Network, BadgePlus } from 'lucide-react'
import RelationshipForm from './relationship-form'
import RelationshipsTable from './relationships-table'
import NetworkGraph from './network-graph'

interface Relationship {
  source: string
  target: string
  type: string
  connection_type?: string
  strength: number
  created_at: string
}

interface RelationshipMetrics {
  total_relationships: number
  average_strength: number
  network_density: number
}

export default function RelationshipsPage() {
  const [relationships, setRelationships] = useState<Relationship[]>([])
  const [metrics, setMetrics] = useState<RelationshipMetrics>({
    total_relationships: 0,
    average_strength: 0,
    network_density: 0
  })
  const [editingRelationship, setEditingRelationship] = useState<Relationship | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [relationshipsResponse, metricsResponse] = await Promise.all([
        fetch('/api/relationships'),
        fetch('/api/relationships/metrics')
      ])
      
      const relationshipsData = await relationshipsResponse.json()
      const metricsData = await metricsResponse.json()
      
      setRelationships(relationshipsData)
      setMetrics(metricsData)
    } catch (error) {
      console.error('Error fetching data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = (source: string, target: string) => {
    setRelationships(prev => 
      prev.filter(r => !(r.source === source && r.target === target))
    )
  }

  const handleEdit = (relationship: Relationship) => {
    setEditingRelationship(relationship)
  }

  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <Link className="w-8 h-8" />
            <h1 className="text-3xl font-bold">Relationships Management</h1>
          </div>
          
          <Sheet>
            <SheetTrigger asChild>
              <Button>
                <BadgePlus className="mr-2 h-4 w-4" />
                Create Relationship
              </Button>
            </SheetTrigger>
            <SheetContent className="w-[600px]">
              <SheetHeader>
                <SheetTitle>Create New Relationship</SheetTitle>
              </SheetHeader>
              <RelationshipForm 
                onSuccess={() => {
                  fetchData()
                }} 
              />
            </SheetContent>
          </Sheet>
        </div>

        {/* Metrics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Total Relationships</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">
                {metrics.total_relationships}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Average Strength</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">
                {(metrics.average_strength * 100).toFixed(1)}%
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Network Density</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">
                {(metrics.network_density * 100).toFixed(1)}%
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Network Graph */}
        <Card className="col-span-1">
          <CardHeader>
            <CardTitle>Relationship Network</CardTitle>
          </CardHeader>
          <CardContent className="h-[600px]">
            <NetworkGraph relationships={relationships} />
          </CardContent>
        </Card>

        {/* Relationships Table */}
        <Card className="col-span-1">
          <CardHeader>
            <CardTitle>Relationship List</CardTitle>
          </CardHeader>
          <CardContent>
            <RelationshipsTable
              relationships={relationships}
              onDelete={handleDelete}
              onEdit={handleEdit}
            />
          </CardContent>
        </Card>

        {/* Edit Sheet */}
        {editingRelationship && (
          <Sheet 
            open={!!editingRelationship} 
            onOpenChange={() => setEditingRelationship(null)}
          >
            <SheetContent className="w-[600px]">
              <SheetHeader>
                <SheetTitle>Edit Relationship</SheetTitle>
              </SheetHeader>
              <RelationshipForm
                relationship={editingRelationship}
                onSuccess={() => {
                  setEditingRelationship(null)
                  fetchData()
                }}
              />
            </SheetContent>
          </Sheet>
        )}
      </div>
    </div>
  )
}