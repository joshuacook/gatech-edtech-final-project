// app/concepts/page.tsx
'use client'
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
import { Separator } from '@/components/ui/separator'
import { PlusCircle, Book, Info } from 'lucide-react'
import ConceptForm from './concept-form'
import ConceptView from './concept-view'

interface Concept {
  name: string
  definition: string
  citations: string[]
  synonyms: string[]
  understanding_level: string
  created_at: string
}

export default function ConceptsPage() {
  const [concepts, setConcepts] = useState<Concept[]>([])
  const [selectedConcept, setSelectedConcept] = useState<Concept | null>(null)
  const [isEditing, setIsEditing] = useState(false)

  useEffect(() => {
    fetchConcepts()
  }, [])

  const fetchConcepts = async () => {
    try {
      const response = await fetch('/api/concepts')
      const data = await response.json()
      setConcepts(data)
    } catch (error) {
      console.error('Error fetching concepts:', error)
    }
  }

  const handleConceptCreated = () => {
    fetchConcepts()
  }

  const handleConceptUpdated = () => {
    fetchConcepts()
    setIsEditing(false)
  }

  return (
    <div className="container mx-auto p-6 space-y-8">
      <div className="flex justify-between items-center">
        <div className="flex items-center space-x-4">
          <Book className="w-8 h-8" />
          <h1 className="text-3xl font-bold">Concepts Management</h1>
        </div>
        
        <Sheet>
          <SheetTrigger asChild>
            <Button>
              <PlusCircle className="mr-2 h-4 w-4" />
              Create Concept
            </Button>
          </SheetTrigger>
          <SheetContent className="w-[600px]">
            <SheetHeader>
              <SheetTitle>Create New Concept</SheetTitle>
            </SheetHeader>
            <ConceptForm onSuccess={handleConceptCreated} />
          </SheetContent>
        </Sheet>
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
                  <Button
                    key={concept.name}
                    variant="ghost"
                    className="w-full justify-start text-left"
                    onClick={() => {
                      setSelectedConcept(concept)
                      setIsEditing(false)
                    }}
                  >
                    {concept.name}
                  </Button>
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
            <ConceptView
              concept={selectedConcept}
              isEditing={isEditing}
              onEditClick={() => setIsEditing(true)}
              onUpdate={handleConceptUpdated}
            />
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
  )
}