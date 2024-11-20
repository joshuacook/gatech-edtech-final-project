// app/page.tsx
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Book, Link, FileText, FolderOpen, Pencil, GraduationCap } from 'lucide-react'

const components = [
  {
    icon: <FolderOpen className="w-8 h-8" />,
    title: "Library",
    description: "Browse and manage uploaded files",
    href: "/library",
    features: [
      "Document organization",
      "Metadata extraction",
      "Content processing"
    ]
  },
  {
    icon: <Book className="w-8 h-8" />,
    title: "Concepts Management",
    description: "Define and organize organizational knowledge",
    href: "/concepts",
    features: [
      "Concept definitions",
      "Understanding levels",
      "Concept refinement"
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
      "Concept hierarchies"
    ]
  },
  {
    icon: <GraduationCap className="w-8 h-8" />,
    title: "Syllabus",
    description: "Course structure and curriculum planning",
    href: "/syllabus",
    features: [
      "Course objectives",
      "Weekly schedule",
      "Learning outcomes"
    ]
  },
  {
    icon: <Pencil className="w-8 h-8" />,
    title: "Planning",
    description: "Lesson planning and materials preparation",
    href: "/planning",
    features: [
      "Lesson objectives",
      "Activity planning",
      "Resource preparation"
    ]
  }
];

export default function HomePage() {
  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <h1 className="text-4xl font-bold">Knowledge Management</h1>

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
  );
}