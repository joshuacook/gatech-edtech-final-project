// app/relationships/relationship-form.tsx
'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

interface Concept {
  name: string
  definition: string
}

interface RelationshipFormProps {
  onSuccess: () => void
}

const RELATIONSHIP_TYPES = {
  'Equivalence': 1.0,
  'Subsumption': 0.8,
  'Overlap': 0.6,
  'Related': 0.4,
  'Disjoint': 0.2,
  'None': 0.0
}

const CONNECTION_TYPES = [
  'Causal',
  'Temporal',
  'Spatial',
  'Functional'
]

export default function RelationshipForm({ onSuccess }: RelationshipFormProps) {
  const [concepts, setConcepts] = useState<Concept[]>([])
  const [formData, setFormData] = useState({
    source: '',
    target: '',
    type: '',
    connection_type: '',
    strength: 0
  })
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    const fetchConcepts = async () => {
      try {
        const response = await fetch('/api/concepts')
        const data = await response.json()
        setConcepts(data)
      } catch (error) {
        console.error('Error fetching concepts:', error)
      }
    }

    fetchConcepts()
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)

    try {
      const response = await fetch('/api/relationships', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
          strength: RELATIONSHIP_TYPES[formData.type as keyof typeof RELATIONSHIP_TYPES]
        }),
      })

      if (response.ok) {
        onSuccess()
      } else {
        const error = await response.json()
        console.error('Error creating relationship:', error)
      }
    } catch (error) {
      console.error('Error creating relationship:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 pt-4">
      <div className="space-y-2">
        <label className="text-sm font-medium">Source Concept</label>
        <Select 
          value={formData.source}
          onValueChange={value => setFormData(prev => ({ ...prev, source: value }))}
        >
          <SelectTrigger>
            <SelectValue placeholder="Select source concept" />
          </SelectTrigger>
          <SelectContent>
            {concepts.map(concept => (
              <SelectItem key={concept.name} value={concept.name}>
                {concept.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium">Target Concept</label>
        <Select 
          value={formData.target}
          onValueChange={value => setFormData(prev => ({ ...prev, target: value }))}
        >
          <SelectTrigger>
            <SelectValue placeholder="Select target concept" />
          </SelectTrigger>
          <SelectContent>
            {concepts.map(concept => (
              <SelectItem key={concept.name} value={concept.name}>
                {concept.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium">Relationship Type</label>
        <Select 
          value={formData.type}
          onValueChange={value => setFormData(prev => ({ ...prev, type: value }))}
        >
          <SelectTrigger>
            <SelectValue placeholder="Select relationship type" />
          </SelectTrigger>
          <SelectContent>
            {Object.entries(RELATIONSHIP_TYPES).map(([type, strength]) => (
              <SelectItem key={type} value={type}>
                {type} ({(strength * 100)}% strength)
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {formData.type === 'Related' && (
        <div className="space-y-2">
          <label className="text-sm font-medium">Connection Type</label>
          <Select 
            value={formData.connection_type}
            onValueChange={value => setFormData(prev => ({ ...prev, connection_type: value }))}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select connection type" />
            </SelectTrigger>
            <SelectContent>
              {CONNECTION_TYPES.map(type => (
                <SelectItem key={type} value={type}>
                  {type}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      )}

      <Button type="submit" className="w-full" disabled={isSubmitting}>
        {isSubmitting ? 'Creating...' : 'Create Relationship'}
      </Button>
    </form>
  )
}