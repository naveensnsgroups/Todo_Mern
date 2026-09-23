"use client";
import React from 'react';
import moment from 'moment';
import DeleteIcon from '@mui/icons-material/Delete';
import { useContext } from 'react';
import TaskContext from '@/context/TaskContext';

export default function Task({ task, id }) {
    const { dispatch } = useContext(TaskContext);

    const handleRemove = (e) => {
        e.preventDefault();
        dispatch({
            type: "REMOVE_TASK",
            id
        });
    };

    const handleMarkDone = (e) => {
        dispatch({
            type: "MARK_DONE",
            id
        });
    };

    return (
        <div className='bg-slate-300 py-4 rounded-lg shadow-md flex items-center justify-center gap-2 mb-3 px-2'>
            <div className="mark-done">
                <input type="checkbox" className="checkbox w-4 h-4 cursor-pointer" onChange={handleMarkDone} checked={task.completed} />
            </div>
            <div className="task-info text-slate-900 text-sm w-10/12">
                <h4 className="task-title text-lg capitalize font-semibold">{task.title}</h4>
                <p className="task-description">{task.description}</p>
                <div className='italic opacity-60 text-xs'>
                    {
                        task?.createdAt ? (
                            <p>{moment(task.createdAt).fromNow()}</p>
                        ) : (
                            <p>just now</p>
                        )
                    }
                </div>
            </div>
            <div className="remove-task text-sm text-white">
                <DeleteIcon
                    style={{ fontSize: 30, cursor: "pointer" }}
                    onClick={handleRemove}
                    className="remove-task-btn bg-blue-700 rounded-full border-2 shadow-2xl border-white p-1 hover:bg-blue-800" />
            </div>
        </div>
    );
}
