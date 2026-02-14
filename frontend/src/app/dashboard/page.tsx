'use client'

import React, { useEffect, useState } from 'react'
import Link from 'next/link'
import { StatsCards } from '@/components/dashboard/StatsCards'
import { RiskChart } from '@/components/dashboard/RiskChart'
import { TimelineChart } from '@/components/dashboard/TimelineChart'
import { TopDangerous } from '@/components/dashboard/TopDangerous'
import { Shield, Terminal } from 'lucide-react'
import { fetchStats, fetchTopDangerous, fetchHistory } from '@/lib/api'

export default function DashboardPage() {
    const [stats, setStats] = useState<any>(null)
    const [topDangerous, setTopDangerous] = useState<any[]>([])
    const [recentInterceptions, setRecentInterceptions] = useState<any[]>([])

    useEffect(() => {
        const load = async () => {
            try {
                const [s, td, h] = await Promise.all([
                    fetchStats(),
                    fetchTopDangerous(),
                    fetchHistory({ limit: 20 }),
                ])
                setStats(s)
                setTopDangerous(td)
                setRecentInterceptions(h.items?.filter((i: any) => i.action !== 'executed') || [])
            } catch (e) {
                console.error('Dashboard load error:', e)
            }
        }
        load()
        const interval = setInterval(load, 5000)
        return () => clearInterval(interval)
    }, [])

    return (
        <div className="min-h-screen bg-zinc-950">
            {/* Header */}
            <header className="border-b border-zinc-800 px-6 py-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <Shield className="w-6 h-6 text-green-500" />
                    <span className="text-lg font-bold">ShellGuard</span>
                </div>
                <nav className="flex gap-4">
                    <Link
                        href="/"
                        className="flex items-center gap-2 px-3 py-1.5 text-sm text-zinc-400 hover:text-zinc-200 transition-colors"
                    >
                        <Terminal className="w-4 h-4" />
                        Terminal
                    </Link>
                    <span className="flex items-center gap-2 px-3 py-1.5 text-sm text-green-400 font-medium">
                        Dashboard
                    </span>
                </nav>
            </header>

            <main className="max-w-7xl mx-auto p-6 space-y-6">
                {/* Stats Cards */}
                <StatsCards stats={stats} />

                {/* Charts Row */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <RiskChart distribution={stats?.risk_distribution || {}} />
                    <TimelineChart />
                </div>

                {/* Top Dangerous */}
                <TopDangerous commands={topDangerous} />

                {/* Recent Interceptions */}
                <div className="bg-zinc-900 rounded-lg border border-zinc-800 p-6">
                    <h3 className="text-lg font-semibold mb-4">Recent Interceptions</h3>
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                            <thead>
                                <tr className="border-b border-zinc-800 text-zinc-400">
                                    <th className="text-left py-2 px-3">Time</th>
                                    <th className="text-left py-2 px-3">Command</th>
                                    <th className="text-left py-2 px-3">Risk</th>
                                    <th className="text-left py-2 px-3">Action</th>
                                    <th className="text-left py-2 px-3">Latency</th>
                                </tr>
                            </thead>
                            <tbody>
                                {recentInterceptions.map((entry: any, i: number) => (
                                    <tr key={i} className="border-b border-zinc-800/50 hover:bg-zinc-800/30">
                                        <td className="py-2 px-3 text-zinc-400">{entry.timestamp?.slice(11, 19)}</td>
                                        <td className="py-2 px-3 font-mono text-sm">{entry.command?.slice(0, 40)}</td>
                                        <td className="py-2 px-3">
                                            <span className={`px-2 py-0.5 rounded text-xs font-medium ${entry.risk_level === 'critical' ? 'bg-red-500/20 text-red-400' :
                                                    entry.risk_level === 'high' ? 'bg-orange-500/20 text-orange-400' :
                                                        entry.risk_level === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                                                            'bg-blue-500/20 text-blue-400'
                                                }`}>
                                                {entry.risk_level}
                                            </span>
                                        </td>
                                        <td className="py-2 px-3">
                                            <span className={`text-xs ${entry.action === 'safe_swap' ? 'text-green-400' :
                                                    entry.action === 'cancelled' ? 'text-zinc-400' :
                                                        entry.action === 'blocked' ? 'text-red-400' :
                                                            entry.action === 'approved' ? 'text-yellow-400' :
                                                                'text-zinc-500'
                                                }`}>
                                                {entry.action === 'safe_swap' ? '🔄 Safe Swap' :
                                                    entry.action === 'cancelled' ? '❌ Cancelled' :
                                                        entry.action === 'blocked' ? '🚫 Blocked' :
                                                            entry.action === 'approved' ? '⚠️ Approved' :
                                                                entry.action}
                                            </span>
                                        </td>
                                        <td className="py-2 px-3 text-zinc-400">{entry.analysis_latency_ms}ms</td>
                                    </tr>
                                ))}
                                {recentInterceptions.length === 0 && (
                                    <tr>
                                        <td colSpan={5} className="py-8 text-center text-zinc-500">
                                            No interceptions yet
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </main>
        </div>
    )
}
