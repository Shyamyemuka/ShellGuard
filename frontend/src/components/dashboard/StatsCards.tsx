import React from 'react'
import { Terminal, Shield, RefreshCw, Clock } from 'lucide-react'

interface Props {
    stats: any
}

export function StatsCards({ stats }: Props) {
    const cards = [
        {
            label: 'Total Commands',
            value: stats?.total_commands || 0,
            icon: Terminal,
            color: 'text-blue-400',
        },
        {
            label: 'Interceptions',
            value: stats?.total_interceptions || 0,
            icon: Shield,
            color: 'text-yellow-400',
        },
        {
            label: 'Safe Swap Rate',
            value: `${stats?.safe_swap_rate?.toFixed(0) || 0}%`,
            icon: RefreshCw,
            color: 'text-green-400',
        },
        {
            label: 'Avg Latency',
            value: `${stats?.avg_analysis_latency_ms || 0}ms`,
            icon: Clock,
            color: 'text-purple-400',
        },
    ]

    return (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {cards.map((card, i) => (
                <div key={i} className="bg-zinc-900 rounded-lg border border-zinc-800 p-6">
                    <div className="flex items-center gap-2 mb-2">
                        <card.icon className={`w-4 h-4 ${card.color}`} />
                        <span className="text-xs text-zinc-400">{card.label}</span>
                    </div>
                    <div className="text-3xl font-bold">{card.value}</div>
                </div>
            ))}
        </div>
    )
}
