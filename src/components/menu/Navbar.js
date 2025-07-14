import React, { useEffect, useState, useRef } from "react";
import "../../styles/navbar.css";

const Navbar = ({ sections, lang }) => {
    const [active, setActive] = useState(sections[0]?.id);
    const [isSticky, setIsSticky] = useState(false);
    const navRef = useRef(null);

    // Track active section during scroll
    useEffect(() => {
        const observer = new IntersectionObserver(
            (entries) => {
                let topMost = null;
                for (const entry of entries) {
                    if (entry.isIntersecting) {
                        if (
                            !topMost ||
                            entry.boundingClientRect.top < topMost.boundingClientRect.top
                        ) {
                            topMost = entry;
                        }
                    }
                }
                if (topMost) {
                    setActive(topMost.target.id);
                }
            },
            {
                rootMargin: '-50% 0px -50% 0px',  // better for mobile
                threshold: 0
            }
        );

        sections.forEach((section) => {
            const el = document.getElementById(section.id);
            if (el) observer.observe(el);
        });

        return () => observer.disconnect();
    }, [sections]);

    // Detect scroll position to toggle sticky class
    useEffect(() => {
        const sentinel = document.getElementById("navbar-sentinel");

        const observer = new IntersectionObserver(
            ([entry]) => {
                setIsSticky(!entry.isIntersecting); // becomes sticky when sentinel disappears
            },
            { threshold: 0 }
        );

        if (sentinel) observer.observe(sentinel);

        return () => observer.disconnect();
    }, []);
    return (
        <nav
            ref={navRef}
            className={`menu-nav ${isSticky ? "sticky" : ""}`}
        >
            {sections.map((sec) => (
                <a
                    key={sec.id}
                    href={`#${sec.id}`}
                    className={active === sec.id ? "active" : ""}
                    onClick={(e) => {
                        e.preventDefault();
                        const target = document.getElementById(sec.id);
                        if (target) {
                            const yOffset = -70;
                            const y =
                                target.getBoundingClientRect().top + window.pageYOffset + yOffset;
                            window.scrollTo({ top: y, behavior: "smooth" });
                            setActive(sec.id);
                        }
                    }}
                >
                    {sec.label[lang]}
                </a>
            ))}
        </nav>
    );
};

export default Navbar;
