"use client";
import React, { useContext } from 'react';
import Link from 'next/link';
import TokenContext from '@/context/TokenContext';
import "./header.css";

function Header() {
    const { userToken, tokenDispatch, user, userDispatch } = useContext(TokenContext);

    const logout = () => {
        if (typeof window !== 'undefined') {
            localStorage.removeItem("authToken");
        }
        tokenDispatch({ type: "UNSET_TOKEN" });
        userDispatch({ type: "UNSET_USER" });
        window.location.href = "/login";
    }

    return (
        <div>
            <nav className='header bg-slate-200 flex justify-between items-center px-4'>
                <div className="logo w-1/4 text-center font-bold text-lg">
                    <Link href="/">Todo App</Link>
                </div>
                <div className='flex justify-between'>
                    {
                        userToken ? (
                            <div className='flex items-center justify-center'>
                                <p className='mr-5'>welcome, <span className='text-xl text-blue-800 capitalize'>{user?.name || "User"}</span></p>
                                <button onClick={logout} className="logout mr-4 bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600">Logout</button>
                            </div>
                        ) : (
                            <ul className='flex justify-end gap-4 w-3/4 pr-6'>
                                <li>
                                    <Link href="/login" className="text-blue-600 hover:underline">Login</Link>
                                </li>
                                <li>
                                    <Link href="/register" className="text-blue-600 hover:underline">Register</Link>
                                </li>
                            </ul>
                        )
                    }
                </div>
            </nav>
        </div>
    );
}

export default Header;
