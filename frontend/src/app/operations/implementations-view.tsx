// src/app/operations/implementations-view.tsx
import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Implementation } from './types'
import { StatusBadge } from './status-badge'

interface ImplementationsViewProps {
  implementations: Implementation[]
}

export function ImplementationsView({ implementations }: ImplementationsViewProps) {
  return (
    <div className="space-y-6">
      {implementations.map((implementation) => (
        <Card key={implementation.name}>
          <CardHeader>
            <div className="flex justify-between items-start">
              <div>
                <CardTitle>{implementation.name}</CardTitle>
                <p className="text-sm text-muted-foreground">{implementation.description}</p>
              </div>
              <StatusBadge status={implementation.status} />
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4">
              <div>
                <h4 className="text-sm font-medium mb-2">Details</h4>
                <div className="grid grid-cols-2 gap-2">
                  {Object.entries(implementation.details).map(([key, value]) => (
                    <div key={key} className="flex justify-between p-2 bg-muted rounded-md">
                      <span className="font-medium">{key}</span>
                      <span className="text-muted-foreground">{value}</span>
                    </div>
                  ))}
                </div>
              </div>
              <div className="flex justify-between text-sm text-muted-foreground">
                <span>Concept: {implementation.concept}</span>
                <span>Created: {new Date(implementation.created_at).toLocaleDateString()}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

