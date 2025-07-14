import React, { useEffect, useState } from 'react';
import '../../styles/settings.css';

export default function Settings() {
  const [admins, setAdmins] = useState([]);
  const [currentUserRole, setCurrentUserRole] = useState('');
  const [selectedAdmin, setSelectedAdmin] = useState(null);
  const [newAdmin, setNewAdmin] = useState({ telegram_id: '', username: '', role: 'admin' });

  const token = localStorage.getItem('token');

  const fetchAdmins = async () => {
    const res = await fetch('/api/admins', {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await res.json();
    setAdmins(data.admins);
    setCurrentUserRole(data.currentUserRole);
  };

  useEffect(() => {
    fetchAdmins();
  }, []);

  const handleAddAdmin = async () => {
    await fetch('/api/admins', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(newAdmin),
    });
    setNewAdmin({ telegram_id: '', username: '', role: 'admin' });
    fetchAdmins();
  };

  const handleSave = async () => {
    await fetch(`/api/admins/${selectedAdmin._id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ role: selectedAdmin.role }),
    });
    setSelectedAdmin(null);
    fetchAdmins();
  };

  const handleRemove = async () => {
    await fetch(`/api/admins/${selectedAdmin._id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` },
    });
    setSelectedAdmin(null);
    fetchAdmins();
  };

  if (currentUserRole !== 'superadmin') {
    return <p style={{ textAlign: 'center' }}>⛔ Доступ запрещён</p>;
  }

  return (
    <div className="settings-container">
      <h2>🛠 Управление администраторами</h2>

      <div className="add-admin-form">
        <input
          type="text"
          placeholder="Telegram ID"
          value={newAdmin.telegram_id}
          onChange={(e) => setNewAdmin({ ...newAdmin, telegram_id: e.target.value })}
        />
        <input
          type="text"
          placeholder="Username"
          value={newAdmin.username}
          onChange={(e) => setNewAdmin({ ...newAdmin, username: e.target.value })}
        />
        <select
          value={newAdmin.role}
          onChange={(e) => setNewAdmin({ ...newAdmin, role: e.target.value })}
        >
          <option value="admin">Admin</option>
          <option value="superadmin">Superadmin</option>
        </select>
        <button onClick={handleAddAdmin}>➕ Добавить</button>
      </div>

      <div className="admins-list">
        {admins.map((admin) => (
          <div
            key={admin._id}
            className="admin-card"
            onClick={() => setSelectedAdmin(admin)}
          >
            <h4>{admin.username}</h4>
            <p>ID: {admin.telegram_id}</p>
            <p>Роль: {admin.role}</p>
          </div>
        ))}
      </div>

      {selectedAdmin && (
        <div className="admin-modal">
          <h3>Редактировать администратора</h3>
          <p>Username: {selectedAdmin.username}</p>
          <p>ID: {selectedAdmin.telegram_id}</p>
          <select
            value={selectedAdmin.role}
            onChange={(e) =>
              setSelectedAdmin({ ...selectedAdmin, role: e.target.value })
            }
          >
            <option value="admin">Admin</option>
            <option value="superadmin">Superadmin</option>
          </select>
          <div className="admin-actions">
            <button onClick={handleSave}>💾 Сохранить</button>
            <button onClick={handleRemove} className="danger">🗑 Удалить</button>
            <button onClick={() => setSelectedAdmin(null)}>✖ Закрыть</button>
          </div>
        </div>
      )}
    </div>
  );
}