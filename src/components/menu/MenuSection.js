import React from "react";
import "../../styles/menuSection.css";

const MenuSection = ({ id, title, items, lang }) => (
  <section id={id} className="menu-section">
    <h2>{title}</h2>
    <div className="menu-grid">
      {items.map((item, idx) => (
        <div className="menu-card" key={item._id || idx}>
          <img
            src={`http://localhost:5000${item.photoUrl || item.image}`}
            alt={item.title?.[lang] || ""}
          />
          <div className="card-body">
            <h3>{item.title?.[lang] || "Անուն"}</h3>
            <p>{item.description?.[lang] || ""}</p>
            <span className="price">{item.price} ֏</span>
          </div>
        </div>
      ))}
    </div>
  </section>
);

export default MenuSection;
