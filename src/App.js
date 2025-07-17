import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
// Admin
import ProtectedRoute from "./ProtectedRoute";
import Statistics from "./components/admin/Statistics";
import Settings from "./components/admin/Settings";
import EditMenu from "./components/admin/EditMenu";
import EditCoverPhoto from "./components/admin/EditCoverPhoto";
import AdminLayout from "./components/admin/AdminLayout";

import "./App.css";
import Tables from "./components/admin/Tables";


// export default ProductPage;
function App() {

  return (
    <Router>
      <Routes>
        {/* Protected admin routes */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <AdminLayout />
            </ProtectedRoute>
          }
        >
          <Route path="tables" element={<Tables />} />
          <Route path="edit-menu" element={<EditMenu />} />
          <Route path="edit-cover" element={<EditCoverPhoto />} />
          <Route path="settings" element={<Settings />} />
          <Route path="statistics" element={<Statistics />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
