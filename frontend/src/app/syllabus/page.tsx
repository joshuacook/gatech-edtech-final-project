import React from 'react';
import { BookOpen, Calendar, Clock, Users, Target, Book, ChevronRight, BarChart, AlertCircle } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function ClassroomPage() {
  return (
    <main className="container mx-auto p-8">
      <Card>
        <CardHeader>
          <div className="flex justify-between items-start">
            <div>
              <CardTitle className="flex items-center gap-2 mb-2">
                <BookOpen className="h-5 w-5" />
                Linear Algebra and Estimation Theory
              </CardTitle>
              <CardDescription>Communications Systems Engineering Certificate (CSEC)</CardDescription>
            </div>
            <div className="flex gap-4 text-sm text-slate-500">
              <div className="flex items-center gap-1">
                <Calendar className="h-4 w-4" />
                January 7, 2025
              </div>
              <div className="flex items-center gap-1">
                <Clock className="h-4 w-4" />
                30 Hours
              </div>
              <div className="flex items-center gap-1">
                <Users className="h-4 w-4" />
                NGC Program
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {/* Course Overview */}
            <div className="grid grid-cols-3 gap-4">
              <div className="col-span-2 space-y-4">
                <div className="prose max-w-none">
                  <p className="text-sm text-slate-600">
                    This course covers foundational concepts in linear algebra as they relate to estimation techniques. 
                    Through interactive exercises and real-world examples, students will gain practical insights into 
                    analytical frameworks critical to engineering and applied sciences.
                  </p>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 bg-slate-50 rounded-lg">
                    <div className="font-medium mb-2 flex items-center gap-2">
                      <Target className="h-4 w-4" />
                      Course Benefits
                    </div>
                    <ul className="text-sm space-y-1 text-slate-600">
                      <li>• Master vector spaces and linear transformations</li>
                      <li>• Apply random vectors and covariance matrices</li>
                      <li>• Develop analytical estimation skills</li>
                      <li>• Design linear estimators using MMSE</li>
                    </ul>
                  </div>
                  <div className="p-4 bg-slate-50 rounded-lg">
                    <div className="font-medium mb-2 flex items-center gap-2">
                      <Book className="h-4 w-4" />
                      Format
                    </div>
                    <ul className="text-sm space-y-1 text-slate-600">
                      <li>• Live-remote lectures twice weekly</li>
                      <li>• 90-minute sessions</li>
                      <li>• Interactive problem-solving</li>
                      <li>• Real-world applications focus</li>
                    </ul>
                  </div>
                </div>
              </div>
              <div className="space-y-4">
                <div className="p-4 bg-blue-50 rounded-lg">
                  <div className="font-medium mb-2">Course Progress</div>
                  <div className="space-y-2">
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Overall Completion</span>
                        <span>0%</span>
                      </div>
                      <div className="w-full h-2 bg-blue-100 rounded">
                        <div className="w-0 h-full bg-blue-500 rounded"></div>
                      </div>
                    </div>
                    <div className="text-xs text-blue-600">
                      Course starts January 7, 2025
                    </div>
                  </div>
                </div>
                <button className="w-full py-2 px-4 bg-blue-500 text-white rounded">
                  Enter Classroom
                </button>
              </div>
            </div>

            {/* Course Timeline */}
            <div className="border-t pt-6">
              <div className="font-medium mb-4">Course Schedule</div>
              <div className="grid gap-4">
                {/* Week 1 */}
                <div className="border rounded-lg">
                  <div className="p-3 border-b bg-slate-50 font-medium">Week 1: Introduction to Random Processes</div>
                  <div className="p-4 space-y-3">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="flex items-center gap-3">
                        <Book className="h-4 w-4" />
                        <div>
                          <div className="text-sm font-medium">Lecture 1: Random Processes Overview</div>
                          <div className="text-xs text-slate-500">Definition and applications</div>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <Book className="h-4 w-4" />
                        <div>
                          <div className="text-sm font-medium">Lecture 2: Estimation Fundamentals</div>
                          <div className="text-xs text-slate-500">Key estimation techniques</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Week 2 */}
                <div className="border rounded-lg">
                  <div className="p-3 border-b bg-slate-50 font-medium">Week 2: Random Vectors and Matrices</div>
                  <div className="p-4 space-y-3">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="flex items-center gap-3">
                        <Book className="h-4 w-4" />
                        <div>
                          <div className="text-sm font-medium">Lecture 3: Random Vector Properties</div>
                          <div className="text-xs text-slate-500">Mean vectors and properties</div>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <Book className="h-4 w-4" />
                        <div>
                          <div className="text-sm font-medium">Lecture 4: Matrix Operations</div>
                          <div className="text-xs text-slate-500">Vector space operations</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Week 3 */}
                <div className="border rounded-lg">
                  <div className="p-3 border-b bg-slate-50 font-medium">Week 3: Covariance and Correlation</div>
                  <div className="p-4 space-y-3">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="flex items-center gap-3">
                        <Book className="h-4 w-4" />
                        <div>
                          <div className="text-sm font-medium">Lecture 5: Covariance Matrices</div>
                          <div className="text-xs text-slate-500">Properties and applications</div>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <Book className="h-4 w-4" />
                        <div>
                          <div className="text-sm font-medium">Lecture 6: Correlation Analysis</div>
                          <div className="text-xs text-slate-500">Cross-correlation techniques</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Collapsed Future Weeks */}
                <button className="flex items-center justify-center gap-2 text-sm text-blue-500 py-2 border rounded">
                  Show 7 more weeks
                  <ChevronRight className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </main>
  );
}