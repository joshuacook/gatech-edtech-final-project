// app/page.tsx
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Brain, Book, Link, Cog, FileText, FolderOpen } from 'lucide-react'

const components = [
  {
    icon: <Book className="w-8 h-8" />,
    title: "Concepts Management",
    description: "Define and organize organizational knowledge",
    href: "/concepts",
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
    href: "/relationships",
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
    href: "/operations",
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
    href: "/upload",
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
    href: "/files",
    features: [
      "File organization",
      "Quick preview",
      "Processing status"
    ]
  }
]

export default function HomePage() {
  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <div className="flex items-center space-x-4">
          <Brain className="w-12 h-12" />
          <h1 className="text-4xl font-bold">Knowledge Management</h1>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {components.map((component) => (
            <a key={component.title} href={component.href}>
              <Card className="h-full hover:shadow-lg transition-shadow cursor-pointer">
                <CardHeader className="flex flex-row items-center space-x-4">
                  <div className="p-2 bg-primary/10 rounded-lg">
                    {component.icon}
                  </div>
                  <div>
                    <CardTitle>{component.title}</CardTitle>
                    <p className="text-sm text-muted-foreground">
                      {component.description}
                    </p>
                  </div>
                </CardHeader>
                <CardContent>
                  <ul className="list-disc list-inside text-sm space-y-2">
                    {component.features.map((feature, index) => (
                      <li key={index} className="text-muted-foreground">
                        {feature}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            </a>
          ))}
        </div>
      </div>
    </div>
  )
}