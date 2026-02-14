import React from 'react'

interface Props {
    commands: Array<{ command: string; count: number }>
}

export function TopDangerous({ commands }: Props) {
    const maxCount = Math.max(...commands.map(c => c.count), 1)

    return (
        <div className="bg-zinc-900 rounded-lg border border-zinc-800 p-6">
            <h3 className="text-lg font-semibold mb-4">Most Common Dangerous Commands</h3>
            <div className="space-y-3">
                {commands.length === 0 && (
                    <p className="text-zinc-500 text-sm">No dangerous commands detected yet</p>
                )}
                {commands.map((cmd, i) => (
                    <div key={i} className="flex items-center gap-3">
                        <span className="text-xs text-zinc-500 w-6">{i + 1}.</span>
                        <span className="font-mono text-sm text-zinc-300 w-40 truncate">{cmd.command}</span>
                        <div className="flex-1 h-4 bg-zinc-800 rounded overflow-hidden">
                            <div
                                className="h-full bg-red-500/70 rounded transition-all duration-500"
                                style={{ width: `${(cmd.count / maxCount) * 100}%` }}
                            />
                        </div>
                        <span className="text-xs text-zinc-400 w-16 text-right">{cmd.count} times</span>
                    </div>
                ))}
            </div>
        </div>
    )
}
