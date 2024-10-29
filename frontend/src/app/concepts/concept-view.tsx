import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Calendar, Star } from 'lucide-react'

interface ConceptViewProps {
  concept: {
    name: string
    definition: string
    citations: string[]
    synonyms: string[]
    understanding_level: string
    created_at: string
  }
}

export default function ConceptView({ concept }: ConceptViewProps) {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>{concept.name}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div>
            <h3 className="font-medium mb-2">Definition</h3>
            <p className="text-muted-foreground">{concept.definition}</p>
          </div>

          {concept.citations.length > 0 && (
            <div>
              <h3 className="font-medium mb-2">Citations</h3>
              <ul className="list-disc list-inside space-y-1">
                {concept.citations.map((citation, index) => (
                  <li key={index} className="text-muted-foreground">{citation}</li>
                ))}
              </ul>
            </div>
          )}

          {concept.synonyms.length > 0 && (
            <div>
              <h3 className="font-medium mb-2">Synonyms</h3>
              <div className="flex flex-wrap gap-2">
                {concept.synonyms.map((synonym, index) => (
                  <span 
                    key={index}
                    className="inline-flex items-center rounded-md bg-muted px-2 py-1 text-sm"
                  >
                    {synonym}
                  </span>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <div className="grid grid-cols-2 gap-6">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center space-x-3">
              <Calendar className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="text-sm font-medium">Created</p>
                <p className="text-sm text-muted-foreground">
                  {new Date(concept.created_at).toLocaleDateString()}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center space-x-3">
              <Star className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="text-sm font-medium">Understanding Level</p>
                <p className="text-sm text-muted-foreground">
                  {concept.understanding_level}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}