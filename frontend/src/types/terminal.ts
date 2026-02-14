/**
 * Terminal-related types
 */
export interface SessionStats {
    total_commands: number
    safe_commands: number
    warnings_issued: number
    approved_risky: number
    safe_swaps: number
    cancelled: number
    blocked: number
    interception_rate: number
    safe_swap_rate: number
}

export interface TerminalMessage {
    type: string
    data?: string
    command?: string
    rows?: number
    cols?: number
}
