import React from 'react';
import { Navigate, Outlet, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import { LayoutDashboard, Ticket, LogOut, PlusCircle } from 'lucide-react';
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function ProtectedRoute() {
  const { user, isLoading } = useAuth();
  
  if (isLoading) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }
  
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="flex h-screen bg-gray-50 text-gray-900 font-sans">
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="h-16 flex items-center px-6 border-b border-gray-200">
          <span className="text-lg font-bold text-indigo-600">Support Desk</span>
        </div>
        
        <nav className="flex-1 p-4 space-y-1">
          <NavLink to="/" icon={<LayoutDashboard size={20} />} label="Dashboard" />
          <NavLink to="/tickets" icon={<Ticket size={20} />} label="Tickets" />
          <NavLink to="/tickets/new" icon={<PlusCircle size={20} />} label="Create Ticket" />
        </nav>
        
        <div className="p-4 border-t border-gray-200">
          <div className="mb-4 px-2">
            <p className="text-sm font-medium text-gray-900 truncate">{user.full_name || 'Agent'}</p>
            <p className="text-xs text-gray-500 truncate">{user.email}</p>
          </div>
          <LogoutButton />
        </div>
      </aside>
      
      <main className="flex-1 overflow-auto">
        <div className="p-8 max-w-7xl mx-auto">
          <Outlet />
        </div>
      </main>
    </div>
  );
}

function NavLink({ to, icon, label }: { to: string, icon: React.ReactNode, label: string }) {
  const location = useLocation();
  const isActive = location.pathname === to || (to !== '/' && location.pathname.startsWith(to));
  
  return (
    <Link
      to={to}
      className={cn(
        "flex items-center space-x-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
        isActive 
          ? "bg-indigo-50 text-indigo-700" 
          : "text-gray-700 hover:bg-gray-100"
      )}
    >
      {icon}
      <span>{label}</span>
    </Link>
  );
}

function LogoutButton() {
  const { logout } = useAuth();
  return (
    <button
      onClick={logout}
      className="flex items-center space-x-3 px-3 py-2 w-full rounded-md text-sm font-medium text-gray-700 hover:bg-red-50 hover:text-red-700 transition-colors"
    >
      <LogOut size={20} />
      <span>Logout</span>
    </button>
  );
}
