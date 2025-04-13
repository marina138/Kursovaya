import { useEffect, useState } from "react";
import { fetchProducts } from "../api";

interface Product {
  id: number;
  name: string;
  price: number;
  image: string;
}

const Catalog = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchProducts()
      .then((data) => {
        setProducts(data);
        setLoading(false);
      })
      .catch((err) => {
        setError("Ошибка загрузки товаров");
        setLoading(false);
      });
  }, []);

  if (loading) return <p>Загрузка...</p>;
  if (error) return <p>{error}</p>;

  return (
    <div>
      <h1>Каталог товаров</h1>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "20px" }}>
        {products.length === 0 ? (
          <p>Товары не найдены</p>
        ) : (
          products.map((product) => (
            <div key={product.id} style={{ border: "1px solid #ddd", padding: "10px" }}>
              <img src={product.image} alt={product.name} width="100" />
              <h3>{product.name}</h3>
              <p>Цена: {product.price} ₽</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Catalog;
