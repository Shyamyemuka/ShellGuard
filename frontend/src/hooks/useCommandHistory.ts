'use client'

import { useState, useCallback } from 'react'
import type { HistoryEntry } from '@/types/history'

export function useCommandHistory() {
    const [entries, setEntries] = useState<HistoryEntry[]>([])

    const addEntry = useCallback((entry: HistoryEntry) => {
        setEntries(prev => [entry, ...prev].slice(0, 200))
    }, [])

    const clear = useCallback(() => {
        setEntries([])
    }, [])

    return { entries, addEntry, clear }
}
