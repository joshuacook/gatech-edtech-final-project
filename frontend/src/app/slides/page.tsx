// src/app/slides/page.tsx
import React from 'react';
import { Book, MessageSquare, Edit3, PlusCircle, Share2, Layout, List, Play, AlertCircle, Columns, ArrowRight } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import Image from 'next/image';

export default function SlideGenerationPage() {
  return (
    <main className="container mx-auto p-8">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-4xl">
            <Book className="h-5 w-5" />
            Generate Slides: Random Vectors & Covariance
          </CardTitle>
          <CardDescription className="text-lg">Week 3, Class 1 - Slide Generation and Customization</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {/* AI Assistant Interface */}
            <div className="rounded-lg border p-4">
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <MessageSquare className="h-5 w-5" />
                  <div className="font-medium">AI Slide Assistant</div>
                </div>
                <div className="flex items-start gap-2">
                  <input 
                    type="text"
                    placeholder="Create slides for covariance matrix properties with visual examples..."
                    className="flex-1 p-2 rounded border"
                  />
                  <button className="px-4 py-2 bg-blue-500 text-white rounded">Generate</button>
                </div>
                <div className="text-xs text-slate-500">
                  Suggested: "Add interactive matrix visualization" | "Include real-world examples" | "Add practice problems"
                </div>
              </div>
            </div>

            {/* Main Content Area */}
            <div className="grid grid-cols-3 gap-6">
              {/* Slide Structure */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="font-medium flex items-center gap-2">
                    <List className="h-4 w-4" />
                    Slide Structure
                  </div>
                  <button className="text-xs px-2 py-1 rounded border">Reorder</button>
                </div>
                <div className="space-y-2">
                  <div className="p-2 rounded border bg-blue-50 flex items-center justify-between">
                    <div className="text-sm">1. Introduction to Random Vectors</div>
                    <Edit3 className="h-4 w-4 text-blue-500" />
                  </div>
                  <div className="p-2 rounded border bg-blue-50 flex items-center justify-between">
                    <div className="text-sm">2. Covariance Matrix Definition</div>
                    <Edit3 className="h-4 w-4 text-blue-500" />
                  </div>
                  <div className="p-2 rounded border bg-white flex items-center justify-between">
                    <div className="text-sm">3. Properties & Examples</div>
                    <Edit3 className="h-4 w-4 text-slate-400" />
                  </div>
                  <div className="p-2 rounded border bg-white flex items-center justify-between">
                    <div className="text-sm">4. Interactive Visualization</div>
                    <Edit3 className="h-4 w-4 text-slate-400" />
                  </div>
                  <div className="p-2 rounded border bg-white flex items-center justify-between">
                    <div className="text-sm">5. Practice Problems</div>
                    <Edit3 className="h-4 w-4 text-slate-400" />
                  </div>
                  <button className="w-full px-3 py-2 rounded border flex items-center justify-center gap-1 text-sm">
                    <PlusCircle className="h-4 w-4" /> Add Slide
                  </button>
                </div>
              </div>

              {/* Current Slide Editor */}
              <div className="col-span-2 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="font-medium flex items-center gap-2">
                    <Layout className="h-4 w-4" />
                    Current Slide: Properties & Examples
                  </div>
                  <div className="flex gap-2">
                    <button className="text-xs px-2 py-1 rounded border">
                      <Play className="h-3 w-3" />
                    </button>
                    <button className="text-xs px-2 py-1 rounded border">Preview</button>
                    <button className="text-xs px-2 py-1 rounded border">Save</button>
                  </div>
                </div>
                <div className="h-[320px] bg-white rounded border p-4">
                  <div className="space-y-4">
                    <div className="text-xl font-bold">Properties of Covariance Matrices</div>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <div className="text-sm font-medium">Key Properties:</div>
                        <ul className="text-sm list-disc list-inside">
                          <li>Symmetry: Σ = Σᵀ</li>
                          <li>Positive Semi-definite</li>
                          <li>Diagonal elements ≥ 0</li>
                        </ul>
                      </div>
                      <div className="border rounded p-2 flex items-center justify-center">
                        <Image src="/cov.png" alt="Covariance" width={500} height={500} />
                      </div>
                    </div>
                  </div>
                </div>

                {/* Slide Tools */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="border rounded p-3 space-y-2">
                    <div className="font-medium text-sm">Quick Add</div>
                    <div className="flex flex-wrap gap-2">
                      <button className="text-xs px-2 py-1 rounded-full border">+ Text</button>
                      <button className="text-xs px-2 py-1 rounded-full border">+ Image</button>
                      <button className="text-xs px-2 py-1 rounded-full border">+ Equation</button>
                      <button className="text-xs px-2 py-1 rounded-full border">+ Matrix</button>
                      <button className="text-xs px-2 py-1 rounded-full border">+ Graph</button>
                    </div>
                  </div>
                  <div className="border rounded p-3 space-y-2">
                    <div className="font-medium text-sm">Layout</div>
                    <div className="flex gap-2">
                      <button className="p-2 rounded border">
                        <Columns className="h-4 w-4" />
                      </button>
                      <button className="p-2 rounded border">
                        <Layout className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Timeline */}
            <div className="border-t pt-4">
              <div className="flex items-center gap-2">
                <div className="p-2 rounded border bg-blue-50 flex-1">
                  Introduction
                  <div className="text-xs text-slate-500">5 slides</div>
                </div>
                <ArrowRight className="h-4 w-4 text-slate-400" />
                <div className="p-2 rounded border bg-blue-50 flex-1">
                  Definitions
                  <div className="text-xs text-slate-500">3 slides</div>
                </div>
                <ArrowRight className="h-4 w-4 text-slate-400" />
                <div className="p-2 rounded border bg-white flex-1">
                  Properties
                  <div className="text-xs text-slate-500">4 slides</div>
                </div>
                <ArrowRight className="h-4 w-4 text-slate-400" />
                <div className="p-2 rounded border bg-white flex-1">
                  Examples
                  <div className="text-xs text-slate-500">3 slides</div>
                </div>
                <ArrowRight className="h-4 w-4 text-slate-400" />
                <div className="p-2 rounded border bg-white flex-1">
                  Practice
                  <div className="text-xs text-slate-500">2 slides</div>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </main>
  );
}