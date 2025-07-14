import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../../styles/loginPage.css'; // optional: create and style as needed

export default function LoginPage() {
  const [step, setStep] = useState(1);
  const [login, setLogin] = useState('');
  const [code, setCode] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleRequestLogin = async () => {
    setLoading(true);
    setMessage('');
    try {
      const res = await fetch('/api/request-login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ login }),
      });
      const data = await res.json();
      if (data.success) {
        setStep(2);
      } else {
        setMessage(data.message || 'Ошибка входа');
      }
    } catch (err) {
      setMessage('Сервер недоступен');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyCode = async () => {
    setLoading(true);
    setMessage('');
    try {
      const res = await fetch('/api/verify-code', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ login, code }),
      });
      const data = await res.json();
      if (data.success) {
        localStorage.setItem('token', data.token);
        navigate('/add-phone');
      } else {
        setMessage(data.message || 'Неверный код');
      }
    } catch (err) {
      setMessage('Сервер недоступен');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <h2>🔐 Вход в админ-панель</h2>

      {step === 1 && (
        <>
          <p>Введите Telegram ID или username</p>
          <input
            type="text"
            value={login}
            onChange={(e) => setLogin(e.target.value)}
            placeholder="Пример: 12345678 или gor_karapetyan"
            className="login-input"
          />
          <button onClick={handleRequestLogin} disabled={loading}>
            {loading ? 'Отправка...' : 'Получить код'}
          </button>
        </>
      )}

      {step === 2 && (
        <>
          <p>Введите код, отправленный в Telegram</p>
          <input
            type="text"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder="6-значный код"
            className="login-input"
          />
          <button onClick={handleVerifyCode} disabled={loading}>
            {loading ? 'Проверка...' : 'Войти'}
          </button>
        </>
      )}

      {message && <p className="login-error">{message}</p>}
    </div>
  );
}
