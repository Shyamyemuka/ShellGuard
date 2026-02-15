'use client'

import { useState, useRef, useCallback, useEffect } from 'react'
import type { ShellTerminalRef } from '@/components/terminal/ShellTerminal'
import type { AnalysisResult } from '@/types/analysis'
import type { HistoryEntry } from '@/types/history'
import type { SessionStats } from '@/types/terminal'

interface WarningState {
    command: string
    analysis: AnalysisResult
}

interface BlockedState {
    command: string
    message: string
    risk_level: string
}

interface ToastNotification {
    id: number
    message: string
    type: 'info' | 'warning' | 'error' | 'success'
}

interface UseTerminalSocketOptions {
    onWarning?: (command: string, analysis: AnalysisResult) => void
    onStatsUpdate?: (stats: SessionStats) => void
    onHistoryUpdate?: (entry: HistoryEntry) => void
}

export function useTerminalSocket(options: UseTerminalSocketOptions = {}) {
    const terminalRef = useRef<ShellTerminalRef>(null)
    const wsRef = useRef<WebSocket | null>(null)
    const [isConnected, setIsConnected] = useState(false)
    const [isAnalyzing, setIsAnalyzing] = useState(false)
    const [analyzingCommand, setAnalyzingCommand] = useState('')
    const [warning, setWarning] = useState<WarningState | null>(null)
    const [blocked, setBlocked] = useState<BlockedState | null>(null)
    const [toasts, setToasts] = useState<ToastNotification[]>([])
    const toastIdRef = useRef(0)

    const showToast = useCallback((message: string, type: ToastNotification['type'] = 'info') => {
        const id = toastIdRef.current++
        setToasts(prev => [...prev, { id, message, type }])
    }, [])

    const connect = useCallback(() => {
        const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws/terminal'
        const ws = new WebSocket(wsUrl)
        wsRef.current = ws

        ws.onopen = () => {
            setIsConnected(true)
            console.log('🛡️ ShellGuard connected')
        }

        ws.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data)
                handleMessage(message)
            } catch {
                // Raw text
            }
        }

        ws.onclose = () => {
            setIsConnected(false)
            // Reconnect after 2 seconds
            setTimeout(connect, 2000)
        }

        ws.onerror = () => {
            setIsConnected(false)
        }
    }, [])

    const handleMessage = useCallback((message: any) => {
        switch (message.type) {
            case 'output':
                terminalRef.current?.write(message.data)
                break

            case 'analyzing':
                setIsAnalyzing(true)
                setAnalyzingCommand(message.command)
                break

            case 'analysis_complete':
                setIsAnalyzing(false)
                setAnalyzingCommand('')
                // If analysis shows invalid command, show a toast notification
                if (message.analysis && message.analysis.title === 'Invalid Command') {
                    showToast(`Command not found: "${message.command}". ${message.analysis.explanation}`, 'warning')
                } else if (message.analysis && message.analysis.title) {
                    // For other safe commands with analysis feedback
                    const explanation = message.analysis.explanation
                    if (explanation && explanation.length < 100) {
                        showToast(explanation, 'info')
                    }
                }
                break

            case 'warning':
                setIsAnalyzing(false)
                setWarning({
                    command: message.command,
                    analysis: message.analysis,
                })
                options.onWarning?.(message.command, message.analysis)
                options.onHistoryUpdate?.({
                    command: message.command,
                    timestamp: new Date().toISOString(),
                    risk_level: message.analysis.risk_level,
                    action: 'warning',
                })
                break

            case 'blocked':
                setIsAnalyzing(false)
                setBlocked({
                    command: message.command,
                    message: message.message,
                    risk_level: message.risk_level,
                })
                options.onHistoryUpdate?.({
                    command: message.command,
                    timestamp: new Date().toISOString(),
                    risk_level: 'critical',
                    action: 'blocked',
                })
                break

            case 'stats_update':
                options.onStatsUpdate?.(message.stats)
                break

            case 'pong':
                break

            case 'error':
                console.error('Server error:', message.message)
                break
        }
    }, [options])

    const sendMessage = useCallback((msg: any) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify(msg))
        }
    }, [])

    const writeToTerminal = useCallback((data: string) => {
        sendMessage({ type: 'input', data })
    }, [sendMessage])

    const sendApprove = useCallback(() => {
        sendMessage({ type: 'approve' })
        if (warning) {
            options.onHistoryUpdate?.({
                command: warning.command,
                timestamp: new Date().toISOString(),
                risk_level: warning.analysis.risk_level,
                action: 'approved',
            })
        }
        setWarning(null)
    }, [sendMessage, warning, options])

    const sendCancel = useCallback(() => {
        sendMessage({ type: 'cancel' })
        if (warning) {
            options.onHistoryUpdate?.({
                command: warning.command,
                timestamp: new Date().toISOString(),
                risk_level: warning.analysis.risk_level,
                action: 'cancelled',
            })
        }
        setWarning(null)
        setBlocked(null)
    }, [sendMessage, warning, options])

    const sendUseAlternative = useCallback((command: string) => {
        sendMessage({ type: 'use_alternative', command })
        if (warning) {
            options.onHistoryUpdate?.({
                command: command,
                timestamp: new Date().toISOString(),
                risk_level: 'safe',
                action: 'safe_swap',
            })
        }
        setWarning(null)
    }, [sendMessage, warning, options])

    // Connect on mount
    useEffect(() => {
        connect()
        return () => {
            wsRef.current?.close()
        }
    }, [connect])

    // Ping keepalive
    useEffect(() => {
        const interval = setInterval(() => {
            sendMessage({ type: 'ping' })
        }, 30000)
        return () => clearInterval(interval)
    }, [sendMessage])

    return {
        terminalRef,
        isConnected,
        isAnalyzing,
        analyzingCommand,
        warning,
        blocked,
        toasts,
        sendApprove,
        sendCancel,
        sendUseAlternative,
        writeToTerminal,
        removeToast: (id: number) => setToasts(prev => prev.filter(t => t.id !== id)),
    }
}
