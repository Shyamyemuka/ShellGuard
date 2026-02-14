/**
 * History entry types
 */
export interface HistoryEntry {
    id?: string
    session_id?: string
    command: string
    timestamp: string
    risk_level: string
    action: string
    risk_score?: number
    risk_title?: string
    analysis_latency_ms?: number
}
