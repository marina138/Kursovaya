import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Catalog from "./pages/Catalog";
import Cart from "./pages/Cart";
import Profile from "./pages/Profile";

const AppRoutes = () => (
  <Router>
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/catalog" element={<Catalog />} />
      <Route path="/cart" element={<Cart />} />
      <Route path="/profile" element={<Profile />} />
    </Routes>
  </Router>
);

export default AppRoutes;
