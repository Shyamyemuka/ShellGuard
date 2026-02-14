import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
    title: 'ShellGuard - AI Terminal Safety Copilot',
    description: 'AI-powered terminal copilot that intercepts dangerous commands',
}

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="en" className="dark">
            <head>
                <link
                    href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap"
                    rel="stylesheet"
                />
            </head>
            <body className="bg-zinc-950 text-zinc-50 min-h-screen">
                {children}
            </body>
        </html>
    )
}
