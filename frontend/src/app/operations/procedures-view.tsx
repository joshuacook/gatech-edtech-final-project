// src/app/operations/procedures-view.tsx
import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Procedure } from './types'
import { StatusBadge } from './status-badge'
import { Clock } from 'lucide-react'

interface ProceduresViewProps {
  procedures: Procedure[]
}

export function ProceduresView({ procedures }: ProceduresViewProps) {
  return (
    <div className="space-y-6">
      {procedures.map((procedure) => (
        <Card key={procedure.name}>
          <CardHeader>
            <div className="flex justify-between items-start">
              <div>
                <CardTitle>{procedure.name}</CardTitle>
                <p className="text-sm text-muted-foreground">{procedure.description}</p>
              </div>
              <StatusBadge status={procedure.status} />
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <h4 className="text-sm font-medium mb-2">Steps</h4>
                <div className="space-y-2">
                  {procedure.steps.map((step) => (
                    <div key={step.order} className="flex items-start space-x-2 p-2 bg-muted rounded-md">
                      <span className="font-medium min-w-[2rem]">{step.order}.</span>
                      <span className="flex-grow">{step.description}</span>
                      <span className="flex items-center text-sm text-muted-foreground">
                        <Clock className="w-4 h-4 mr-1" />
                        {step.expected_duration}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
              <div className="flex justify-between text-sm text-muted-foreground">
                <span>Concept: {procedure.concept}</span>
                <span>Created: {new Date(procedure.created_at).toLocaleDateString()}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}