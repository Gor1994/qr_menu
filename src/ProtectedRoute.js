// import { useEffect, useState } from "react";
// import { jwtDecode } from "jwt-decode";

// const ProtectedRoute = ({ children }) => {
//   const [loading, setLoading] = useState(true);

// useEffect(() => {
//   const subdomain = window.location.hostname.split(".")[0];

//   const redirectToLogin = () => {
//     window.location.href = "https://login.ater-vpn.ru";
//   };

//   const hash = window.location.hash;
//   const tokenFromHash = hash.startsWith("#token=")
//     ? hash.replace("#token=", "")
//     : null;

//   if (tokenFromHash) {
//     try {
//       const decoded = jwtDecode(tokenFromHash);
//       const partner = decoded.restaurantId;

//       if (partner === subdomain) {
//         localStorage.setItem("jwt_token", tokenFromHash);
//         console.log("✅ Token saved from hash.");
//         window.location.hash = ""; // Clean it up
//         window.location.reload(); // Restart protected flow
//       } else {
//         console.warn("❌ Partner mismatch. Redirecting...");
//         redirectToLogin();
//       }
//       return;
//     } catch (e) {
//       console.error("Invalid token in hash:", e);
//       redirectToLogin();
//       return;
//     }
//   }

//   const storedToken = localStorage.getItem("jwt_token");

//   if (storedToken) {
//     try {
//       const decoded = jwtDecode(storedToken);
//       if (decoded.restaurantId === subdomain) {
//         setLoading(false);
//       } else {
//         console.warn("❌ Partner mismatch in stored token.");
//         localStorage.removeItem("jwt_token");
//         redirectToLogin();
//       }
//     } catch (e) {
//       console.error("❌ Invalid stored token:", e);
//       localStorage.removeItem("jwt_token");
//       redirectToLogin();
//     }
//   } else {
//     redirectToLogin(); // No token at all
//   }
// }, []);


//   if (loading) return null; // or a loading spinner

//   return children;
// };

// export default ProtectedRoute;

import { useEffect, useState } from "react";
import { jwtDecode } from "jwt-decode";
import { useLocation, useNavigate } from "react-router-dom";

const ProtectedRoute = ({ children }) => {
  const [loading, setLoading] = useState(true);
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const subdomain = window.location.hostname.split(".")[0];
    const hash = window.location.hash;
    const tokenFromHash = hash.startsWith("#token=")
      ? hash.replace("#token=", "")
      : null;

    const redirectToLogin = () => {
      window.location.href = "https://login.ater-vpn.ru";
    };

    const handleRouting = (decoded) => {
      const { role, restaurantId, branchId, branchIds } = decoded;
      const path = location.pathname;
      const query = new URLSearchParams(location.search);
      const branchIdInUrl = query.get("branchId");

      // Ensure subdomain matches restaurantId
      if (restaurantId !== subdomain) {
        console.warn("❌ Subdomain mismatch");
        localStorage.removeItem("jwt_token");
        redirectToLogin();
        return;
      }

      if (role === "partner") {
        // Partners go to /branches
        if (path !== "/branches") {
          navigate("/branches", { replace: true });
          return;
        }
      }

      if (role === "manager" || role === "waiter") {
        if (path !== "/edit-menu" || branchIdInUrl !== branchId) {
          console.warn("❌ Unauthorized branch access. Redirecting...");
          navigate(`/edit-menu?branchId=${branchId}`, { replace: true });
          return;
        }
      }

      setLoading(false);
    };

    // Token from hash (first time login)
    if (tokenFromHash) {
      try {
        const decoded = jwtDecode(tokenFromHash);
        if (decoded.restaurantId === subdomain) {
          localStorage.setItem("jwt_token", tokenFromHash);
          console.log("✅ Token saved from hash.");
          window.location.hash = "";
          window.location.reload();
        } else {
          redirectToLogin();
        }
      } catch (e) {
        console.error("Invalid token from hash");
        redirectToLogin();
      }
      return;
    }

    // Token from localStorage
    const storedToken = localStorage.getItem("jwt_token");
    if (storedToken) {
      try {
        const decoded = jwtDecode(storedToken);
        handleRouting(decoded);
      } catch (e) {
        console.error("Invalid stored token");
        localStorage.removeItem("jwt_token");
        redirectToLogin();
      }
    } else {
      redirectToLogin();
    }
  }, [location]);

  if (loading) return null;

  return children;
};

export default ProtectedRoute;

