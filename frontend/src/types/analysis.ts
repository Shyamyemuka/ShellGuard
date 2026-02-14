/**
 * Analysis result types
 */
export interface CommandBreakdownPart {
    part: string
    meaning: string
    risk_contribution: string
}

export interface AnalysisResult {
    risk_level: 'critical' | 'high' | 'medium' | 'low'
    risk_score: number
    allow: boolean
    title: string
    explanation: string
    consequences: string[]
    safer_alternative: string | null
    alternative_explanation: string | null
    data_loss_risk: number
    service_impact_risk: number
    reversibility: number
    requires_sudo: boolean
    affected_scope: string
    command_breakdown: CommandBreakdownPart[]
    analysis_source: string
    model_used: string | null
    tokens_used: number
    analysis_latency_ms: number
}
