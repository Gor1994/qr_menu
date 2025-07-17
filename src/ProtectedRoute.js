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

      // 1. Subdomain mismatch protection
      if (restaurantId !== subdomain) {
        localStorage.removeItem("jwt_token");
        redirectToLogin();
        return;
      }

      // 2. Manager/waiter logic
      if (role === "manager" || role === "waiter") {
        const activeBranchId = localStorage.getItem("active_branch_id");

        if (!activeBranchId) {
          localStorage.setItem("active_branch_id", branchId);
        } else if (activeBranchId !== branchId) {
          console.warn("❌ Branch mismatch. Resetting to correct branch.");
          localStorage.setItem("active_branch_id", branchId);
          window.location.reload();
          return;
        }

        setLoading(false);
        return;
      }

      // 3. Partner logic
      if (role === "partner") {
        console.log("🧩 Partner role detected");

        const activeBranchId = localStorage.getItem("active_branch_id");

        if (!activeBranchId) {
          console.log("here");
          
          // Save list of branchIds
          if (Array.isArray(branchIds) && branchIds.length > 0) {
            localStorage.setItem("branch_ids", JSON.stringify(branchIds));
            localStorage.setItem("active_branch_id", branchIds[0]); // default to first one
          } else {
            console.warn("❌ No branchIds found for partner");
            redirectToLogin();
            return;
          }

          const isBranchesRoute =
            path === "/branches" || path === "/" || window.location.href.includes("/branches");

          if (!isBranchesRoute) {
            console.log("🔁 Redirecting partner to /branches");
            navigate("/branches");
            return;
          }

          setLoading(false);
          return;
        }

        // ✅ Partner already has active branch
        setLoading(false);
        return;
      }

      // 4. Unknown role fallback
      redirectToLogin();
    };

    // Token from hash (first-time login)
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
        console.error("Invalid token from hash:", e);
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
        console.error("Invalid stored token:", e);
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

