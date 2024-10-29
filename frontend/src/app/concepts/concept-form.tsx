// app/concepts/concept-form.tsx
import React from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useState } from 'react'

interface ConceptFormProps {
  concept?: {
    name: string
    definition: string
    citations: string[]
    synonyms: string[]
    understanding_level: string
  }
  onSuccess: () => void
}

export default function ConceptForm({ concept, onSuccess }: ConceptFormProps) {
  const [formData, setFormData] = useState({
    name: concept?.name || '',
    definition: concept?.definition || '',
    citations: concept?.citations.join('\n') || '',
    synonyms: concept?.synonyms.join(', ') || '',
    understanding_level: concept?.understanding_level || 'None'
  })
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)

    const payload = {
      name: formData.name,
      definition: formData.definition,
      citations: formData.citations.split('\n').filter(c => c.trim()),
      synonyms: formData.synonyms.split(',').map(s => s.trim()).filter(Boolean),
      understanding_level: formData.understanding_level
    }

    try {
      const response = await fetch(concept 
        ? `/api/concepts/${encodeURIComponent(concept.name)}`
        : '/api/concepts', { 
        method: concept ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })

      if (response.ok) {
        onSuccess()
      } else {
        console.error('Error saving concept:', await response.text())
      }
    } catch (error) {
      console.error('Error saving concept:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 pt-4">
      {!concept && (
        <div className="space-y-2">
          <label className="text-sm font-medium">Concept Name</label>
          <Input
            value={formData.name}
            onChange={e => setFormData(prev => ({ ...prev, name: e.target.value }))}
            placeholder="Enter concept name"
            required
          />
        </div>
      )}

      <div className="space-y-2">
        <label className="text-sm font-medium">Definition</label>
        <Textarea
          value={formData.definition}
          onChange={e => setFormData(prev => ({ ...prev, definition: e.target.value }))}
          placeholder="Enter concept definition"
          required
        />
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium">Citations (one per line)</label>
        <Textarea
          value={formData.citations}
          onChange={e => setFormData(prev => ({ ...prev, citations: e.target.value }))}
          placeholder="Enter citations"
        />
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium">Synonyms (comma separated)</label>
        <Input
          value={formData.synonyms}
          onChange={e => setFormData(prev => ({ ...prev, synonyms: e.target.value }))}
          placeholder="Enter synonyms"
        />
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium">Understanding Level</label>
        <Select
          value={formData.understanding_level}
          onValueChange={value => setFormData(prev => ({ ...prev, understanding_level: value }))}
        >
          <SelectTrigger>
            <SelectValue placeholder="Select understanding level" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="None">None</SelectItem>
            <SelectItem value="Functional">Functional</SelectItem>
            <SelectItem value="Practical">Practical</SelectItem>
            <SelectItem value="Proficient">Proficient</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <Button type="submit" className="w-full" disabled={isSubmitting}>
        {isSubmitting ? 'Saving...' : (concept ? 'Update Concept' : 'Create Concept')}
      </Button>
    </form>
  )
}