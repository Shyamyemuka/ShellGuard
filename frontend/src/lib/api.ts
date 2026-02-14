/**
 * REST API Client
 */
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

async function fetchJson(path: string) {
    const response = await fetch(`${API_URL}${path}`)
    if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
    }
    return response.json()
}

export async function fetchStats() {
    return fetchJson('/stats')
}

export async function fetchHistory(params?: { limit?: number; risk_level?: string; action?: string }) {
    const query = new URLSearchParams()
    if (params?.limit) query.set('limit', params.limit.toString())
    if (params?.risk_level) query.set('risk_level', params.risk_level)
    if (params?.action) query.set('action', params.action)
    return fetchJson(`/history?${query.toString()}`)
}

export async function fetchHealth() {
    return fetchJson('/health')
}

export async function fetchDashboardSummary() {
    return fetchJson('/dashboard/summary')
}

export async function fetchRiskDistribution() {
    return fetchJson('/dashboard/risk-distribution')
}

export async function fetchTimeline() {
    return fetchJson('/dashboard/timeline')
}

export async function fetchTopDangerous() {
    return fetchJson('/dashboard/top-dangerous')
}

export async function fetchPatterns() {
    return fetchJson('/patterns')
}
