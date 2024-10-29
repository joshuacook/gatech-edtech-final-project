
// src/app/operations/types.ts

export interface Implementation {
    name: string
    type: "Design" | "Configuration" | "Integration" | "Process"
    description: string
    details: Record<string, string>
    concept: string
    status: "Active" | "Draft" | "Archived"
    created_at: string
  }
  
  export interface ProcedureStep {
    order: number
    description: string
    expected_duration: string
  }
  
  export interface Procedure {
    name: string
    description: string
    steps: ProcedureStep[]
    concept: string
    status: "Active" | "Draft" | "Archived"
    created_at: string
  }
  
  export interface Tool {
    name: string
    purpose: string
    type: "Software" | "Framework" | "Service" | "Hardware"
    concepts: string[]
    integration_details?: {
      "Access Level": string
      "Primary Use": string
      "Key Features": string[]
      [key: string]: string | string[]
    }
    status: "Active" | "Evaluation" | "Deprecated"
    created_at: string
  }
  
  export interface OperationsByConceptResponse {
    implementations: Implementation[]
    procedures: Procedure[]
    tools: Tool[]
  }