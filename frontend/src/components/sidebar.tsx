// components/sidebar.tsx
'use client'

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { 
  Home, 
  Book, 
  Link as LinkIcon, 
  Cog, 
  FileText,
  FolderOpen,
  LayoutDashboard,
  Pencil,
  GraduationCap,
} from "lucide-react"

const routes = [
  {
    name: "Home",
    icon: Home,
    href: "/",
  },
  {
    name: "Library",
    icon: FolderOpen,
    href: "/library",
  },
  {
    name: "Concepts",
    icon: Book,
    href: "/concepts",
  },
  {
    name: "Relationships",
    icon: LinkIcon,
    href: "/relationships",
  },
  // {
  //   name: "Operations",
  //   icon: Cog,
  //   href: "/operations",
  // },
  {
    name: "Syllabus",
    icon: GraduationCap,
    href: "/syllabus",
  },
  {
    name: "Planning",
    icon: Pencil,
    href: "/planning",
  }
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <div className="border-r bg-background w-64 relative">
      <div className="p-6">
        <div className="flex items-center gap-2 font-semibold">
          <LayoutDashboard className="h-6 w-6" />
          <span>Knowledge Base</span>
        </div>
      </div>
      
      <ScrollArea className="h-[calc(100vh-5rem)] pb-10">
        <div className="space-y-1 p-4">
          {routes.map((route) => (
            <Button
              key={route.href}
              variant={pathname === route.href ? "secondary" : "ghost"}
              className={cn(
                "w-full justify-start gap-2",
                pathname === route.href && "bg-secondary"
              )}
              asChild
            >
              <Link href={route.href}>
                <route.icon className="h-4 w-4" />
                {route.name}
              </Link>
            </Button>
          ))}
        </div>
      </ScrollArea>
    </div>
  )
}