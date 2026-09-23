"use client";
import React, { useContext } from 'react';
import Task from '@/components/Task/Task';
import TaskContext from '@/context/TaskContext';

export default function AllTaskPage() {
    const { tasks } = useContext(TaskContext);
    return (
        <div>
            {
                (tasks && tasks.length !== 0) ? (
                    tasks.map((task, index) => {
                        return (
                            <Task
                                key={index}
                                task={task}
                                id={index}
                            />
                        );
                    })
                ) : (
                    <h1 className="text-center text-gray-500 mt-6 text-lg">No Task Found</h1>
                )
            }
        </div>
    );
}
