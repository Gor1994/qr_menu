import React, { useState } from "react";
import "../../styles/tables.css";

/* Mock data with images + qty + price */
const mockTables = [
  {
    id: 1,
    status: "busy",
    orders: [
      {
        image: "/images/borscht.jpg",
        title: "Բորշ",
        titleRU: "Борщ",
        qty: 2,
        price: 1500,
      },
      {
        image: "/images/khash.jpg",
        title: "Խաշ",
        titleRU: "Хаш",
        qty: 1,
        price: 2500,
      },
    ],
  },
  {
    id: 2,
    status: "need_waiter",
    orders: [
      {
        image: "/images/salad.jpg",
        title: "Թարմ աղցան",
        titleRU: "Свежий салат",
        qty: 1,
        price: 1100,
      },
    ],
  },
  {
    id: 3,
    status: "check_request",
    orders: [
      {
        image: "/images/steak.jpg",
        title: "Սթեյք",
        titleRU: "Стейк",
        qty: 1,
        price: 4500,
      },
      {
        image: "/images/coke.jpg",
        title: "Կոկա-Կոլա",
        titleRU: "Coca-Cola",
        qty: 2,
        price: 600,
      },
    ],
  },
  { id: 4, status: "free", orders: [] },
  { id: 5, status: "reserved", orders: [] },
  { id: 6, status: "busy", orders: [] },
  { id: 7, status: "free", orders: [] },
  { id: 8, status: "need_waiter", orders: [] },
  { id: 9, status: "reserved", orders: [] },
  { id: 10, status: "check_request", orders: [] },
];

/* Status meta */
const statusInfo = {
  busy: { label: "Занят", color: "gray", desc: "Клиенты находятся за столом" },
  need_waiter: { label: "Вызвать официанта", color: "red", desc: "Нужна помощь официанта" },
  check_request: { label: "Просит счёт", color: "yellow", desc: "Гость просит счёт" },
  free: { label: "Свободен", color: "green", desc: "Стол свободен" },
  reserved: { label: "Забронирован", color: "blue", desc: "Стол зарезервирован" },
};

export default function TablesPage() {
  const [selected, setSelected] = useState(null);

  return (
    <div className="tables-page">
      <h2>Столы</h2>
      <div className="table-grid">
        {mockTables.map((t) => (
          <div
            key={t.id}
            className={`table-card status-${t.status}`}
            onClick={() => setSelected(t)}
          >
            {t.id}
          </div>
        ))}
      </div>

      {selected && (
        <div className="modal-overlay" onClick={() => setSelected(null)}>
          <div className="modal-table" onClick={(e) => e.stopPropagation()}>
            <h3>Стол №{selected.id}</h3>
            <p className={`status-tag status-${selected.status}`}>
              {statusInfo[selected.status].label}
            </p>
            <p className="description">{statusInfo[selected.status].desc}</p>

            <h4>Заказы</h4>
            {selected.orders.length === 0 ? (
              <p className="order-note">Нет активных заказов</p>
            ) : (
              <div className="order-list">
                {selected.orders.map((o, i) => (
                  <div key={i} className="order-item">
                    <img src={o.image} alt={o.title} />
                    <div className="order-info">
                      <b>{o.title}</b>
                      <p>{o.titleRU}</p>
                      <p>
                        {o.qty} × {o.price} ֏ = {o.qty * o.price} ֏
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}

            <button className="close-button" onClick={() => setSelected(null)}>
              Закрыть
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
