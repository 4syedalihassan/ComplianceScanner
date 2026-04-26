const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ApiOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  body?: unknown;
  headers?: Record<string, string>;
}

class ApiClient {
  private token: string | null = null;

  setToken(token: string | null) {
    this.token = token;
    if (token) {
      localStorage.setItem('auth_token', token);
    } else {
      localStorage.removeItem('auth_token');
    }
  }

  getToken(): string | null {
    if (!this.token) {
      this.token = localStorage.getItem('auth_token');
    }
    return this.token;
  }

  async request<T>(endpoint: string, options: ApiOptions = {}): Promise<T> {
    const { method = 'GET', body, headers = {} } = options;

    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    if (body) {
      headers['Content-Type'] = 'application/json';
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
      credentials: 'include',
    });

    if (response.status === 401) {
      this.setToken(null);
      window.location.href = '/login';
      throw new Error('Unauthorized');
    }

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(error.detail || 'Request failed');
    }

    if (response.status === 204) {
      return undefined as T;
    }

    return response.json();
  }

  // Auth
  async login(email: string, password: string) {
    const formData = new URLSearchParams();
    formData.append('email', email);
    formData.append('password', password);

    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData,
      credentials: 'include',
    });

    const data = await response.json();
    
    if (data.mfa_required) {
      return { mfa_required: true, temp_token: data.temp_token };
    }
    
    if (data.access_token) {
      this.setToken(data.access_token);
      return { token: data.access_token };
    }
    
    throw new Error('Login failed');
  }

  async verifyMfa(tempToken: string, code: string) {
    const response = await fetch(`${API_BASE}/auth/mfa-verify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ temp_token: tempToken, code }),
      credentials: 'include',
    });

    const data = await response.json();
    
    if (data.access_token) {
      this.setToken(data.access_token);
      return { token: data.access_token };
    }
    
    throw new Error('MFA verification failed');
  }

  async logout() {
    await this.request('/auth/logout', { method: 'POST' });
    this.setToken(null);
  }

  // Customers
  async getCustomers() {
    return this.request<Array<{
      id: number;
      name: string;
      type: string;
      environment: string;
      accounts: string;
      last_scan: string;
      compliance_score: number;
      status: string;
    }>>('/api/customers');
  }

  async getCustomer(id: number) {
    return this.request<{
      id: number;
      name: string;
      type: string;
      created_at: string;
    }>(`/api/customers/${id}`);
  }

  async createCustomer(data: { name: string; type: string; environment: string }) {
    return this.request('/api/customers', { method: 'POST', body: data });
  }

  async updateCustomer(id: number, data: { name?: string; type?: string }) {
    return this.request(`/api/customers/${id}`, { method: 'PUT', body: data });
  }

  async deleteCustomer(id: number) {
    return this.request(`/api/customers/${id}`, { method: 'DELETE' });
  }

  // Scans
  async getScans(customerId: number) {
    return this.request<Array<{
      id: number;
      customer_id: number;
      scan_type: string;
      status: string;
      started_at: string;
      completed_at: string;
      findings_count: number;
    }>>(`/api/customers/${customerId}/scans`);
  }

  async getScan(id: number) {
    return this.request<{
      id: number;
      customer_id: number;
      scan_type: string;
      status: string;
      findings: Array<{
        id: number;
        control_id: string;
        title: string;
        severity: string;
        status: string;
      }>;
    }>(`/api/scans/${id}`);
  }

  async triggerScan(customerId: number, scanType: string) {
    return this.request(`/api/customers/${customerId}/scan`, {
      method: 'POST',
      body: { scan_type: scanType },
    });
  }

  // Findings
  async getFindings(customerId: number, filters?: { severity?: string; status?: string }) {
    const params = new URLSearchParams();
    if (filters?.severity) params.append('severity', filters.severity);
    if (filters?.status) params.append('status', filters.status);
    
    const query = params.toString();
    return this.request<Array<{
      id: number;
      control_id: string;
      title: string;
      description: string;
      severity: string;
      status: string;
      asset: string;
      customer_name: string;
      scan_date: string;
    }>>(`/api/customers/${customerId}/findings${query ? `?${query}` : ''}`);
  }

  async updateFindingStatus(id: number, status: string) {
    return this.request(`/api/findings/${id}/status`, {
      method: 'PUT',
      body: { status },
    });
  }

  // Reports
  async getReports(customerId: number) {
    return this.request<Array<{
      id: number;
      title: string;
      type: string;
      generated_at: string;
      compliance_score: number;
    }>>(`/api/customers/${customerId}/reports`);
  }

  async downloadReport(id: number) {
    const response = await fetch(`${API_BASE}/api/reports/${id}/download`, {
      headers: { 'Authorization': `Bearer ${this.getToken()}` },
    });
    
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `report-${id}.pdf`;
    a.click();
    window.URL.revokeObjectURL(url);
  }

  // Users
  async getUsers() {
    return this.request<Array<{
      id: number;
      email: string;
      name: string;
      role: string;
      mfa_enabled: boolean;
      status: string;
      last_login: string;
    }>>('/api/users');
  }

  async createUser(data: { email: string; name: string; role: string; password: string }) {
    return this.request('/api/users', { method: 'POST', body: data });
  }

  async updateUser(id: number, data: { name?: string; role?: string }) {
    return this.request(`/api/users/${id}`, { method: 'PUT', body: data });
  }

  async deleteUser(id: number) {
    return this.request(`/api/users/${id}`, { method: 'DELETE' });
  }

  // Audit Logs
  async getAuditLogs(filters?: { action?: string }) {
    const params = new URLSearchParams();
    if (filters?.action) params.append('action', filters.action);
    
    const query = params.toString();
    return this.request<Array<{
      id: number;
      action: string;
      user_email: string;
      ip_address: string;
      details: string;
      timestamp: string;
    }>>(`/api/audit-logs${query ? `?${query}` : ''}`);
  }

  // Dashboard Stats
  async getDashboardStats() {
    return this.request<{
      compliance_score: number;
      total_customers: number;
      critical_findings: number;
      active_scans: number;
    }>('/api/dashboard/stats');
  }

  async getRecentFindings(limit: number = 10) {
    return this.request<Array<{
      id: number;
      control_id: string;
      title: string;
      severity: string;
      status: string;
    }>>(`/api/dashboard/recent-findings?limit=${limit}`);
  }

  async getActivityFeed(limit: number = 10) {
    return this.request<Array<{
      id: number;
      type: string;
      title: string;
      description: string;
      timestamp: string;
    }>>(`/api/dashboard/activity?limit=${limit}`);
  }

  // Agents
  async getAgents(customerId: number) {
    return this.request<Array<{
      id: number;
      hostname: string;
      ip_address: string;
      agent_type: string;
      os: string;
      status: string;
      last_check: string;
      findings_count: number;
    }>>(`/api/customers/${customerId}/agents`);
  }

  async generateAgentScript(customerId: number, osType: string) {
    return this.request<{ script: string }>(`/api/agents/generate`, {
      method: 'POST',
      body: { customer_id: customerId, os_type: osType },
    });
  }

  // Settings
  async getSettings() {
    return this.request<{
      organization_name: string;
      timezone: string;
      require_mfa: boolean;
      session_timeout: number;
      scan_retention_days: number;
      audit_retention_days: number;
    }>('/api/settings');
  }

  async updateSettings(data: {
    organization_name?: string;
    timezone?: string;
    require_mfa?: boolean;
    session_timeout?: number;
    scan_retention_days?: number;
    audit_retention_days?: number;
  }) {
    return this.request('/api/settings', { method: 'PUT', body: data });
  }

  async getEmailSettings() {
    return this.request<{
      smtp_host: string;
      smtp_port: number;
      notifications: Array<{ event: string; enabled: boolean }>;
      recipients: string[];
    }>('/api/settings/email');
  }

  async updateEmailSettings(data: {
    smtp_host?: string;
    smtp_port?: number;
    notifications?: Array<{ event: string; enabled: boolean }>;
    recipients?: string[];
  }) {
    return this.request('/api/settings/email', { method: 'PUT', body: data });
  }

  async getIntegrations() {
    return this.request<Array<{ id: string; name: string; connected: number; status: string }>>('/api/settings/integrations');
  }

  async connectIntegration(id: string, credentials: unknown) {
    return this.request(`/api/settings/integrations/${id}/connect`, {
      method: 'POST',
      body: credentials,
    });
  }
}

export const api = new ApiClient();
export default api;