'use client'

import React, { useState, useCallback } from 'react'
import { ShellTerminal } from '@/components/terminal/ShellTerminal'
import { TerminalHeader } from '@/components/terminal/TerminalHeader'
import { WarningOverlay } from '@/components/warning/WarningOverlay'
import { AnalysisPanel } from '@/components/panels/AnalysisPanel'
import { HistoryPanel } from '@/components/panels/HistoryPanel'
import { StatsBar } from '@/components/panels/StatsBar'
import { useTerminalSocket } from '@/hooks/useTerminalSocket'
import type { AnalysisResult } from '@/types/analysis'
import type { HistoryEntry } from '@/types/history'
import type { SessionStats } from '@/types/terminal'

export default function TerminalPage() {
    const [activePanel, setActivePanel] = useState<'analysis' | 'history'>('analysis')
    const [lastAnalysis, setLastAnalysis] = useState<AnalysisResult | null>(null)
    const [history, setHistory] = useState<HistoryEntry[]>([])
    const [stats, setStats] = useState<SessionStats>({
        total_commands: 0,
        safe_commands: 0,
        warnings_issued: 0,
        approved_risky: 0,
        safe_swaps: 0,
        cancelled: 0,
        blocked: 0,
        interception_rate: 0,
        safe_swap_rate: 0,
    })

    const handleWarning = useCallback((command: string, analysis: AnalysisResult) => {
        setLastAnalysis(analysis)
    }, [])

    const handleHistoryUpdate = useCallback((entry: HistoryEntry) => {
        setHistory(prev => [entry, ...prev].slice(0, 100))
    }, [])

    const handleStatsUpdate = useCallback((newStats: SessionStats) => {
        setStats(newStats)
    }, [])

    const {
        terminalRef,
        isConnected,
        isAnalyzing,
        analyzingCommand,
        warning,
        blocked,
        sendApprove,
        sendCancel,
        sendUseAlternative,
        writeToTerminal,
    } = useTerminalSocket({
        onWarning: handleWarning,
        onStatsUpdate: handleStatsUpdate,
        onHistoryUpdate: handleHistoryUpdate,
    })

    return (
        <div className="flex flex-col h-screen">
            {/* Header Stats Bar */}
            <StatsBar stats={stats} isConnected={isConnected} />

            {/* Main Content */}
            <div className="flex flex-1 overflow-hidden">
                {/* Terminal Area - 60% */}
                <div className="flex-[3] flex flex-col relative border-r border-zinc-800">
                    <TerminalHeader />
                    <div className="flex-1 relative">
                        <ShellTerminal
                            ref={terminalRef}
                            writeToTerminal={writeToTerminal}
                        />

                        {/* Analyzing Indicator */}
                        {isAnalyzing && (
                            <div className="absolute bottom-4 left-4 right-4">
                                <div className="bg-yellow-950/90 border border-yellow-800 rounded-lg px-4 py-3 flex items-center gap-3 analyzing-pulse">
                                    <div className="w-4 h-4 rounded-full bg-yellow-500 animate-pulse" />
                                    <span className="text-yellow-200 text-sm">
                                        Analyzing command safety: <code className="font-mono text-yellow-100">{analyzingCommand}</code>
                                    </span>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Warning Overlay */}
                    {warning && (
                        <WarningOverlay
                            command={warning.command}
                            analysis={warning.analysis}
                            onApprove={sendApprove}
                            onUseAlternative={sendUseAlternative}
                            onCancel={sendCancel}
                        />
                    )}

                    {/* Blocked Overlay */}
                    {blocked && (
                        <WarningOverlay
                            command={blocked.command}
                            analysis={{
                                risk_level: 'critical',
                                risk_score: 100,
                                allow: false,
                                title: 'Command Blocked',
                                explanation: blocked.message,
                                consequences: ['System destruction', 'Data loss', 'Irreversible damage'],
                                safer_alternative: null,
                                alternative_explanation: null,
                                data_loss_risk: 100,
                                service_impact_risk: 100,
                                reversibility: 0,
                                requires_sudo: false,
                                affected_scope: 'Entire system',
                                command_breakdown: [],
                                analysis_source: 'hard_block',
                                model_used: null,
                                tokens_used: 0,
                                analysis_latency_ms: 0,
                            }}
                            isBlocked={true}
                            onCancel={sendCancel}
                            onApprove={() => { }}
                            onUseAlternative={() => { }}
                        />
                    )}
                </div>

                {/* Side Panel - 40% */}
                <div className="flex-[2] flex flex-col bg-zinc-950">
                    {/* Panel Tabs */}
                    <div className="flex border-b border-zinc-800">
                        <button
                            onClick={() => setActivePanel('analysis')}
                            className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${activePanel === 'analysis'
                                    ? 'text-green-400 border-b-2 border-green-400 bg-zinc-900/50'
                                    : 'text-zinc-400 hover:text-zinc-300'
                                }`}
                        >
                            Analysis
                        </button>
                        <button
                            onClick={() => setActivePanel('history')}
                            className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${activePanel === 'history'
                                    ? 'text-green-400 border-b-2 border-green-400 bg-zinc-900/50'
                                    : 'text-zinc-400 hover:text-zinc-300'
                                }`}
                        >
                            History
                        </button>
                    </div>

                    {/* Panel Content */}
                    <div className="flex-1 overflow-auto p-4">
                        {activePanel === 'analysis' && (
                            <AnalysisPanel analysis={lastAnalysis} />
                        )}
                        {activePanel === 'history' && (
                            <HistoryPanel entries={history} />
                        )}
                    </div>
                </div>
            </div>
        </div>
    )
}
