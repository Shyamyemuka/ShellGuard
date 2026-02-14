import React from 'react'
import type { HistoryEntry } from '@/types/history'

interface Props {
    entries: HistoryEntry[]
}

export function HistoryPanel({ entries }: Props) {
    const getStatusIcon = (action: string) => {
        switch (action) {
            case 'executed': return '✅'
            case 'approved': return '⚠️'
            case 'safe_swap': return '🔄'
            case 'cancelled': return '❌'
            case 'blocked': return '🔴'
            default: return '⚪'
        }
    }

    const getTimeAgo = (timestamp: string) => {
        const diff = Date.now() - new Date(timestamp).getTime()
        const seconds = Math.floor(diff / 1000)
        if (seconds < 60) return `${seconds}s ago`
        const minutes = Math.floor(seconds / 60)
        if (minutes < 60) return `${minutes}m ago`
        const hours = Math.floor(minutes / 60)
        return `${hours}h ago`
    }

    if (entries.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-zinc-500">
                <div className="text-4xl mb-3">📋</div>
                <p className="text-sm">No commands yet</p>
                <p className="text-xs mt-1">Commands will appear here</p>
            </div>
        )
    }

    return (
        <div className="space-y-1">
            <h3 className="text-sm font-semibold text-zinc-300 mb-3">Recent Commands</h3>
            {entries.map((entry, i) => (
                <div
                    key={i}
                    className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-zinc-900/50 transition-colors animate-slide-in"
                    title={entry.command}
                >
                    <span className="text-base shrink-0">{getStatusIcon(entry.action)}</span>
                    <div className="flex-1 min-w-0">
                        <div className="font-mono text-xs text-zinc-200 truncate">
                            {entry.command}
                        </div>
                        <div className="text-[10px] text-zinc-500">
                            {entry.timestamp ? getTimeAgo(entry.timestamp) : 'just now'}
                        </div>
                    </div>
                    {entry.risk_level && entry.risk_level !== 'safe' && (
                        <span className={`text-[10px] px-1.5 py-0.5 rounded font-medium shrink-0 ${entry.risk_level === 'critical' ? 'bg-red-500/20 text-red-400' :
                                entry.risk_level === 'high' ? 'bg-orange-500/20 text-orange-400' :
                                    entry.risk_level === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                                        'bg-blue-500/20 text-blue-400'
                            }`}>
                            {entry.risk_level}
                        </span>
                    )}
                </div>
            ))}
        </div>
    )
}
