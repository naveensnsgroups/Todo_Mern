"use client";
import React, { useContext } from 'react';
import CompletedTask from '@/components/CompletedTask';
import TaskContext from '@/context/TaskContext';

export default function CompletedTaskPage() {
    const { tasks } = useContext(TaskContext);
    const completedTasks = tasks ? tasks.filter(t => t.completed) : [];

    return (
        <div>
            {
                (completedTasks.length !== 0) ? (
                    tasks.map((task, index) => {
                        return (
                            task.completed && <CompletedTask
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
