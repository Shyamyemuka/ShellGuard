import React from 'react'

interface Props {
    level: string
    score?: number
}

export function Badge({ level, score }: Props) {
    const styles: Record<string, string> = {
        critical: 'bg-red-500/20 text-red-400 border-red-500/30',
        high: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
        medium: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
        low: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
        safe: 'bg-green-500/20 text-green-400 border-green-500/30',
    }

    return (
        <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold border ${styles[level] || styles.medium
            }`}>
            {level.toUpperCase()}
            {score !== undefined && <span className="opacity-70">({score})</span>}
        </span>
    )
}
