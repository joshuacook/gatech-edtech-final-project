// src/app/lessons/page.tsx
import React from 'react';
import { BookOpen, PlusCircle, Clock, Target, List, CheckSquare, ArrowRight, AlertCircle } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function LessonsPage() {
  return (
    <main className="container mx-auto p-8">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-4xl">
            <BookOpen className="h-5 w-5" />
            Lesson Plan: Random Vectors & Covariance
          </CardTitle>
          <CardDescription className="text-lg">Week 3, Class 1: Properties of Random Vectors and Their Transformations</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {/* Prerequisites Alert */}
            <div className="bg-blue-50 p-3 rounded-lg flex items-start gap-2">
              <AlertCircle className="h-5 w-5 text-blue-500 mt-0.5" />
              <div className="text-sm">
                <div className="font-medium text-blue-700">Prerequisites Check</div>
                <div className="text-blue-600">Ensure students have completed the vector space operations and probability basics modules</div>
              </div>
            </div>

            {/* Main Content Grid */}
            <div className="grid grid-cols-3 gap-4">
              {/* Learning Objectives Section */}
              <div className="space-y-3">
                <div className="font-medium flex items-center gap-2">
                  <Target className="h-4 w-4" />
                  Learning Objectives
                </div>
                <div className="space-y-2">
                  <div className="p-3 rounded border bg-white">
                    <div className="text-sm font-medium">Compute and interpret covariance matrices</div>
                    <div className="text-xs text-slate-500">Bloom's: Analysis</div>
                  </div>
                  <div className="p-3 rounded border bg-white">
                    <div className="text-sm font-medium">Transform random vectors</div>
                    <div className="text-xs text-slate-500">Bloom's: Application</div>
                  </div>
                  <div className="p-3 rounded border bg-white">
                    <div className="text-sm font-medium">Analyze correlation matrices</div>
                    <div className="text-xs text-slate-500">Bloom's: Analysis</div>
                  </div>
                  <button className="w-full px-3 py-2 rounded border flex items-center justify-center gap-1 text-sm">
                    <PlusCircle className="h-4 w-4" /> Add Objective
                  </button>
                </div>
              </div>

              {/* Activities Section */}
              <div className="space-y-3">
                <div className="font-medium flex items-center gap-2">
                  <List className="h-4 w-4" />
                  Learning Activities
                </div>
                <div className="space-y-2">
                  <div className="p-3 rounded border bg-white">
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="text-sm font-medium">Review of Random Vectors</div>
                        <div className="text-xs text-slate-500">Interactive discussion</div>
                      </div>
                      <div className="flex items-center gap-1 text-xs text-slate-500">
                        <Clock className="h-3 w-3" /> 15m
                      </div>
                    </div>
                  </div>
                  <div className="p-3 rounded border bg-white">
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="text-sm font-medium">Covariance Matrix Lab</div>
                        <div className="text-xs text-slate-500">Hands-on practice</div>
                      </div>
                      <div className="flex items-center gap-1 text-xs text-slate-500">
                        <Clock className="h-3 w-3" /> 30m
                      </div>
                    </div>
                  </div>
                  <div className="p-3 rounded border bg-white">
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="text-sm font-medium">Cross-Correlation Analysis</div>
                        <div className="text-xs text-slate-500">Signal processing example</div>
                      </div>
                      <div className="flex items-center gap-1 text-xs text-slate-500">
                        <Clock className="h-3 w-3" /> 25m
                      </div>
                    </div>
                  </div>
                  <button className="w-full px-3 py-2 rounded border flex items-center justify-center gap-1 text-sm">
                    <PlusCircle className="h-4 w-4" /> Add Activity
                  </button>
                </div>
              </div>

              {/* Checks Section */}
              <div className="space-y-3">
                <div className="font-medium flex items-center gap-2">
                  <CheckSquare className="h-4 w-4" />
                  Checks for Understanding
                </div>
                <div className="space-y-2">
                  <div className="p-3 rounded border bg-white">
                    <div className="text-sm font-medium">Covariance Properties Quiz</div>
                    <div className="text-xs text-slate-500">Mathematical properties</div>
                    <div className="mt-2 text-xs">4 proof-based questions</div>
                  </div>
                  <div className="p-3 rounded border bg-white">
                    <div className="text-sm font-medium">Transform Exercise</div>
                    <div className="text-xs text-slate-500">Vector transformations</div>
                    <div className="mt-2 text-xs">2 computational problems</div>
                  </div>
                  <div className="p-3 rounded border bg-white">
                    <div className="text-sm font-medium">Signal Analysis</div>
                    <div className="text-xs text-slate-500">Engineering application</div>
                    <div className="mt-2 text-xs">Group discussion</div>
                  </div>
                  <button className="w-full px-3 py-2 rounded border flex items-center justify-center gap-1 text-sm">
                    <PlusCircle className="h-4 w-4" /> Add Check
                  </button>
                </div>
              </div>
            </div>

            {/* Sequence Timeline */}
            <div className="p-4 bg-slate-50 rounded-lg mt-6">
              <div className="font-medium mb-3">Session Sequence</div>
              <div className="flex items-center gap-2">
                <div className="p-2 bg-white rounded border flex-1">
                  <div className="text-sm font-medium">Theory Review</div>
                  <div className="text-xs text-slate-500">15m - Random vectors</div>
                </div>
                <ArrowRight className="h-4 w-4 text-slate-400" />
                <div className="p-2 bg-white rounded border flex-1">
                  <div className="text-sm font-medium">Practical Lab</div>
                  <div className="text-xs text-slate-500">30m - Covariance</div>
                </div>
                <ArrowRight className="h-4 w-4 text-slate-400" />
                <div className="p-2 bg-white rounded border flex-1">
                  <div className="text-sm font-medium">Application</div>
                  <div className="text-xs text-slate-500">25m - Correlation</div>
                </div>
                <ArrowRight className="h-4 w-4 text-slate-400" />
                <div className="p-2 bg-white rounded border flex-1">
                  <div className="text-sm font-medium">Assessment</div>
                  <div className="text-xs text-slate-500">10m - Quiz</div>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </main>
  );
}