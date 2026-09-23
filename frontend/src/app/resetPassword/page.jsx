"use client";
import React, { useState, Suspense } from 'react';
import { useSearchParams } from "next/navigation";
import axios from "@/Axios/axios.js";

function ResetPasswordForm() {
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [message, setMessage] = useState("");
    const [error, setError] = useState("");
    const searchParams = useSearchParams();
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setMessage("");
        setError("");
        if (password !== confirmPassword) {
            setError("Passwords do not match");
            setIsLoading(false);
        } else {
            try {
                const token = searchParams.get("token");
                const res = await axios.post("/forgotPassword/resetPassword", { token, password });
                setMessage(res.data.message);
            } catch (err) {
                setError(err.response?.data?.message || "Reset failed");
            } finally {
                setIsLoading(false);
            }
        }
    };

    return (
        <div className='text-center py-12'>
            <h1 className='text-xl font-bold p-5'>Reset Password</h1>
            <form className="w-2/5 mx-auto p-5" onSubmit={handleSubmit}>
                <input type="password"
                    className="p-3 rounded-md shadow-lg w-full my-4 border border-gray-300"
                    placeholder="Enter new password"
                    onChange={(e) => setPassword(e.target.value)}
                    value={password}
                    required
                />
                <input type="password"
                    className="p-3 rounded-md shadow-lg w-full my-4 border border-gray-300"
                    placeholder="Confirm new password"
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    value={confirmPassword}
                    required
                />
                <button className="p-2 rounded-md shadow-md bg-indigo-700 text-white px-5 mt-10 disabled:bg-indigo-400" disabled={isLoading}>Reset</button>
            </form>
            {
                message && <div className='mt-10 bg-green-700 mx-auto w-2/5 p-3 rounded-lg shadow-lg text-white text-lg'>
                    <p>{message}</p>
                </div>
            }
            {
                error && <div className='mt-10 bg-red-700 mx-auto w-2/5 p-3 rounded-lg shadow-lg text-white text-lg'>
                    <p>{error}</p>
                </div>
            }
        </div>
    );
}

export default function ResetPasswordPage() {
    return (
        <Suspense fallback={<div>Loading...</div>}>
            <ResetPasswordForm />
        </Suspense>
    );
}
