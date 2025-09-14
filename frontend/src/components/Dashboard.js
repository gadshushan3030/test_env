import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import { authAPI } from '../api';
import './Dashboard.css';

const Dashboard = ({ user, onLogout }) => {
  const [users, setUsers] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showUserList, setShowUserList] = useState(false);

  useEffect(() => {
    // Check API health on component mount
    checkAPIHealth();
  }, []);

  const checkAPIHealth = async () => {
    try {
      await authAPI.healthCheck();
      toast.success('API מחובר בהצלחה!');
    } catch (error) {
      toast.error('API לא זמין: ' + error.message);
    }
  };

  const loadUsers = async () => {
    setIsLoading(true);
    try {
      const usersList = await authAPI.listUsers();
      setUsers(usersList);
      setShowUserList(true);
      toast.success('רשימת משתמשים נטענה בהצלחה!');
    } catch (error) {
      toast.error('שגיאה בטעינת משתמשים: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
    onLogout();
    toast.success('התנתקת בהצלחה!');
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>ברוכים הבאים, {user.display_name || user.email}!</h1>
        <button onClick={handleLogout} className="logout-button">
          התנתק
        </button>
      </div>

      <div className="dashboard-content">
        <div className="user-info">
          <h2>פרטי המשתמש שלך:</h2>
          <div className="info-card">
            <p><strong>ID:</strong> {user.uid || user.id}</p>
            <p><strong>אימייל:</strong> {user.email}</p>
            <p><strong>שם:</strong> {user.display_name || 'לא מוגדר'}</p>
            <p><strong>טלפון:</strong> {user.phone_number || 'לא מוגדר'}</p>
            <p><strong>אימייל מאומת:</strong> {user.email_verified ? 'כן' : 'לא'}</p>
          </div>
        </div>

        <div className="actions">
          <h2>פעולות זמינות:</h2>
          <div className="action-buttons">
            <button 
              onClick={checkAPIHealth}
              className="action-button"
            >
              בדיקת חיבור ל-API
            </button>
            
            <button 
              onClick={loadUsers}
              className="action-button"
              disabled={isLoading}
            >
              {isLoading ? 'טוען...' : 'טען רשימת משתמשים'}
            </button>
          </div>
        </div>

        {showUserList && (
          <div className="users-list">
            <h2>רשימת משתמשים ({users.length}):</h2>
            <div className="users-grid">
              {users.map((userItem) => (
                <div key={userItem.uid} className="user-card">
                  <h3>{userItem.display_name || 'ללא שם'}</h3>
                  <p><strong>אימייל:</strong> {userItem.email}</p>
                  <p><strong>טלפון:</strong> {userItem.phone_number || 'לא מוגדר'}</p>
                  <p><strong>נוצר:</strong> {new Date(userItem.created_at).toLocaleDateString('he-IL')}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
