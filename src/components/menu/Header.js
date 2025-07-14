import React from "react";
import "../../styles/header.css";

const Header = ({ lang, setLang }) => (
  <header className="header">
    <img
      src="/images/cover.jpg"
      alt="Cover"
      className="header-image"
    />
    <div className="overlay" />
    <div className="header-content">
      {/* <h1>Ընտանեկան Ռեստորան</h1> */}
      <div className="lang-switch">
        <button
          onClick={() => setLang("AM")}
          className={lang === "AM" ? "active" : ""}
        >
          🇦🇲
        </button>
        <button
          onClick={() => setLang("RU")}
          className={lang === "RU" ? "active" : ""}
        >
          🇷🇺
        </button>
      </div>
    </div>
  </header>
);

export default Header;
