"use client"
import React, { useState } from 'react';
import { 
  Search,
  Book,
  Plus,
  Filter,
  ArrowUpDown,
  ExternalLink,
  BookOpen,
  MessageSquare,
  Target,
  Network,
  LucideIcon,
  FileText,
  CheckCircle2,
  AlertCircle,
  Send,
  X
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

const ConceptsPage = () => {
  const [selectedConcept, setSelectedConcept] = useState(null);
  const [refinementMessages, setRefinementMessages] = useState([
    {
      role: 'assistant',
      content: 'How would you like to refine this concept? I can help clarify definitions, add examples, or expand relationships.',
      timestamp: '2024-03-20T10:00:00Z'
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [attachedDocs, setAttachedDocs] = useState([
    { name: 'Advanced Vector Spaces.pdf', status: 'processed' },
    { name: 'Linear Algebra Notes.pdf', status: 'processing' }
  ]);
  
  // Mock data for Linear Algebra course concepts
  const concepts = [
    {
      id: 1,
      lexeme: "Random Vector",
      definition: "A vector whose components are random variables, characterized by its probability distribution and statistical properties.",
      status: "active",
      relationships: 8,
      citations: 5,
      level: "Practical",
      lastUpdated: "2024-03-15",
      category: "Fundamentals",
      metadata: {
        hasImplementations: true,
        hasProcedures: true,
        hasAssessments: true
      }
    },
    {
      id: 2,
      lexeme: "Covariance Matrix",
      definition: "A square matrix whose entries are the covariances between the components of a random vector, representing the joint variability of the variables.",
      status: "active",
      relationships: 12,
      citations: 7,
      level: "Mastery",
      lastUpdated: "2024-03-14",
      category: "Estimation",
      metadata: {
        hasImplementations: true,
        hasProcedures: true,
        hasAssessments: true
      }
    },
    {
      id: 3, 
      lexeme: "Linear Transformation",
      definition: "A function between vector spaces that preserves vector addition and scalar multiplication operations.",
      status: "active",
      relationships: 10,
      citations: 6,
      level: "Intermediate",
      lastUpdated: "2024-03-13",
      category: "Vector Spaces",
      metadata: {
        hasImplementations: true,
        hasProcedures: true,
        hasAssessments: true
      }
    },
    {
      id: 4,
      lexeme: "Minimum Mean Square Error",
      definition: "An estimation method that minimizes the average squared difference between the estimated and actual values.",
      status: "draft",
      relationships: 6,
      citations: 4,
      level: "Basic",
      lastUpdated: "2024-03-12",
      category: "Estimation",
      metadata: {
        hasImplementations: false,
        hasProcedures: true,
        hasAssessments: true
      }
    },
    {
      id: 5,
      lexeme: "Cross-Correlation",
      definition: "A measure of similarity between two signals as a function of the displacement of one relative to the other.",
      status: "active",
      relationships: 7,
      citations: 5,
      level: "Intermediate",
      lastUpdated: "2024-03-11",
      category: "Signal Processing",
      metadata: {
        hasImplementations: true,
        hasProcedures: true,
        hasAssessments: false
      }
    }
  ];

  const handleSendMessage = () => {
    if (!inputMessage.trim()) return;

    // Mock new message
    const newMessages = [
      ...refinementMessages,
      {
        role: 'user',
        content: inputMessage,
        timestamp: new Date().toISOString()
      },
      {
        role: 'assistant',
        content: 'I\'ve updated the concept based on your input. The definition now includes your clarification about vector space properties.',
        timestamp: new Date().toISOString()
      }
    ];

    setRefinementMessages(newMessages);
    setInputMessage('');
  };

  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Book className="w-8 h-8" />
            <div>
              <h1 className="text-3xl font-bold">Linear Algebra Concepts</h1>
              <p className="text-sm text-muted-foreground">
                Linear Algebra and Estimation Theory Course Concepts
              </p>
            </div>
          </div>
          <button className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-md">
            <Plus className="w-4 h-4" />
            New Concept
          </button>
        </div>

        {/* Search and Filters */}
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <input 
                  className="w-full pl-10 pr-4 py-2 border rounded-md" 
                  placeholder="Search linear algebra concepts..."
                />
              </div>
              <button className="flex items-center gap-2 px-4 py-2 border rounded-md">
                <Filter className="w-4 h-4" />
                Filters
              </button>
              <button className="flex items-center gap-2 px-4 py-2 border rounded-md">
                <ArrowUpDown className="w-4 h-4" />
                Sort
              </button>
            </div>
          </CardContent>
        </Card>

        {/* Main Content Grid */}
        <div className="grid grid-cols-3 gap-6">
          {/* Concept List */}
          <div className="col-span-1 space-y-4">
            {concepts.map(concept => (
              <Card 
                key={concept.id}
                className={`cursor-pointer hover:shadow-md transition-shadow ${
                  selectedConcept?.id === concept.id ? 'border-primary' : ''
                }`}
                onClick={() => setSelectedConcept(concept)}
              >
                <CardHeader className="p-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-lg">{concept.lexeme}</CardTitle>
                      <CardDescription className="line-clamp-2">
                        {concept.definition}
                      </CardDescription>
                    </div>
                    <Badge variant={concept.status === 'active' ? 'default' : 'secondary'}>
                      {concept.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="p-4 pt-0">
                  <div className="flex items-center gap-4 text-sm text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <Network className="w-4 h-4" />
                      {concept.relationships}
                    </span>
                    <span className="flex items-center gap-1">
                      <FileText className="w-4 h-4" />
                      {concept.citations}
                    </span>
                    <Badge variant="outline">{concept.level}</Badge>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Concept Details */}
          <div className="col-span-2">
            {selectedConcept ? (
              <div className="space-y-6">
                <Card>
                  <CardHeader className="p-6">
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="flex items-center gap-2">
                          <CardTitle className="text-2xl">{selectedConcept.lexeme}</CardTitle>
                          <Badge>{selectedConcept.category}</Badge>
                        </div>
                        <CardDescription className="mt-2">
                          Last updated {selectedConcept.lastUpdated}
                        </CardDescription>
                      </div>
                      <div className="flex gap-2">
                        <button className="p-2 hover:bg-secondary rounded-md">
                          <ExternalLink className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="p-6 pt-0">
                    <Tabs defaultValue="details">
                      <TabsList>
                        <TabsTrigger value="details">Details</TabsTrigger>
                        <TabsTrigger value="refine">Refine</TabsTrigger>
                      </TabsList>

                      <TabsContent value="details">
                        <div className="prose max-w-none">
                          <div className="space-y-6">
                            <div>
                              <h3 className="text-lg font-medium mb-2">Definition</h3>
                              <p className="text-muted-foreground">
                                {selectedConcept.definition}
                              </p>
                            </div>

                            <div className="grid grid-cols-3 gap-4">
                              {selectedConcept.metadata.hasImplementations && (
                                <Card>
                                  <CardContent className="p-4">
                                    <div className="flex items-center gap-2">
                                      <CheckCircle2 className="w-4 h-4 text-green-500" />
                                      <span className="font-medium">MATLAB Implementation</span>
                                    </div>
                                  </CardContent>
                                </Card>
                              )}
                              {selectedConcept.metadata.hasProcedures && (
                                <Card>
                                  <CardContent className="p-4">
                                    <div className="flex items-center gap-2">
                                      <CheckCircle2 className="w-4 h-4 text-green-500" />
                                      <span className="font-medium">Calculation Steps</span>
                                    </div>
                                  </CardContent>
                                </Card>
                              )}
                              {selectedConcept.metadata.hasAssessments && (
                                <Card>
                                  <CardContent className="p-4">
                                    <div className="flex items-center gap-2">
                                      <CheckCircle2 className="w-4 h-4 text-green-500" />
                                      <span className="font-medium">Practice Problems</span>
                                    </div>
                                  </CardContent>
                                </Card>
                              )}
                            </div>

                            <div className="grid grid-cols-2 gap-6">
                              <div>
                                <h3 className="text-lg font-medium mb-4">Understanding Level</h3>
                                <div className="space-y-2">
                                  <div className="flex items-center justify-between p-2 bg-secondary rounded">
                                    <span>Mastery</span>
                                    <Badge variant="outline">Target</Badge>
                                  </div>
                                  <div className="flex items-center justify-between p-2">
                                    <span>Practical</span>
                                    <Badge variant="outline">Current</Badge>
                                  </div>
                                  <div className="flex items-center justify-between p-2">
                                    <span>Basic</span>
                                    <Badge variant="outline">Achieved</Badge>
                                  </div>
                                </div>
                              </div>

                              <div>
                                <h3 className="text-lg font-medium mb-4">Related Concepts</h3>
                                <div className="space-y-2">
                                  <div className="p-2 border rounded">
                                    <div className="text-sm">Vector Spaces</div>
                                    <div className="text-xs text-muted-foreground">Foundation concept</div>
                                  </div>
                                  <div className="p-2 border rounded">
                                    <div className="text-sm">Linear Transformations</div>
                                    <div className="text-xs text-muted-foreground">Related operation</div>
                                  </div>
                                  <div className="p-2 border rounded">
                                    <div className="text-sm">Estimation Theory</div>
                                    <div className="text-xs text-muted-foreground">Application area</div>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </TabsContent>

                      <TabsContent value="refine">
                        <Tabs defaultValue="chat">
                          <TabsList>
                            <TabsTrigger value="chat" className="flex items-center gap-2">
                              <MessageSquare className="w-4 h-4" />
                              Chat Refinement
                            </TabsTrigger>
                            <TabsTrigger value="docs" className="flex items-center gap-2">
                              <FileText className="w-4 h-4" />
                              Document Attachment
                            </TabsTrigger>
                          </TabsList>

                          <TabsContent value="chat" className="mt-4">
                            <ScrollArea className="h-[400px] border rounded-lg p-4">
                              {refinementMessages.map((message, index) => (
                                <div
                                  key={index}
                                  className={`mb-4 p-3 rounded-lg ${
                                    message.role === 'user' 
                                      ? 'bg-primary text-primary-foreground ml-12' 
                                      : 'bg-muted mr-12'
                                  }`}
                                >
                                  <div className="text-sm">{message.content}</div>
                                  <div className="text-xs mt-1 opacity-70">
                                    {new Date(message.timestamp).toLocaleTimeString()}
                                  </div>
                                </div>
                              ))}
                            </ScrollArea>
                            <div className="flex gap-2 mt-4">
                              <Input
                                value={inputMessage}
                                onChange={(e) => setInputMessage(e.target.value)}
                                placeholder="Type your refinement suggestion..."
                                onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                              />
                              <Button onClick={handleSendMessage}>
                                  <Send className="w-4 h-4" />
                                </Button>
                              </div>
                          </TabsContent>

                          <TabsContent value="docs" className="mt-4">
                            <div className="space-y-4">
                              <div className="border-2 border-dashed rounded-lg p-8 text-center">
                                <Input
                                  type="file"
                                  className="hidden"
                                  id="doc-upload"
                                  onChange={(e) => {
                                    if (e.target.files?.[0]) {
                                      setAttachedDocs(prev => [...prev, {
                                        name: e.target.files[0].name,
                                        status: 'processing'
                                      }]);
                                    }
                                  }}
                                />
                                <label
                                  htmlFor="doc-upload"
                                  className="cursor-pointer"
                                >
                                  <FileText className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                                  <p className="text-sm text-muted-foreground">
                                    Drop files here or click to upload supporting documents
                                  </p>
                                </label>
                              </div>

                              <div className="space-y-2">
                                {attachedDocs.map((doc, index) => (
                                  <div key={index} className="flex items-center justify-between p-2 border rounded">
                                    <div className="flex items-center gap-2">
                                      <FileText className="w-4 h-4" />
                                      <span>{doc.name}</span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                      <Badge variant={doc.status === 'processed' ? 'default' : 'secondary'}>
                                        {doc.status}
                                      </Badge>
                                      <Button variant="ghost" size="icon">
                                        <X className="w-4 h-4" />
                                      </Button>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          </TabsContent>
                        </Tabs>
                      </TabsContent>
                    </Tabs>
                  </CardContent>
                </Card>
              </div>
            ) : (
              <div className="h-full flex items-center justify-center text-muted-foreground">
                Select a concept to view details
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConceptsPage;