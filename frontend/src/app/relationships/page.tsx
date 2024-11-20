"use client"
import React, { useState } from 'react';
import { 
  Network,
  Plus,
  ZoomIn,
  ZoomOut,
  Focus,
  ChevronLeft,
  Search,
  Filter,
  ArrowUpDown,
} from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import NetworkVisualization from './NetworkVisualization';

const ConceptDetailsModal = ({ concept, onClose }) => {
  if (!concept) return null;
  
  return (
    <Dialog open={!!concept} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>
            <div className="flex items-center gap-2">
              <span>{concept.label}</span>
              <Badge>{concept.category}</Badge>
            </div>
          </DialogTitle>
        </DialogHeader>
        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-medium mb-2">Definition</h3>
            <p className="text-muted-foreground">
              {concept.definition || "A foundational concept in linear algebra that provides the mathematical structure for understanding vector operations and transformations."}
            </p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <h3 className="text-lg font-medium mb-2">Properties</h3>
              <div className="space-y-2">
                {['Closure under addition', 'Scalar multiplication', 'Distributive properties'].map((prop) => (
                  <div key={prop} className="p-2 bg-secondary rounded">
                    {prop}
                  </div>
                ))}
              </div>
            </div>
            <div>
              <h3 className="text-lg font-medium mb-2">Related Concepts</h3>
              <div className="space-y-2">
                {concept.related?.map((rel) => (
                  <div key={rel.name} className="p-2 border rounded">
                    <div className="text-sm">{rel.name}</div>
                    <div className="text-xs text-muted-foreground">{rel.type}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default function RelationshipsPage() {
  const [currentView, setCurrentView] = useState('topLevel');
  const [selectedConcept, setSelectedConcept] = useState(null);
  
  // Modified conceptData section in RelationshipsPage
const conceptData = {
  'Vector Spaces': {
    label: 'Vector Spaces',
    category: 'Fundamentals',
    definition: 'A mathematical structure that consists of a collection of vectors, which may be added together and multiplied by scalars.',
    related: [
      { name: 'Linear Transformations', type: 'Child concept' },
      { name: 'Matrix Theory', type: 'Related concept' },
      { name: 'Random Processes', type: 'Application' },
    ]
  },
  'Linear Transformations': {
    label: 'Linear Transformations',
    category: 'Operations',
    definition: 'A mapping between vector spaces that preserves vector addition and scalar multiplication.',
    related: [
      { name: 'Vector Spaces', type: 'Parent concept' },
      { name: 'Matrix Theory', type: 'Implementation' },
      { name: 'Estimation Theory', type: 'Application' },
    ]
  },
  'Random Processes': {
    label: 'Random Processes',
    category: 'Applications',
    definition: 'A collection of random variables indexed by time or space, used to model systems with uncertainty.',
    related: [
      { name: 'Vector Spaces', type: 'Foundation' },
      { name: 'Estimation Theory', type: 'Application' },
    ]
  },
  'Estimation Theory': {
    label: 'Estimation Theory',
    category: 'Applications',
    definition: 'A branch of statistics and signal processing that deals with estimating the values of parameters based on measured data.',
    related: [
      { name: 'Random Processes', type: 'Foundation' },
      { name: 'Linear Transformations', type: 'Tool' },
    ]
  },
  'Matrix Theory': {
    label: 'Matrix Theory',
    category: 'Fundamentals',
    definition: 'The study of matrices and their properties, particularly in relation to linear transformations and vector spaces.',
    related: [
      { name: 'Vector Spaces', type: 'Foundation' },
      { name: 'Linear Transformations', type: 'Application' },
    ]
  },  
  'Stochastic Processes': {
    label: 'Stochastic Processes',
    category: 'Theory',
    definition: 'Mathematical objects usually defined as a collection of random variables indexed by some set.',
    related: [
      { name: 'Random Processes', type: 'Parent concept' },
      { name: 'Markov Processes', type: 'Related concept' },
    ]
  },
  'Time Series': {
    label: 'Time Series',
    category: 'Applications',
    definition: 'A sequence of data points ordered in time, used to track changes and patterns over time.',
    related: [
      { name: 'Random Processes', type: 'Parent concept' },
      { name: 'Stochastic Processes', type: 'Related concept' },
    ]
  },
  'Markov Processes': {
    label: 'Markov Processes',
    category: 'Theory',
    definition: 'A stochastic process with the property that the future states depend only on the current state.',
    related: [
      { name: 'Random Processes', type: 'Parent concept' },
      { name: 'Stochastic Processes', type: 'Related concept' },
    ]
  },
  'Gaussian Processes': {
    label: 'Gaussian Processes',
    category: 'Theory',
    definition: 'A collection of random variables, any finite number of which have a multivariate normal distribution.',
    related: [
      { name: 'Random Processes', type: 'Parent concept' },
      { name: 'Stochastic Processes', type: 'Related concept' },
    ]
  },
};

  const handleNodeClick = (conceptName) => {
    if (conceptName === 'Random Processes' && currentView === 'topLevel') {
      setCurrentView('randomProcesses');
    } else {
      setSelectedConcept(conceptData[conceptName]);
    }
  };

  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Network className="w-8 h-8" />
            <div>
              <h1 className="text-3xl font-bold">Concept Network</h1>
              <p className="text-sm text-muted-foreground">
                Linear Algebra and Estimation Theory Concept Network
              </p>
            </div>
          </div>
          <button className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-md">
            <Plus className="w-4 h-4" />
            Add Relationship
          </button>
        </div>

        {/* Navigation */}
        {currentView !== 'topLevel' && (
          <div className="flex items-center gap-2">
            <button 
              className="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
              onClick={() => setCurrentView('topLevel')}
            >
              <ChevronLeft className="w-4 h-4" />
              Back to Overview
            </button>
            <span className="text-sm text-muted-foreground">/</span>
            <span className="text-sm">
              {currentView === 'randomProcesses' ? 'Random Processes Detail' : 'Vector Spaces Detail'}
            </span>
          </div>
        )}

        {/* Network Visualization Card */}
        <div className="relative w-full h-[600px] bg-white rounded-lg border shadow-sm">
          <div className="absolute top-4 left-4 space-y-2 z-10">
            <button className="p-2 bg-white rounded-full shadow hover:bg-slate-50">
              <ZoomIn className="w-4 h-4" />
            </button>
            <button className="p-2 bg-white rounded-full shadow hover:bg-slate-50">
              <ZoomOut className="w-4 h-4" />
            </button>
            <button className="p-2 bg-white rounded-full shadow hover:bg-slate-50">
              <Focus className="w-4 h-4" />
            </button>
          </div>

          <div className="w-full h-full">
          <NetworkVisualization 
            onNodeClick={handleNodeClick}
            currentView={currentView}
          />
          </div>
        </div>

        {/* Concept Details Modal */}
        <ConceptDetailsModal 
          concept={selectedConcept}
          onClose={() => setSelectedConcept(null)}
        />
      </div>
    </div>
  );
}