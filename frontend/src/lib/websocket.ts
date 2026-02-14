/**
 * WebSocket client helper
 */
export function createWebSocket(url: string): WebSocket {
    return new WebSocket(url)
}

export function getWebSocketUrl(): string {
    return process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws/terminal'
}
