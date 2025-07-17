import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import "../../styles/branches.css";

const EditBranches = () => {
  const [branches, setBranches] = useState([]);
  const [newBranch, setNewBranch] = useState({ name: "", address: "" });
  const [editingBranch, setEditingBranch] = useState(null);
  const [editForm, setEditForm] = useState({ name: "", address: "" });
  const navigate = useNavigate();

  useEffect(() => {
    // Mock data for branches
    const mockBranches = [
      { _id: "branch-001", name: "Downtown KFC", address: "5 Abovyan St, Yerevan" },
      { _id: "branch-002", name: "Komitas KFC", address: "125 Komitas Ave, Yerevan" },
      { _id: "branch-003", name: "Malatia KFC", address: "45 Sebastia St, Yerevan" },
      { _id: "branch-004", name: "Kentron KFC", address: "1 Republic Square, Yerevan" },
      { _id: "branch-005", name: "Arabkir KFC", address: "88 Baghramyan Ave, Yerevan" }
    ];
    setBranches(mockBranches);
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
          <div className="branch-card" key={branch._id} onClick={() => {navigate(`/edit-menu`, { replace: true });}}>
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
