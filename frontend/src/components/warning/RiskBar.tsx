import React from 'react'

interface Props {
    label: string
    value: number
}

export function RiskBar({ label, value }: Props) {
    const clampedValue = Math.max(0, Math.min(100, value))

    const getColor = (val: number) => {
        if (val >= 80) return 'bg-red-500'
        if (val >= 60) return 'bg-orange-500'
        if (val >= 40) return 'bg-yellow-500'
        if (val >= 20) return 'bg-blue-500'
        return 'bg-green-500'
    }

    return (
        <div className="flex items-center gap-3">
            <span className="text-xs text-zinc-400 w-28 shrink-0">{label}</span>
            <div className="flex-1 h-2 bg-zinc-800 rounded-full overflow-hidden">
                <div
                    className={`h-full rounded-full risk-bar-fill ${getColor(clampedValue)}`}
                    style={{ width: `${clampedValue}%` }}
                />
            </div>
            <span className="text-xs text-zinc-400 w-10 text-right">{clampedValue}%</span>
        </div>
    )
}
