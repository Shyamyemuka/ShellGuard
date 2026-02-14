import React from 'react'
import Link from 'next/link'
import { Shield, AlertTriangle, RefreshCw, BarChart3 } from 'lucide-react'
import type { SessionStats } from '@/types/terminal'

interface Props {
    stats: SessionStats
    isConnected: boolean
}

export function StatsBar({ stats, isConnected }: Props) {
    return (
        <header className="flex items-center justify-between px-4 py-2 bg-zinc-900 border-b border-zinc-800">
            {/* Brand */}
            <div className="flex items-center gap-2">
                <Shield className="w-5 h-5 text-green-500" />
                <span className="font-bold text-sm">ShellGuard</span>
                <span className="text-xs text-zinc-500">AI Terminal Safety Copilot</span>
                {/* Connection Status */}
                <div className={`w-2 h-2 rounded-full ml-2 ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
            </div>

            {/* Stats */}
            <div className="flex items-center gap-4 text-xs">
                <div className="flex items-center gap-1.5">
                    <span className="text-zinc-500">Cmds:</span>
                    <span className="font-mono font-bold">{stats.total_commands}</span>
                </div>
                <div className="flex items-center gap-1.5">
                    <AlertTriangle className="w-3 h-3 text-yellow-500" />
                    <span className="font-mono font-bold">{stats.warnings_issued + stats.blocked}</span>
                </div>
                <div className="flex items-center gap-1.5">
                    <RefreshCw className="w-3 h-3 text-green-500" />
                    <span className="font-mono font-bold">{stats.safe_swaps}</span>
                </div>
                <div className="flex items-center gap-1.5">
                    <span className="text-zinc-500">Swap Rate:</span>
                    <span className="font-mono font-bold text-green-400">{stats.safe_swap_rate.toFixed(0)}%</span>
                </div>

                {/* Dashboard Link */}
                <Link
                    href="/dashboard"
                    className="flex items-center gap-1 px-2 py-1 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 rounded transition-colors"
                >
                    <BarChart3 className="w-3 h-3" />
                    Dashboard
                </Link>
            </div>
        </header>
    )
}
