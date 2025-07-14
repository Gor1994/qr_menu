import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { useState, useEffect } from "react";

// Admin
import LoginPage from "./components/admin/LoginPage";
import ProtectedRoute from "./ProtectedRoute";
import Statistics from "./components/admin/Statistics";
import Settings from "./components/admin/Settings";
import EditMenu from "./components/admin/EditMenu";
import EditCoverPhoto from "./components/admin/EditCoverPhoto";
import AdminLayout from "./components/admin/AdminLayout";

// Menu
import Header from "./components/menu/Header";
import Navbar from "./components/menu/Navbar";
import MenuSection from "./components/menu/MenuSection";
// import { menuDataAM } from "./data/menu";
import { slugify } from "./utils/slugify";
import WaiterButton from "./components/menu/WaiterButton";


import "./App.css";

function MenuLandingPage() {
  const [lang, setLang] = useState("AM");

  const [tabs, setTabs] = useState({ AM: [], RU: [] });
  const [menuData, setMenuData] = useState({}); // { "Hot Dishes": [items], ... }

  useEffect(() => {
    const fetchData = async () => {
      const tabsRes = await fetch("http://localhost:5000/api/menu-tabs");
      const tabsData = await tabsRes.json();
      setTabs(tabsData); // { AM: [...], RU: [...] }

      // Fetch all items using AM tab names as tabId keys
      const allItems = {};
      for (const tab of tabsData.AM) {
        const itemsRes = await fetch(`http://localhost:5000/api/menu-items?tab=${tab}`);
        const itemsData = await itemsRes.json();
        allItems[tab] = itemsData;
      }
      setMenuData(allItems);
    };

    fetchData();
  }, []);

  const sectionList = (tabs.AM || []).map((amLabel, idx) => {
    const ruLabel = tabs.RU?.[idx] || "";
    const label = { AM: amLabel, RU: ruLabel };

    return {
      id: slugify(label[lang]),   // visible section id
      tabId: amLabel,             // used to fetch items
      label,                      // localized display
      items: menuData[amLabel] || []  // access by AM tab label
    };
  });

  return (
    <div>
      <Header lang={lang} setLang={setLang} />
      <div id="navbar-sentinel" />
      <Navbar sections={sectionList} lang={lang} />
      <main>
        {sectionList.map((section) => (
          <MenuSection
            key={section.id}
            id={section.id}
            title={section.label[lang]}
            items={section.items}
            lang={lang}
          />
        ))}
      </main>
      <WaiterButton onClick={() => alert("Մատուցողը կկանչվի անմիջապես")} />
    </div>
  );
}


function App() {
  return (
    <Router>
      <Routes>
        {/* Admin login without layout */}
        <Route path="/admin/login" element={<LoginPage />} />

        {/* Admin section with layout */}
        <Route path="/admin" element={<AdminLayout />}>
          <Route path="edit-menu" element={<EditMenu />} />
          <Route path="edit-cover" element={<ProtectedRoute><EditCoverPhoto /></ProtectedRoute>} />
          <Route path="settings" element={<Settings />} />
          <Route path="statistics" element={<ProtectedRoute><Statistics /></ProtectedRoute>} />
        </Route>

        {/* Public menu */}
        <Route path="/*" element={<MenuLandingPage />} />
      </Routes>
    </Router>
  );
}

export default App;
