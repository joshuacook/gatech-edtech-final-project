// src/app/operations/page.tsx
"use client"

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Cog, Package, FileText, Hammer } from 'lucide-react'
import { Implementation, Procedure, Tool } from './types'
import { ImplementationsView } from './implementations-view'
import { ProceduresView } from './procedures-view'
import { ToolsView } from './tools-view'

export default function OperationsPage() {
  const [implementations, setImplementations] = useState<Implementation[]>([])
  const [procedures, setProcedures] = useState<Procedure[]>([])
  const [tools, setTools] = useState<Tool[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true)
        const [implRes, procRes, toolsRes] = await Promise.all([
          fetch('/api/implementations'),
          fetch('/api/procedures'),
          fetch('/api/tools')
        ])
        
        const [implData, procData, toolsData] = await Promise.all([
          implRes.json(),
          procRes.json(),
          toolsRes.json()
        ])
        
        setImplementations(implData)
        setProcedures(procData)
        setTools(toolsData)
      } catch (error) {
        console.error('Error fetching operational data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  if (loading) {
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
          <Cog className="w-8 h-8" />
          <h1 className="text-3xl font-bold">Operational Elements</h1>
        </div>

        {/* Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center space-x-4">
              <Package className="w-5 h-5" />
              <div>
                <CardTitle>Implementations</CardTitle>
                <p className="text-sm text-muted-foreground">
                  Active: {implementations.filter(i => i.status === 'Active').length}
                </p>
              </div>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center space-x-4">
              <FileText className="w-5 h-5" />
              <div>
                <CardTitle>Procedures</CardTitle>
                <p className="text-sm text-muted-foreground">
                  Active: {procedures.filter(p => p.status === 'Active').length}
                </p>
              </div>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center space-x-4">
              <Hammer className="w-5 h-5" />
              <div>
                <CardTitle>Tools</CardTitle>
                <p className="text-sm text-muted-foreground">
                  Active: {tools.filter(t => t.status === 'Active').length}
                </p>
              </div>
            </CardHeader>
          </Card>
        </div>

        {/* Main Content Tabs */}
        <Tabs defaultValue="implementations" className="w-full">
          <TabsList className="grid w-full grid-cols-3 max-w-[600px]">
            <TabsTrigger value="implementations" className="flex items-center gap-2">
              <Package className="h-4 w-4" />
              Implementations
            </TabsTrigger>
            <TabsTrigger value="procedures" className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              Procedures
            </TabsTrigger>
            <TabsTrigger value="tools" className="flex items-center gap-2">
              <Hammer className="h-4 w-4" />
              Tools
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="implementations">
            <ImplementationsView implementations={implementations} />
          </TabsContent>
          
          <TabsContent value="procedures">
            <ProceduresView procedures={procedures} />
          </TabsContent>
          
          <TabsContent value="tools">
            <ToolsView tools={tools} />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}