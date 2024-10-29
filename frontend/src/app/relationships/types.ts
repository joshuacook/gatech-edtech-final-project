// Base concept type for reference
export interface Concept {
  name: string
  definition: string
  citations?: string[]
  synonyms?: string[]
  created_at: string
  understanding_level: string
}

// Basic relationship structure (from MongoDB)
export interface BaseRelationship {
  source: string
  target: string
  type: string
  connection_type?: string
  strength: number
  created_at: string
}

// Relationship with populated concept references
export interface PopulatedRelationship extends Omit<BaseRelationship, 'source' | 'target'> {
  source: Concept
  target: Concept
}

// Network graph types
export interface NetworkGraphNode extends BaseRelationship {}

export interface NetworkGraphProps {
  relationships: NetworkGraphNode[]
}