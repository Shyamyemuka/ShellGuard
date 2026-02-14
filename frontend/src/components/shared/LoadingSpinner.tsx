import React from 'react'

interface Props {
    size?: 'sm' | 'md' | 'lg'
}

export function LoadingSpinner({ size = 'md' }: Props) {
    const sizes = {
        sm: 'w-4 h-4',
        md: 'w-6 h-6',
        lg: 'w-8 h-8',
    }

    return (
        <div className={`${sizes[size]} animate-spin rounded-full border-2 border-zinc-700 border-t-green-500`} />
    )
}
