"use client"

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { Book, Info } from 'lucide-react'
import ConceptView from './concept-view'
import { Concept } from './types'

export default function ConceptsPage() {
  const [concepts, setConcepts] = useState<Concept[]>([])
  const [selectedConcept, setSelectedConcept] = useState<Concept | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchConcepts() {
      try {
        setLoading(true)
        const response = await fetch('/api/concepts')
        const data = await response.json()
        setConcepts(data)
      } catch (error) {
        console.error('Error fetching concepts:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchConcepts()
  }, [])

  if (loading && !concepts.length) {
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
          <Book className="w-8 h-8" />
          <h1 className="text-3xl font-bold">Concepts</h1>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="col-span-1 space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Concepts Overview</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {concepts.map((concept) => (
                    <button
                      key={concept.name}
                      className="w-full text-left px-3 py-2 rounded-md hover:bg-accent hover:text-accent-foreground"
                      onClick={() => setSelectedConcept(concept)}
                    >
                      {concept.name}
                    </button>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Statistics</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Total Concepts</span>
                  <span className="font-medium">{concepts.length}</span>
                </div>
                <Separator />
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Recently Added</span>
                  <span className="font-medium">
                    {concepts.filter(c => {
                      const date = new Date(c.created_at)
                      const now = new Date()
                      const diffDays = Math.ceil((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24))
                      return diffDays <= 7
                    }).length}
                  </span>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="col-span-1 md:col-span-3">
            {selectedConcept ? (
              <ConceptView concept={selectedConcept} />
            ) : (
              <Card>
                <CardContent className="p-8 text-center text-muted-foreground">
                  <Info className="w-12 h-12 mx-auto mb-4" />
                  <p>Select a concept from the sidebar to view its details</p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}