// WaiterButton.jsx
import React from "react";
import { FaBell } from "react-icons/fa"; // or any other icon
import "../../styles/waiterButton.css";

const WaiterButton = ({ onClick }) => (
  <button className="waiter-call-button" onClick={onClick}>
    <FaBell size={24} />
    {/* Կանչել մատուցողին */}
  </button>
);

export default WaiterButton;
