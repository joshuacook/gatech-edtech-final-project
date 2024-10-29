// src/app/operations/tools-view.tsx
import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tool } from './types'
import { StatusBadge } from './status-badge'

interface ToolsViewProps {
  tools: Tool[]
}

export function ToolsView({ tools }: ToolsViewProps) {
  return (
    <div className="space-y-6">
      {tools.map((tool) => (
        <Card key={tool.name}>
          <CardHeader>
            <div className="flex justify-between items-start">
              <div>
                <CardTitle>{tool.name}</CardTitle>
                <p className="text-sm text-muted-foreground">{tool.purpose}</p>
              </div>
              <StatusBadge status={tool.status} />
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {tool.integration_details && (
                <div>
                  <h4 className="text-sm font-medium mb-2">Integration Details</h4>
                  <div className="grid gap-2">
                    {Object.entries(tool.integration_details).map(([key, value]) => (
                      <div key={key} className="p-2 bg-muted rounded-md">
                        <span className="font-medium">{key}</span>
                        <div className="text-sm text-muted-foreground">
                          {Array.isArray(value) ? value.join(', ') : value}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              <div className="flex flex-wrap gap-2">
                {tool.concepts.map((concept) => (
                  <span 
                    key={concept}
                    className="px-2 py-1 text-sm bg-primary/10 rounded-md"
                  >
                    {concept}
                  </span>
                ))}
              </div>
              <div className="flex justify-between text-sm text-muted-foreground">
                <span>Type: {tool.type}</span>
                <span>Created: {new Date(tool.created_at).toLocaleDateString()}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}