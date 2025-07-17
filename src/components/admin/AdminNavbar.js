import { Link } from "react-router-dom";

function AdminNavbar({ onLogout }) {
  return (
    <nav className="navbar">
      <div className="navbar-logo">MENU Admin</div>
      <ul className="navbar-links">
        <li><Link to="/edit-menu">Меню</Link></li>
        <li><Link to="/edit-cover">Обложка</Link></li>
        <li><Link to="/settings">Настройки</Link></li>
        <li><button onClick={onLogout} className="logout-button">Выйти</button></li>
      </ul>
    </nav>
  );
}

export default AdminNavbar;
