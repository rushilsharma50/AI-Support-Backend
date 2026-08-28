export interface User {
  id: number;
  email: string;
  full_name: string | null;
  is_active: boolean;
  created_at: string;
}

export interface Ticket {
  id: number;
  title: string;
  description: string;
  status: 'OPEN' | 'IN_PROGRESS' | 'RESOLVED' | 'CLOSED';
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';
  category: 'BILLING' | 'TECHNICAL' | 'ACCOUNT' | 'SHIPPING' | 'GENERAL' | null;
  sentiment: 'POSITIVE' | 'NEUTRAL' | 'NEGATIVE' | null;
  ai_summary: string | null;
  ai_suggested_response: string | null;
  created_by: number;
  assigned_to: number | null;
  created_at: string;
  updated_at: string;
}

export interface TicketHistory {
  id: number;
  ticket_id: number;
  user_id: number;
  action: string;
  old_value: string | null;
  new_value: string | null;
  created_at: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}
