'use client'

import { useState, useCallback } from 'react'
import type { SessionStats } from '@/types/terminal'

export function useSessionStats() {
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

    const update = useCallback((newStats: SessionStats) => {
        setStats(newStats)
    }, [])

    return { stats, update }
}
