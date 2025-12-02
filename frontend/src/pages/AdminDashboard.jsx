import { useState, useEffect } from "react";
import { toast } from "sonner";
import axios from "axios";
import { ClipboardList, Trash2, Lock, LogOut, Users } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Logo = ({ size = "default" }) => (
  <div className="logo-container" style={{ 
    marginBottom: size === "small" ? 0 : 24,
    gap: size === "small" ? 8 : 12 
  }}>
    <img 
      src="/logo.png" 
      alt="Nexovent Labs" 
      className="logo-image" 
      style={{ 
        width: size === "small" ? 32 : 48, 
        height: size === "small" ? 32 : 48,
        animation: size === "small" ? "none" : undefined
      }} 
    />
    <span className="logo-text" style={{ fontSize: size === "small" ? 18 : 24 }}>
      <span className="orange">Nexovent</span>
      <span className="black"> Labs</span>
    </span>
  </div>
);

const AdminDashboard = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    return sessionStorage.getItem("adminAuthenticated") === "true";
  });
  const [password, setPassword] = useState("");
  const [submissions, setSubmissions] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [loginError, setLoginError] = useState("");

  useEffect(() => {
    if (isAuthenticated) {
      fetchSubmissions();
    }
  }, []);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoginError("");

    try {
      const response = await axios.post(`${API}/admin/verify`, { password });
      if (response.data.success) {
        setIsAuthenticated(true);
        sessionStorage.setItem("adminAuthenticated", "true");
        fetchSubmissions();
      }
    } catch (error) {
      setLoginError("Invalid password. Please try again.");
    }
  };

  const fetchSubmissions = async () => {
    setIsLoading(true);
    try {
      const response = await axios.get(`${API}/submissions`);
      setSubmissions(response.data);
    } catch (error) {
      console.error("Error fetching submissions:", error);
      toast.error("Failed to load submissions");
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this submission?")) return;

    try {
      await axios.delete(`${API}/submissions/${id}`);
      setSubmissions((prev) => prev.filter((s) => s.id !== id));
      toast.success("Submission deleted");
    } catch (error) {
      console.error("Error deleting submission:", error);
      toast.error("Failed to delete submission");
    }
  };

  const formatDate = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  if (!isAuthenticated) {
    return (
      <div className="admin-login">
        <div className="admin-login-card">
          <Logo />
          <div className="admin-icon">
            <Lock size={28} color="white" />
          </div>
          <h1>Admin Access</h1>
          <p>Enter password to view submissions</p>

          <form onSubmit={handleLogin}>
            <div className="form-field">
              <input
                type="password"
                placeholder="Enter admin password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                data-testid="admin-password-input"
              />
              {loginError && <p className="error-text">{loginError}</p>}
            </div>
            <button type="submit" className="submit-btn" data-testid="admin-login-btn">
              Access Dashboard
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-container">
      <div className="admin-header">
        <div className="admin-header-left">
          <Logo size="small" />
          <span style={{ 
            color: '#a1a1aa', 
            fontSize: 24, 
            fontWeight: 300,
            marginLeft: 8,
            marginRight: 8
          }}>|</span>
          <h1 style={{ margin: 0 }}>Dashboard</h1>
        </div>
        <button 
          className="logout-btn" 
          onClick={() => {
            setIsAuthenticated(false);
            setPassword("");
            sessionStorage.removeItem("adminAuthenticated");
          }}
          data-testid="logout-btn"
        >
          <LogOut size={16} style={{ marginRight: 8 }} />
          Logout
        </button>
      </div>

      <div className="admin-content">
        <div className="stats-bar">
          <div className="stat-item">
            <Users size={20} color="#FF6B35" />
            <span className="stat-label">Total Submissions</span>
            <span className="stat-value" data-testid="total-submissions">{submissions.length}</span>
          </div>
        </div>

        {isLoading ? (
          <div className="loading">Loading submissions</div>
        ) : submissions.length === 0 ? (
          <div className="empty-state">
            <ClipboardList size={56} />
            <p>No submissions yet</p>
          </div>
        ) : (
          <div className="table-container">
            <table className="submissions-table" data-testid="submissions-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Business Name</th>
                  <th>Mobile Number</th>
                  <th>Email</th>
                  <th>Submitted At</th>
                  <th style={{ textAlign: 'center' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {submissions.map((submission) => (
                  <tr key={submission.id} data-testid={`submission-row-${submission.id}`}>
                    <td style={{ fontWeight: 500, color: '#18181b' }}>{submission.name}</td>
                    <td>{submission.business_name}</td>
                    <td>{submission.mobile_number}</td>
                    <td>{submission.email || '-'}</td>
                    <td style={{ color: '#71717a' }}>{formatDate(submission.timestamp)}</td>
                    <td style={{ textAlign: 'center' }}>
                      <button
                        className="delete-btn"
                        onClick={() => handleDelete(submission.id)}
                        data-testid={`delete-btn-${submission.id}`}
                      >
                        <Trash2 size={14} style={{ marginRight: 6 }} />
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminDashboard;
