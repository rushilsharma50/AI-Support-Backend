import React, { useEffect, useState } from 'react';
import { api } from '../api';
import type { Ticket } from '../types';
import { Ticket as TicketIcon, AlertCircle, AlertTriangle, AlertOctagon } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Dashboard() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        // Fetch all tickets to calculate stats frontend-side as requested
        const data = await api.get('/api/tickets?limit=1000');
        setTickets(data);
      } catch (err) {
        console.error('Failed to load tickets', err);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (loading) return <div>Loading dashboard...</div>;

  const total = tickets.length;
  const open = tickets.filter(t => t.status === 'OPEN').length;
  const highUrgent = tickets.filter(t => t.priority === 'HIGH' || t.priority === 'URGENT').length;
  const negative = tickets.filter(t => t.sentiment === 'NEGATIVE').length;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard title="Total Tickets" value={total} icon={<TicketIcon className="text-blue-500" />} />
        <StatCard title="Open Tickets" value={open} icon={<AlertCircle className="text-yellow-500" />} />
        <StatCard title="High/Urgent Priority" value={highUrgent} icon={<AlertTriangle className="text-orange-500" />} />
        <StatCard title="Negative Sentiment" value={negative} icon={<AlertOctagon className="text-red-500" />} />
      </div>

      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-medium text-gray-900">Recent Tickets</h2>
          <Link to="/tickets" className="text-sm text-indigo-600 hover:text-indigo-900">View all</Link>
        </div>
        <div className="divide-y divide-gray-200">
          {tickets.slice(0, 5).map(ticket => (
            <div key={ticket.id} className="py-4 flex justify-between items-center hover:bg-gray-50 -mx-6 px-6 transition-colors">
              <div className="flex-1 min-w-0">
                <Link to={`/tickets/${ticket.id}`} className="text-sm font-medium text-indigo-600 truncate">{ticket.title}</Link>
                <p className="text-sm text-gray-500 truncate">{ticket.description}</p>
              </div>
              <div className="ml-4 flex items-center space-x-2">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                  {ticket.status}
                </span>
              </div>
            </div>
          ))}
          {tickets.length === 0 && (
            <div className="py-4 text-center text-sm text-gray-500">No support tickets yet.</div>
          )}
        </div>
      </div>
    </div>
  );
}

function StatCard({ title, value, icon }: { title: string, value: number | string, icon: React.ReactNode }) {
  return (
    <div className="bg-white overflow-hidden shadow rounded-lg">
      <div className="p-5">
        <div className="flex items-center">
          <div className="flex-shrink-0">{icon}</div>
          <div className="ml-5 w-0 flex-1">
            <dl>
              <dt className="text-sm font-medium text-gray-500 truncate">{title}</dt>
              <dd className="text-3xl font-semibold text-gray-900">{value}</dd>
            </dl>
          </div>
        </div>
      </div>
    </div>
  );
}
