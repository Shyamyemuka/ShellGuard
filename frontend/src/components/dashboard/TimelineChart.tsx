import React from 'react'

export function TimelineChart() {
    return (
        <div className="bg-zinc-900 rounded-lg border border-zinc-800 p-6">
            <h3 className="text-lg font-semibold mb-4">Commands Over Time</h3>
            <div className="flex items-end gap-1 h-40">
                {Array.from({ length: 24 }, (_, i) => {
                    const height = Math.random() * 100
                    return (
                        <div key={i} className="flex-1 flex flex-col items-center gap-1">
                            <div
                                className="w-full bg-green-500/60 rounded-t"
                                style={{ height: `${height}%` }}
                            />
                        </div>
                    )
                })}
            </div>
            <div className="flex justify-between mt-2 text-[10px] text-zinc-500">
                <span>24h ago</span>
                <span>Now</span>
            </div>
            <div className="flex gap-4 mt-3 text-xs">
                <div className="flex items-center gap-1">
                    <div className="w-3 h-2 bg-green-500/60 rounded" />
                    <span className="text-zinc-400">Total</span>
                </div>
                <div className="flex items-center gap-1">
                    <div className="w-3 h-2 bg-red-500/60 rounded" />
                    <span className="text-zinc-400">Intercepted</span>
                </div>
            </div>
        </div>
    )
}
