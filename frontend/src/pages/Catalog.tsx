import { useEffect, useState } from "react";
import { fetchProducts } from "../api";
import React, { useEffect, useState } from 'react';
import axiosClient from '../axiosClient';

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
const CatalogPage = () => {
  const [products, setProducts] = useState([]);

  useEffect(() => {
    axiosClient.get('products/')
      .then(response => {
        setProducts(response.data);
      })
      .catch(error => {
        console.error('Ошибка при загрузке товаров:', error);
      });
  }, []);

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4">
      {products.map(product => (
        <div key={product.id} className="p-4 border rounded shadow">
          <h2 className="font-semibold">{product.name}</h2>
          <p>{product.description}</p>
          <p className="text-lg font-bold">{product.price}₽</p>
        </div>
      ))}
    </div>
  );
};

export default CatalogPage;
export default Catalog;
