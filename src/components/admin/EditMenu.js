import React, { useState, useEffect } from "react";
import "../../styles/editMenu.css";
import { BASE_URL } from "../../config";

const EditMenu = () => {
  const [tabs, setTabs] = useState({ AM: [], RU: [] });
  const [newTab, setNewTab] = useState({ AM: "", RU: "" });
  const [selectedTab, setSelectedTab] = useState(null);
  const [items, setItems] = useState([]);
  const [newItem, setNewItem] = useState({
    titleAM: "",
    titleRU: "",
    AM: "",
    RU: "",
    price: "",
    image: null,
  });

  const [editingItem, setEditingItem] = useState(null); // item being edited
  const [editForm, setEditForm] = useState({
    titleAM: "",
    titleRU: "",
    AM: "",
    RU: "",
    price: "",
    image: null,
  });
  // TODO fix after adding branches logic
  const BRANCH_ID = "branch-kfc-1"
  const openEditModal = (item) => {
    setEditingItem(item);
    setEditForm({
      titleAM: item.title?.AM || "",
      titleRU: item.title?.RU || "",
      AM: item.description?.AM || "",
      RU: item.description?.RU || "",
      price: item.price || "",
      image: null,
    });
  }
  const fetchItemsForSelectedTab = async () => {
    if (!selectedTab) return;
    const res = await fetch(`${BASE_URL}/api/items?tab=${selectedTab}&branchId=${BRANCH_ID}`);
    const data = await res.json();
    setItems(data);
  };
  useEffect(() => {
    fetchItemsForSelectedTab();
  }, [selectedTab]);

const handleSaveChanges = async () => {
  const formData = new FormData();
  formData.append("tabId", selectedTab);
  formData.append("branchId", BRANCH_ID);
  formData.append("name", editForm.titleAM);
  formData.append("titleAM", editForm.titleAM);
  formData.append("titleRU", editForm.titleRU);
  formData.append("AM", editForm.AM);
  formData.append("RU", editForm.RU);
  formData.append("price", editForm.price);
  formData.append("image", editingItem.photoUrl || ""); // fallback image

  if (editForm.image) {
    formData.set("image", editForm.image); // override with file
  }

  const res = await fetch(`${BASE_URL}/api/items/${editingItem._id}`, {
    method: "PUT",
    body: formData
  });

  const updated = await res.json();
  setItems((prev) => prev.map((i) => (i._id === updated._id ? updated : i)));
  await fetchItemsForSelectedTab();
  setEditingItem(null);
};

  const handleDeleteItem = async () => {
    await fetch(`${BASE_URL}/api/items/${editingItem._id}`, {
      method: "DELETE",
    });
    setItems((prev) => prev.filter((i) => i._id !== editingItem._id));
    await fetchItemsForSelectedTab();
    setEditingItem(null);
  };

  // Fetch tabs from DB
  useEffect(() => {
    fetch(`${BASE_URL}/api/menus/menu-tabs?branchId=${BRANCH_ID}`)
      .then((res) => res.json())
      .then(setTabs);
  }, []);

  // Fetch items for selected tab
  useEffect(() => {
    if (!selectedTab) return;
    fetch(`${BASE_URL}/api/items?tab=${selectedTab}&branchId=${BRANCH_ID}`)
      .then((res) => res.json())
      .then(setItems);
  }, [selectedTab]);

  const handleTabAdd = () => {
    console.log("here");

    if (!newTab.AM || !newTab.RU) return;

    const updated = {
      AM: [...(tabs.AM || []), newTab.AM],
      RU: [...(tabs.RU || []), newTab.RU],
    };

    fetch(`${BASE_URL}/api/menus/menu-tabs`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...updated, branchId: BRANCH_ID }),
    })
      .then((res) => res.json())
      .then(() => {
        // Re-fetch tabs after saving
        fetch(`${BASE_URL}/api/menus/menu-tabs?branchId=${BRANCH_ID}`)
          .then((res) => res.json())
          .then(setTabs)
          .then((data) => {
            setTabs(data);
            setSelectedTab(newTab.AM); // or default to the first tab in the array
          });;
      });

    setNewTab({ AM: "", RU: "" });

  };

  const handleItemSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append("tabId", selectedTab);
    formData.append("price", newItem.price);
    formData.append("AM", newItem.AM);
    formData.append("RU", newItem.RU);
    formData.append("titleAM", newItem.titleAM);
    formData.append("titleRU", newItem.titleRU);
    formData.append("image", newItem.image);
    formData.append("branchId", BRANCH_ID);

    const res = await fetch(`${BASE_URL}/api/items`, {
      method: "POST",
      body: formData,
    });

    const newEntry = await res.json();
    setItems((prev) => [...prev, newEntry]);
    setNewItem({
      titleAM: "",
      titleRU: "",
      AM: "",
      RU: "",
      price: "",
      image: null,
    });
    await fetchItemsForSelectedTab();
  };

  return (
    <div className="edit-menu">
      <h2>Редактировать Меню</h2>

      <div className="tab-add">
        <input
          type="text"
          placeholder="Նոր բաժին (AM)"
          value={newTab.AM}
          onChange={(e) => setNewTab({ ...newTab, AM: e.target.value })}
        />
        <input
          type="text"
          placeholder="Новый раздел (RU)"
          value={newTab.RU}
          onChange={(e) => setNewTab({ ...newTab, RU: e.target.value })}
        />
        <button type="button" onClick={handleTabAdd}>
          Ավելացնել բաժին
        </button>
      </div>

      <div className="tab-list">
        {tabs?.AM?.map((tab, index) => (
          <button
            key={`${tab}-${index}`}
            className={selectedTab === tab ? "active" : ""}
            onClick={() => setSelectedTab(tab)}
          >
            {tab} / {tabs.RU[index]}
          </button>
        ))}
      </div>

      {selectedTab && (
        <>
          <form className="item-form" onSubmit={handleItemSubmit}>
            <h3>Ավելացնել ուտեստ</h3>
            <input
              type="text"
              placeholder="Վերնագիր (AM)"
              value={newItem.titleAM}
              onChange={(e) =>
                setNewItem({ ...newItem, titleAM: e.target.value })
              }
              required
            />
            <input
              type="text"
              placeholder="Заголовок (RU)"
              value={newItem.titleRU}
              onChange={(e) =>
                setNewItem({ ...newItem, titleRU: e.target.value })
              }
              required
            />
            <input
              type="text"
              placeholder="Описание (AM)"
              value={newItem.AM}
              onChange={(e) => setNewItem({ ...newItem, AM: e.target.value })}
              required
            />
            <input
              type="text"
              placeholder="Описание (RU)"
              value={newItem.RU}
              onChange={(e) => setNewItem({ ...newItem, RU: e.target.value })}
              required
            />
            <input
              type="number"
              placeholder="Цена"
              value={newItem.price}
              onChange={(e) =>
                setNewItem({ ...newItem, price: e.target.value })
              }
              required
            />
            <input
              type="file"
              accept="image/*"
              onChange={(e) =>
                setNewItem({ ...newItem, image: e.target.files[0] })
              }
              required
            />
            <button type="submit">Ավելացնել</button>
          </form>
          <div className="items-section">
            <h3>Ուտեստներ՝: {selectedTab}</h3>
            <div className="item-grid">
              {items.map((item) => (
                <div className="item-card" key={item._id} onClick={() => openEditModal(item)}>
                  <img src={`${BASE_URL}/${item.photoUrl}`} alt="" />
                  <div className="info">
                    <p><b>Վերնագիր:</b> {item.title?.AM}</p>
                    <p><b>Заголовок:</b> {item.title?.RU}</p>
                    <p><b>AM:</b> {item.description?.AM}</p>
                    <p><b>RU:</b> {item.description?.RU}</p>
                    <p><b>Цена:</b> {item.price} ֏</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}

      {editingItem && (
        <div className="modal-overlay">
          <div className="edit-modal-form">
            <h3>Խմբագրել ուտեստը</h3>
            <input
              type="text"
              placeholder="Վերնագիր (AM)"
              value={editForm.titleAM}
              onChange={(e) => setEditForm({ ...editForm, titleAM: e.target.value })}
            />
            <input
              type="text"
              placeholder="Заголовок (RU)"
              value={editForm.titleRU}
              onChange={(e) => setEditForm({ ...editForm, titleRU: e.target.value })}
            />
            <input
              type="text"
              placeholder="Նկարագրություն (AM)"
              value={editForm.AM}
              onChange={(e) => setEditForm({ ...editForm, AM: e.target.value })}
            />
            <input
              type="text"
              placeholder="Описание (RU)"
              value={editForm.RU}
              onChange={(e) => setEditForm({ ...editForm, RU: e.target.value })}
            />
            <input
              type="number"
              placeholder="Գին"
              value={editForm.price}
              onChange={(e) => setEditForm({ ...editForm, price: e.target.value })}
            />
            {editingItem?.photoUrl && (
              <img
                src={`${BASE_URL}/${editingItem.photoUrl}`}
                alt="Current"
                className="modal-preview-image"
              />
            )}
            <label>
              Նոր Նկար (ըստ ցանկության)
              <input
                type="file"
                accept="image/*"
                onChange={(e) => setEditForm({ ...editForm, image: e.target.files[0] })}
              />
            </label>
            <div className="modal-buttons">
              <button onClick={handleSaveChanges}>Պահպանել</button>
              <button onClick={handleDeleteItem}>Ջնջել</button>
              <button onClick={() => setEditingItem(null)}>Փակել</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EditMenu;
