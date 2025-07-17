import React, { useState, useEffect } from "react";
import "../../styles/editEmployees.css";

const EditEmployees = () => {
  const [employees, setEmployees] = useState([]);
  const [newEmployee, setNewEmployee] = useState({
    name: "",
    role: "waiter",
    info: "",
    image: null,
    imageUrl: null
  });
  const [editingEmployee, setEditingEmployee] = useState(null);
  const [editForm, setEditForm] = useState({
    name: "",
    role: "waiter",
    info: "",
    image: null,
    imageUrl: null
  });

  useEffect(() => {
    const mock = [
      {
        _id: "emp-001",
        name: "Anna Hakobyan",
        role: "manager",
        info: "General manager with 5 years of experience",
        imageUrl: "https://i.pravatar.cc/150?img=1"
      },
      {
        _id: "emp-002",
        name: "Gor Sargsyan",
        role: "waiter",
        info: "Part-time waiter, student at YSU",
        imageUrl: "https://i.pravatar.cc/150?img=2"
      }
    ];
    setEmployees(mock);
  }, []);

  const handleAdd = () => {
    if (!newEmployee.name || !newEmployee.info || !newEmployee.image) return;

    const url = URL.createObjectURL(newEmployee.image);
    const newEntry = {
      _id: Date.now().toString(),
      ...newEmployee,
      imageUrl: url
    };

    setEmployees((prev) => [...prev, newEntry]);
    setNewEmployee({ name: "", role: "waiter", info: "", image: null, imageUrl: null });
  };

  const openEditModal = (emp) => {
    setEditingEmployee(emp);
    setEditForm({
      name: emp.name,
      role: emp.role,
      info: emp.info,
      image: null,
      imageUrl: emp.imageUrl
    });
  };

  const handleSave = () => {
    const updated = {
      ...editingEmployee,
      ...editForm,
      imageUrl: editForm.image ? URL.createObjectURL(editForm.image) : editForm.imageUrl
    };
    setEmployees((prev) =>
      prev.map((e) => (e._id === editingEmployee._id ? updated : e))
    );
    setEditingEmployee(null);
  };

  const handleDelete = () => {
    setEmployees((prev) => prev.filter((e) => e._id !== editingEmployee._id));
    setEditingEmployee(null);
  };

  return (
    <div className="edit-employees">
      <h2>Employees</h2>

      <div className="employee-add">
        <input
          type="text"
          placeholder="Full Name"
          value={newEmployee.name}
          onChange={(e) => setNewEmployee({ ...newEmployee, name: e.target.value })}
        />
        <select
          value={newEmployee.role}
          onChange={(e) => setNewEmployee({ ...newEmployee, role: e.target.value })}
        >
          <option value="manager">Manager</option>
          <option value="waiter">Waiter</option>
        </select>
        <input
          type="text"
          placeholder="Info"
          value={newEmployee.info}
          onChange={(e) => setNewEmployee({ ...newEmployee, info: e.target.value })}
        />
        <input
          type="file"
          accept="image/*"
          onChange={(e) => setNewEmployee({ ...newEmployee, image: e.target.files[0] })}
        />
        <button onClick={handleAdd}>Add Employee</button>
      </div>

      <div className="employee-grid">
        {employees.map((emp) => (
          <div className="employee-card" key={emp._id} onClick={() => openEditModal(emp)}>
            <img src={emp.imageUrl} alt={emp.name} className="employee-img" />
            <h4>{emp.name}</h4>
            <p>{emp.role === "manager" ? "👔 Manager" : "🧾 Waiter"}</p>
            <p className="info">{emp.info}</p>
          </div>
        ))}
      </div>

      {editingEmployee && (
        <div className="modal-overlay">
          <div className="edit-modal-form">
            <h3>Edit Employee</h3>
            <input
              type="text"
              value={editForm.name}
              onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
            />
            <select
              value={editForm.role}
              onChange={(e) => setEditForm({ ...editForm, role: e.target.value })}
            >
              <option value="manager">Manager</option>
              <option value="waiter">Waiter</option>
            </select>
            <input
              type="text"
              value={editForm.info}
              onChange={(e) => setEditForm({ ...editForm, info: e.target.value })}
              placeholder="Employee Info"
            />
            {editForm.imageUrl && (
              <img src={editForm.imageUrl} alt="" className="modal-preview-image" />
            )}
            <input
              type="file"
              accept="image/*"
              onChange={(e) => setEditForm({ ...editForm, image: e.target.files[0] })}
            />
            <div className="modal-buttons">
              <button onClick={handleSave}>Save</button>
              <button onClick={handleDelete}>Delete</button>
              <button onClick={() => setEditingEmployee(null)}>Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EditEmployees;
