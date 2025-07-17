import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import "../../styles/branches.css";
import { BASE_URL } from "../../config";

const EditBranches = () => {
  const [branches, setBranches] = useState([]);
  const [newBranch, setNewBranch] = useState({ name: "", address: "" });
  const [editingBranch, setEditingBranch] = useState(null);
  const [editForm, setEditForm] = useState({ name: "", address: "" });
  const navigate = useNavigate();

  useEffect(() => {
  const subdomain = window.location.hostname.split(".")[0];

  const fetchBranches = async () => {
    const token = localStorage.getItem("jwt_token");
    const activeBranchId = localStorage.getItem("active_branch_id");

    if (!token || !activeBranchId) return;

    try {
      const res = await fetch(`${window.location.origin}/api/branchesApi`, {
        headers: {
          "X-Restaurant-Id": subdomain,
        },
      });

      if (!res.ok) throw new Error("Failed to fetch branches");
      const data = await res.json();
      setBranches(data);
    } catch (err) {
      console.error("❌ Branch fetch failed:", err);
      alert("Failed to load branches. Please check your connection.");
    }
  };

  const interval = setInterval(() => {
    const token = localStorage.getItem("jwt_token");
    const activeBranchId = localStorage.getItem("active_branch_id");
    if (token && activeBranchId) {
      clearInterval(interval);
      fetchBranches();
    }
  }, 200); // Check every 200ms

  return () => clearInterval(interval);
}, []);
  const handleAddBranch = () => {
    if (!newBranch.name || !newBranch.address) return;
    const newEntry = {
      _id: Date.now().toString(),
      ...newBranch
    };
    setBranches((prev) => [...prev, newEntry]);
    setNewBranch({ name: "", address: "" });
  };

  const openEditModal = (branch) => {
    setEditingBranch(branch);
    setEditForm({ name: branch.name, address: branch.address });
  };

  const handleSaveChanges = () => {
    setBranches((prev) =>
      prev.map((b) =>
        b._id === editingBranch._id ? { ...b, ...editForm } : b
      )
    );
    setEditingBranch(null);
  };

  const handleDeleteBranch = () => {
    setBranches((prev) => prev.filter((b) => b._id !== editingBranch._id));
    setEditingBranch(null);
  };

  return (
    <div className="edit-branches">
      <h2>Restaurant Branches</h2>

      <div className="branch-add">
        <input
          type="text"
          placeholder="Branch Name"
          value={newBranch.name}
          onChange={(e) => setNewBranch({ ...newBranch, name: e.target.value })}
        />
        <input
          type="text"
          placeholder="Branch Address"
          value={newBranch.address}
          onChange={(e) => setNewBranch({ ...newBranch, address: e.target.value })}
        />
        <button onClick={handleAddBranch}>Add Branch</button>
      </div>

      <div className="branch-grid">
        {branches.map((branch) => (
          <div className="branch-card" key={branch._id} onClick={() => { navigate(`/edit-menu`, { replace: true }); }}>
            <h4>{branch.name}</h4>
            <p>{branch.address}</p>
          </div>
        ))}
      </div>

      {editingBranch && (
        <div className="modal-overlay">
          <div className="edit-modal-form">
            <h3>Edit Branch</h3>
            <input
              type="text"
              value={editForm.name}
              onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
            />
            <input
              type="text"
              value={editForm.address}
              onChange={(e) => setEditForm({ ...editForm, address: e.target.value })}
            />
            <div className="modal-buttons">
              <button onClick={handleSaveChanges}>Save</button>
              <button onClick={handleDeleteBranch}>Delete</button>
              <button onClick={() => setEditingBranch(null)}>Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EditBranches;
