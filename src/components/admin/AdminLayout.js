import { Outlet, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import AdminNavbar from "./AdminNavbar";
import "../../styles/adminNavbar.css";

function AdminLayout() {
  // const [loading, setLoading] = useState(true);
  // const navigate = useNavigate();

  // useEffect(() => {
  //   const urlParams = new URLSearchParams(window.location.search);
  //   const tokenFromUrl = urlParams.get("token");

  //   if (tokenFromUrl) {
  //     localStorage.setItem("jwt_token", tokenFromUrl);

  //     // Clean up URL
  //     const cleanUrl = window.location.origin + window.location.pathname;
  //     window.history.replaceState({}, document.title, cleanUrl);
  //   }

  //   const token = localStorage.getItem("jwt_token");
  //   if (!token) {
  //     window.location.href = "https://login.ater-vpn.ru";
  //   } else {
  //     setLoading(false);
  //   }
  // }, []);

  const handleLogout = () => {
    localStorage.removeItem("jwt_token");
    window.location.href = "https://login.ater-vpn.ru";
  };

  // if (loading) return null;

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
