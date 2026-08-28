import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../api';
import type { Ticket, TicketHistory } from '../types';
import { Bot, Trash2, Edit2, History, Save, X } from 'lucide-react';
import { useAuth } from '../AuthContext';

export default function TicketDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [history, setHistory] = useState<TicketHistory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  const [isEditing, setIsEditing] = useState(false);
  const [editStatus, setEditStatus] = useState('');
  const [editPriority, setEditPriority] = useState('');
  
  const [aiLoading, setAiLoading] = useState(false);
  const [deleteLoading, setDeleteLoading] = useState(false);

  useEffect(() => {
    fetchData();
  }, [id]);

  const fetchData = async () => {
    try {
      const [ticketData, historyData] = await Promise.all([
        api.get(`/api/tickets/${id}`),
        api.get(`/api/tickets/${id}/history`)
      ]);
      setTicket(ticketData);
      setHistory(historyData);
      setEditStatus(ticketData.status);
      setEditPriority(ticketData.priority);
    } catch (err: any) {
      if (err.status === 404) {
        setError('Ticket not found');
      } else {
        setError('Failed to load ticket details');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleUpdate = async () => {
    try {
      const updated = await api.put(`/api/tickets/${id}`, {
        status: editStatus,
        priority: editPriority
      });
      setTicket(updated);
      setIsEditing(false);
      // Refresh history
      const historyData = await api.get(`/api/tickets/${id}/history`);
      setHistory(historyData);
    } catch (err: any) {
      alert(err.message || 'Update failed');
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this ticket?')) return;
    setDeleteLoading(true);
    try {
      await api.delete(`/api/tickets/${id}`);
      navigate('/tickets');
    } catch (err: any) {
      alert(err.message || 'Delete failed');
      setDeleteLoading(false);
    }
  };

  const handleAiAnalyze = async () => {
    setAiLoading(true);
    try {
      const updated = await api.post(`/api/tickets/${id}/analyze`, {});
      setTicket(updated);
      const historyData = await api.get(`/api/tickets/${id}/history`);
      setHistory(historyData);
    } catch (err: any) {
      alert(err.message || 'AI Analysis failed. Is GEMINI_API_KEY set?');
    } finally {
      setAiLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div className="text-red-600">{error}</div>;
  if (!ticket) return null;

  const isCreator = user?.id === ticket.created_by;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Ticket #{ticket.id}</h1>
        {isCreator && (
          <div className="flex space-x-2">
            <button
              onClick={() => setIsEditing(!isEditing)}
              className="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-sm font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none"
            >
              {isEditing ? <X className="h-4 w-4 mr-1" /> : <Edit2 className="h-4 w-4 mr-1" />}
              {isEditing ? 'Cancel' : 'Edit'}
            </button>
            <button
              onClick={handleDelete}
              disabled={deleteLoading}
              className="inline-flex items-center px-3 py-1.5 border border-transparent shadow-sm text-sm font-medium rounded text-white bg-red-600 hover:bg-red-700 focus:outline-none disabled:opacity-50"
            >
              <Trash2 className="h-4 w-4 mr-1" />
              Delete
            </button>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">{ticket.title}</h2>
            <p className="text-gray-700 whitespace-pre-wrap">{ticket.description}</p>
          </div>

          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium flex items-center">
                <Bot className="h-5 w-5 mr-2 text-indigo-500" />
                AI Analysis
              </h3>
              <button
                onClick={handleAiAnalyze}
                disabled={aiLoading}
                className="inline-flex items-center px-3 py-1.5 border border-transparent text-sm font-medium rounded shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none disabled:opacity-50"
              >
                {aiLoading ? 'Processing...' : 'Analyze with AI'}
              </button>
            </div>
            
            {ticket.ai_summary ? (
              <div className="space-y-4">
                <div>
                  <span className="block text-xs font-medium text-gray-500 uppercase">Summary</span>
                  <p className="mt-1 text-sm text-gray-900">{ticket.ai_summary}</p>
                </div>
                <div>
                  <span className="block text-xs font-medium text-gray-500 uppercase">Suggested Response</span>
                  <div className="mt-1 p-3 bg-gray-50 rounded border border-gray-200">
                    <p className="text-sm text-gray-800 whitespace-pre-wrap">{ticket.ai_suggested_response}</p>
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-sm text-gray-500 italic">No AI analysis has been performed yet.</p>
            )}
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium mb-4">Details</h3>
            
            {isEditing ? (
              <div className="space-y-4">
                <div>
                  <label className="block text-xs font-medium text-gray-700">Status</label>
                  <select
                    value={editStatus}
                    onChange={(e) => setEditStatus(e.target.value)}
                    className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                  >
                    <option value="OPEN">OPEN</option>
                    <option value="IN_PROGRESS">IN PROGRESS</option>
                    <option value="RESOLVED">RESOLVED</option>
                    <option value="CLOSED">CLOSED</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-700">Priority</label>
                  <select
                    value={editPriority}
                    onChange={(e) => setEditPriority(e.target.value)}
                    className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                  >
                    <option value="LOW">LOW</option>
                    <option value="MEDIUM">MEDIUM</option>
                    <option value="HIGH">HIGH</option>
                    <option value="URGENT">URGENT</option>
                  </select>
                </div>
                <button
                  onClick={handleUpdate}
                  className="w-full inline-flex justify-center items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none"
                >
                  <Save className="h-4 w-4 mr-2" /> Save Changes
                </button>
              </div>
            ) : (
              <dl className="grid grid-cols-1 gap-x-4 gap-y-4">
                <div>
                  <dt className="text-xs font-medium text-gray-500 uppercase">Status</dt>
                  <dd className="mt-1"><span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">{ticket.status}</span></dd>
                </div>
                <div>
                  <dt className="text-xs font-medium text-gray-500 uppercase">Priority</dt>
                  <dd className="mt-1 text-sm font-medium text-gray-900">{ticket.priority}</dd>
                </div>
                <div>
                  <dt className="text-xs font-medium text-gray-500 uppercase">Category</dt>
                  <dd className="mt-1 text-sm text-gray-900">{ticket.category || 'Uncategorized'}</dd>
                </div>
                <div>
                  <dt className="text-xs font-medium text-gray-500 uppercase">Sentiment</dt>
                  <dd className="mt-1 text-sm text-gray-900">{ticket.sentiment || 'Unknown'}</dd>
                </div>
                <div>
                  <dt className="text-xs font-medium text-gray-500 uppercase">Created</dt>
                  <dd className="mt-1 text-sm text-gray-900">{new Date(ticket.created_at).toLocaleString()}</dd>
                </div>
              </dl>
            )}
          </div>

          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium flex items-center mb-4">
              <History className="h-5 w-5 mr-2 text-gray-400" />
              History
            </h3>
            <ul className="space-y-4">
              {history.map((item) => (
                <li key={item.id} className="text-sm">
                  <div className="font-medium text-gray-900">{item.action.replace('_', ' ').toUpperCase()}</div>
                  <div className="text-gray-500 text-xs mt-0.5">{new Date(item.created_at).toLocaleString()}</div>
                  {(item.old_value || item.new_value) && (
                    <div className="mt-1 text-gray-600 text-xs">
                      {item.old_value && <span>{item.old_value} &rarr; </span>}
                      <span className="font-medium">{item.new_value}</span>
                    </div>
                  )}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
