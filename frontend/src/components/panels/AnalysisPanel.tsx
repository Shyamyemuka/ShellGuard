import React from 'react'
import { RiskBar } from '@/components/warning/RiskBar'
import { Badge } from '@/components/shared/Badge'
import type { AnalysisResult } from '@/types/analysis'

interface Props {
    analysis: AnalysisResult | null
}

export function AnalysisPanel({ analysis }: Props) {
    if (!analysis) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-zinc-500">
                <div className="text-4xl mb-3">🛡️</div>
                <p className="text-sm">No analysis yet</p>
                <p className="text-xs mt-1">Try a command to see the analysis</p>
            </div>
        )
    }

    return (
        <div className="space-y-4">
            <div>
                <h3 className="text-sm font-semibold text-zinc-300 mb-2">Last Analysis</h3>
                <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-3 space-y-3">
                    {/* Command */}
                    <div>
                        <span className="text-xs text-zinc-500">Command</span>
                        <div className="font-mono text-sm text-zinc-200 mt-0.5 break-all">
                            {analysis.title}
                        </div>
                    </div>

                    {/* Risk Badge */}
                    <div className="flex items-center gap-2">
                        <span className="text-xs text-zinc-500">Risk</span>
                        <Badge level={analysis.risk_level} score={analysis.risk_score} />
                    </div>

                    {/* Risk Bars */}
                    <div className="space-y-2 pt-2">
                        <RiskBar label="Data Loss" value={analysis.data_loss_risk} />
                        <RiskBar label="Service" value={analysis.service_impact_risk} />
                        <RiskBar label="Irreversible" value={100 - analysis.reversibility} />
                    </div>

                    {/* Details */}
                    <div className="pt-2 border-t border-zinc-800 space-y-2 text-xs">
                        <div className="flex justify-between">
                            <span className="text-zinc-500">Source</span>
                            <span className="text-zinc-300">{analysis.analysis_source}</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-zinc-500">Latency</span>
                            <span className="text-zinc-300">{analysis.analysis_latency_ms}ms</span>
                        </div>
                        {analysis.model_used && (
                            <div className="flex justify-between">
                                <span className="text-zinc-500">Model</span>
                                <span className="text-zinc-300">{analysis.model_used}</span>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Explanation */}
            {analysis.explanation && (
                <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-3">
                    <span className="text-xs text-zinc-500">Explanation</span>
                    <p className="text-sm text-zinc-300 mt-1">{analysis.explanation}</p>
                </div>
            )}
        </div>
    )
}
