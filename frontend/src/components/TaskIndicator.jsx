"use client";
import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function TaskIndicator() {
    const pathname = usePathname();

    const isActive = (path) => pathname === path;

    return (
        <div className='flex-grow mt-4'>
            <nav>
                <ul className='flex gap-3 justify-between p-3 bg-slate-400 rounded-lg shadow-2xl'>
                    <li>
                        <Link href="/" className={`font-semibold ${isActive('/') ? 'text-blue-900 underline' : 'text-white'}`}>All Task</Link>
                    </li>
                    <li>
                        <Link href="/active" className={`font-semibold ${isActive('/active') ? 'text-blue-900 underline' : 'text-white'}`}>Active</Link>
                    </li>
                    <li>
                        <Link href="/completed" className={`font-semibold ${isActive('/completed') ? 'text-blue-900 underline' : 'text-white'}`}>Completed</Link>
                    </li>
                </ul>
            </nav>
        </div>
    );
}
