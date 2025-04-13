import { Link } from "react-router-dom";

const Home = () => {
  return (
    <div>
      <h1>Добро пожаловать в магазин одежды!</h1>
      <p>Выберите категорию товаров:</p>
      <Link to="/catalog" style={{ padding: "10px", background: "blue", color: "white", textDecoration: "none", borderRadius: "5px" }}>
        Перейти в каталог
      </Link>
    </div>
  );
};

export default Home;
