import React from 'react'

interface Props {
    distribution: Record<string, number>
}

export function RiskChart({ distribution }: Props) {
    const total = Object.values(distribution).reduce((a, b) => a + b, 0) || 1

    const levels = [
        { key: 'safe', label: 'Safe', color: 'bg-green-500' },
        { key: 'low', label: 'Low', color: 'bg-blue-500' },
        { key: 'medium', label: 'Medium', color: 'bg-yellow-500' },
        { key: 'high', label: 'High', color: 'bg-orange-500' },
        { key: 'critical', label: 'Critical', color: 'bg-red-500' },
    ]

    return (
        <div className="bg-zinc-900 rounded-lg border border-zinc-800 p-6">
            <h3 className="text-lg font-semibold mb-4">Risk Distribution</h3>
            <div className="space-y-3">
                {levels.map(level => {
                    const count = distribution[level.key] || 0
                    const pct = total > 0 ? (count / total) * 100 : 0
                    return (
                        <div key={level.key} className="flex items-center gap-3">
                            <span className="text-xs text-zinc-400 w-16">{level.label}</span>
                            <div className="flex-1 h-6 bg-zinc-800 rounded overflow-hidden">
                                <div
                                    className={`h-full ${level.color} rounded transition-all duration-500`}
                                    style={{ width: `${pct}%` }}
                                />
                            </div>
                            <span className="text-xs text-zinc-400 w-12 text-right">{count}</span>
                        </div>
                    )
                })}
            </div>
        </div>
    )
}
