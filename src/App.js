import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
// Admin
import ProtectedRoute from "./ProtectedRoute";
import Statistics from "./components/admin/Statistics";
import EditMenu from "./components/admin/EditMenu";
import EditCoverPhoto from "./components/admin/EditCoverPhoto";
import AdminLayout from "./components/admin/AdminLayout";

import "./App.css";
import Tables from "./components/admin/Tables";
import EditBranches from "./components/admin/Branches";
import EditEmployees from "./components/admin/EditEmployees";


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
          <Route path="statistics" element={<Statistics />} />
          <Route path="" element={<EditBranches />} />
          <Route path="employees" element={<EditEmployees />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
