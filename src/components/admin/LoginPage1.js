import { useEffect } from "react";
import { GoogleLogin } from "@react-oauth/google";
import { jwtDecode } from "jwt-decode";
import { useNavigate } from "react-router-dom";

const LoginPage = () => {
    const navigate = useNavigate();

    const handleGoogleLogin = async (credentialResponse) => {
        try {
            const decoded = jwtDecode(credentialResponse.credential);
            const email = decoded.email;

            // Check if partner
            const partnerRes = await fetch("http://127.0.0.1:5000/api/check-partner", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email }),
            });

            const partnerData = await partnerRes.json();
            // Check if admin
            const adminRes = await fetch("http://127.0.0.1:5000/api/check-admin", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email }),
            });

            const adminData = await adminRes.json();

            if (partnerData.success || adminData.success) {
                // Optionally save login state here
                navigate("/admin/edit-menu");
                return;
            }
            alert("Access denied. You're not authorized.");
        } catch (err) {
            console.error("Login error:", err);
            alert("Something went wrong during login.");
        }
    };


    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100">
            <div className="bg-white p-10 rounded-xl shadow-lg text-center">
                <h2 className="text-2xl font-bold mb-6">Login with Google</h2>
                <GoogleLogin
                    onSuccess={handleGoogleLogin}
                    onError={() => console.log("Login Failed")}
                    useOneTap
                    theme="outline"
                    size="large"
                />
            </div>
        </div>
    );
};

export default LoginPage;
