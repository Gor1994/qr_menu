import { Outlet, useNavigate } from "react-router-dom";
import AdminNavbar from "./AdminNavbar"; // extracted navbar here
import "../../styles/adminNavbar.css";

function AdminLayout() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/admin/login");
  };

  return (
    <>
      <AdminNavbar onLogout={handleLogout} />
      <Outlet />
      <footer className="footer">
        <p>&copy; 2025 AterGrid. All rights reserved.</p>
      </footer>
    </>
  );
}

export default AdminLayout;
