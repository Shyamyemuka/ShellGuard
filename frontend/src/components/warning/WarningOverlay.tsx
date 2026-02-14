'use client'

import React, { useEffect, useCallback } from 'react'
import { RiskBar } from './RiskBar'
import { ConsequenceList } from './ConsequenceList'
import { SafeAlternative } from './SafeAlternative'
import { Badge } from '@/components/shared/Badge'
import { Shield, AlertTriangle, XOctagon } from 'lucide-react'
import type { AnalysisResult } from '@/types/analysis'

interface Props {
    command: string
    analysis: AnalysisResult
    isBlocked?: boolean
    onApprove: () => void
    onUseAlternative: (command: string) => void
    onCancel: () => void
}

export function WarningOverlay({
    command,
    analysis,
    isBlocked = false,
    onApprove,
    onUseAlternative,
    onCancel,
}: Props) {
    const handleKeyDown = useCallback((e: KeyboardEvent) => {
        if (e.key === 'Escape') {
            onCancel()
        } else if (e.key === 'Enter' && !isBlocked) {
            onApprove()
        } else if (e.key === 's' && analysis.safer_alternative && !isBlocked) {
            onUseAlternative(analysis.safer_alternative)
        }
    }, [onApprove, onCancel, onUseAlternative, analysis.safer_alternative, isBlocked])

    useEffect(() => {
        window.addEventListener('keydown', handleKeyDown)
        return () => window.removeEventListener('keydown', handleKeyDown)
    }, [handleKeyDown])

    const riskColors = {
        critical: { bg: 'bg-red-950/95', border: 'border-red-800', text: 'text-red-400' },
        high: { bg: 'bg-orange-950/95', border: 'border-orange-800', text: 'text-orange-400' },
        medium: { bg: 'bg-yellow-950/95', border: 'border-yellow-800', text: 'text-yellow-400' },
        low: { bg: 'bg-blue-950/95', border: 'border-blue-800', text: 'text-blue-400' },
    }

    // Hard-blocked commands get special red treatment
    const colors = isBlocked
        ? { bg: 'bg-red-950/98', border: 'border-red-600', text: 'text-red-300' }
        : (riskColors[analysis.risk_level as keyof typeof riskColors] || riskColors.medium)

    return (
        <div className="absolute inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm warning-overlay-enter">
            <div className={`w-full max-w-lg mx-4 rounded-xl ${colors.bg} ${colors.border} ${isBlocked ? 'border-2 animate-pulse' : 'border'} shadow-2xl overflow-hidden`}>
                {/* Header */}
                <div className="flex items-center gap-3 px-6 py-4 border-b border-zinc-800/50">
                    {isBlocked ? (
                        <XOctagon className="w-6 h-6 text-red-500" />
                    ) : (
                        <Shield className="w-6 h-6 text-green-500" />
                    )}
                    <span className="font-bold text-lg">
                        {isBlocked ? 'ShellGuard — BLOCKED' : 'ShellGuard Warning'}
                    </span>
                    <div className="ml-auto">
                        {isBlocked ? (
                            <span className="px-3 py-1 bg-red-600 text-white text-xs font-bold uppercase rounded-full animate-pulse">
                                ⛔ BLOCKED
                            </span>
                        ) : (
                            <Badge level={analysis.risk_level} score={analysis.risk_score} />
                        )}
                    </div>
                </div>

                {/* Content */}
                <div className="px-6 py-4 space-y-4 max-h-[60vh] overflow-y-auto">
                    {/* Command */}
                    <div className="bg-black/30 rounded-lg p-3">
                        <code className="text-sm font-mono text-zinc-200 break-all">{command}</code>
                    </div>

                    {/* Title & Explanation */}
                    <div>
                        <h3 className={`text-base font-semibold ${colors.text} mb-1`}>
                            {analysis.title}
                        </h3>
                        <p className="text-sm text-zinc-300">{analysis.explanation}</p>
                    </div>

                    {/* Consequences */}
                    {analysis.consequences?.length > 0 && (
                        <ConsequenceList consequences={analysis.consequences} />
                    )}

                    {/* Risk Breakdown */}
                    <div className="space-y-2">
                        <h4 className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">
                            Risk Breakdown
                        </h4>
                        <RiskBar label="Data Loss" value={analysis.data_loss_risk} />
                        <RiskBar label="Service Impact" value={analysis.service_impact_risk} />
                        <RiskBar label="Irreversibility" value={100 - analysis.reversibility} />
                    </div>

                    {/* Safe Alternative */}
                    {analysis.safer_alternative && !isBlocked && (
                        <SafeAlternative
                            command={analysis.safer_alternative}
                            explanation={analysis.alternative_explanation || ''}
                        />
                    )}

                    {/* Command Breakdown */}
                    {analysis.command_breakdown?.length > 0 && (
                        <div className="space-y-1">
                            <h4 className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">
                                Command Breakdown
                            </h4>
                            <div className="bg-black/20 rounded-lg overflow-hidden">
                                {analysis.command_breakdown.map((part: any, i: number) => (
                                    <div key={i} className="flex text-xs border-b border-zinc-800/30 last:border-0">
                                        <span className="font-mono text-yellow-300 px-3 py-1.5 w-24 shrink-0 bg-black/20">
                                            {part.part}
                                        </span>
                                        <span className="text-zinc-300 px-3 py-1.5">{part.meaning}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>

                {/* Actions */}
                <div className="flex gap-3 px-6 py-4 border-t border-zinc-800/50 bg-black/20">
                    {!isBlocked && (
                        <button
                            onClick={onApprove}
                            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-lg transition-colors flex items-center gap-2"
                        >
                            ✅ Approve
                            <span className="text-xs opacity-60">[Enter]</span>
                        </button>
                    )}
                    {analysis.safer_alternative && !isBlocked && (
                        <button
                            onClick={() => onUseAlternative(analysis.safer_alternative!)}
                            className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-lg transition-colors flex items-center gap-2"
                        >
                            🔄 Use Safe
                            <span className="text-xs opacity-60">[S]</span>
                        </button>
                    )}
                    <button
                        onClick={onCancel}
                        className="px-4 py-2 bg-zinc-700 hover:bg-zinc-600 text-white text-sm font-medium rounded-lg transition-colors flex items-center gap-2 ml-auto"
                    >
                        ❌ Cancel
                        <span className="text-xs opacity-60">[Esc]</span>
                    </button>
                </div>
            </div>
        </div>
    )
}
