// Statistics.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import '../../styles/statistics.css';

const Statistics = () => {
  const [usersByDate, setUsersByDate] = useState([]);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [totalUsers, setTotalUsers] = useState(0);

  const fetchUserStats = async (date) => {
    try {
      const res = await axios.get(`https://nts-center.ru/api/stats/users?date=${date}`);
      setUsersByDate(res.data);
    } catch (err) {
      console.error('Error fetching stats:', err);
    }
  };

  useEffect(() => {
    fetchUserStats(selectedDate);
  }, [selectedDate]);

  const fetchTotalUsers = async () => {
  try {
    const res = await axios.get('https://nts-center.ru/api/stats/total_users');
    setTotalUsers(res.data.total);
  } catch (err) {
    console.error('Error fetching total user count:', err);
  }
};
useEffect(() => {
  fetchTotalUsers();
}, []);

  return (
    <div className="statistics-container">
      <h2>📈 Статистика пользователей</h2>
      <div className="total-users-box">
        <h3>👥 Всего пользователей:</h3>
        <p><strong>{totalUsers}</strong></p>
      </div>

      <div className="date-picker">
        <label>Выберите дату: </label>
        <input
          type="date"
          value={selectedDate}
          onChange={(e) => setSelectedDate(e.target.value)}
        />
      </div>

      <div className="stats-box">
        <h3>Пользователи за {selectedDate}:</h3>
        <p><strong>{usersByDate.count || 0}</strong> новых пользователей</p>
        {usersByDate.users && usersByDate.users.length > 0 && (
          <ul className="user-list">
            {usersByDate.users.map((user) => (
              <li key={user.telegram_id}>
                {user.telegram_id || '--'} (@{user.username || 'нет'})
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default Statistics;