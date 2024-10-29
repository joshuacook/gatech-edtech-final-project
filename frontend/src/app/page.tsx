import React from 'react';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { Brain, Book, Link, Cog, FileText, FolderOpen } from 'lucide-react';

const HomePage = () => {
  const stats = [
    { label: "Total Concepts", value: "25", delta: "+2" },
    { label: "Relationships", value: "43", delta: "+5" },
    { label: "Implementations", value: "12", delta: "+1" }
  ];

  const components = [
    {
      icon: <Book className="w-8 h-8" />,
      title: "Concepts Management",
      description: "Define and organize organizational knowledge",
      features: [
        "Manage definitions and citations",
        "Track understanding levels",
        "Maintain knowledge hierarchy"
      ]
    },
    {
      icon: <Link className="w-8 h-8" />,
      title: "Relationships Management",
      description: "Create and manage connections between concepts",
      features: [
        "Visual knowledge networks",
        "Relationship mapping",
        "Connection strength tracking"
      ]
    },
    {
      icon: <Cog className="w-8 h-8" />,
      title: "Operational Elements",
      description: "Implement concepts in practical contexts",
      features: [
        "Procedures documentation",
        "Tools integration",
        "Implementation validation"
      ]
    },
    {
      icon: <FileText className="w-8 h-8" />,
      title: "File Upload",
      description: "Upload and process documents",
      features: [
        "Multiple file formats",
        "Automatic processing",
        "Content extraction"
      ]
    },
    {
      icon: <FolderOpen className="w-8 h-8" />,
      title: "File Browser",
      description: "Browse and manage uploaded files",
      features: [
        "File organization",
        "Quick preview",
        "Processing status"
      ]
    }
  ];

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex items-center space-x-4">
          <Brain className="w-12 h-12" />
          <h1 className="text-4xl font-bold">Knowledge Management</h1>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {stats.map((stat, index) => (
            <Card key={index}>
              <CardContent className="p-6">
                <div className="text-2xl font-bold">{stat.value}</div>
                <div className="text-sm text-muted-foreground">{stat.label}</div>
                <div className="text-sm text-green-600">+{stat.delta} new</div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Main Components Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {components.map((component, index) => (
            <Card key={index} className="hover:shadow-lg transition-shadow">
              <CardHeader className="flex flex-row items-center space-x-4">
                <div className="p-2 bg-primary/10 rounded-lg">
                  {component.icon}
                </div>
                <div>
                  <h3 className="text-xl font-semibold">{component.title}</h3>
                  <p className="text-sm text-muted-foreground">
                    {component.description}
                  </p>
                </div>
              </CardHeader>
              <CardContent>
                <ul className="list-disc list-inside text-sm space-y-2">
                  {component.features.map((feature, featureIndex) => (
                    <li key={featureIndex}>{feature}</li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};

export default HomePage;