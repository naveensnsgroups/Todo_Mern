"use client";
import './globals.css';
import { useEffect, useReducer } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import TokenContext from '@/context/TokenContext';
import TaskContext from '@/context/TaskContext';
import tokenReducer from '@/reducer/tokenReducer';
import userReducer from '@/reducer/userReducer';
import taskReducer from '@/reducer/taskReducer';
import Header from '@/components/Header/Header';
import Layout from '@/components/Layout';
import axios from '@/Axios/axios';

function ProvidersWrapper({ children }) {
  const router = useRouter();
  const pathname = usePathname();

  const getStoredToken = () => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem("authToken");
      if (stored) {
        try {
          return JSON.parse(stored);
        } catch {
          return stored;
        }
      }
    }
    return null;
  };

  const initialToken = getStoredToken();
  const [userToken, tokenDispatch] = useReducer(tokenReducer, initialToken);
  const [user, userDispatch] = useReducer(userReducer, {});
  const [tasks, dispatch] = useReducer(taskReducer, []);

  const isAuthRoute = pathname === '/login' || pathname === '/register' || pathname === '/forgotPassword' || pathname === '/resetPassword';

  useEffect(() => {
    if (!initialToken && !isAuthRoute) {
      router.push('/login');
    }
  }, [initialToken, isAuthRoute, router]);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const res = await axios.get("/user/getUser", {
          headers: {
            Authorization: `Bearer ${userToken}`
          }
        });
        userDispatch({ type: "SET_USER", payload: res.data.user });
      } catch (error) {
        console.log(error);
      }
    };
    if (userToken) {
      fetchUser();
    }
  }, [userToken]);

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        const res = await axios.get("/task/getTask", {
          headers: {
            Authorization: `Bearer ${userToken}`
          }
        });
        dispatch({ type: "SET_TASK", payload: res.data });
      } catch (error) {
        console.log(error);
      }
    };
    if (userToken) {
      fetchTasks();
    }
  }, [userToken]);

  return (
    <TokenContext.Provider value={{ userToken, tokenDispatch, user, userDispatch }}>
      <TaskContext.Provider value={{ tasks, dispatch }}>
        <Header />
        {isAuthRoute ? (
          children
        ) : (
          userToken ? <Layout>{children}</Layout> : null
        )}
      </TaskContext.Provider>
    </TokenContext.Provider>
  );
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="bg-gray-100 min-h-screen">
        <ProvidersWrapper>
          {children}
        </ProvidersWrapper>
      </body>
    </html>
  );
}
