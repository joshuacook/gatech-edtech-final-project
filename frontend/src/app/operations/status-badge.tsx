import React from 'react'
import { Badge } from "@/components/ui/badge"

interface StatusBadgeProps {
status: string
className?: string
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
    case 'active':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100'
    case 'draft':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-100'
    case 'archived':
    case 'deprecated':
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-100'
    case 'evaluation':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100'
    default:
        return 'bg-gray-100 text-gray-800'
    }
}

return (
    <Badge 
    variant="secondary" 
    className={`${getStatusColor(status)} ${className || ''}`}
    >
    {status}
    </Badge>
)
}