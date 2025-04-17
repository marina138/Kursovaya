import React, { useEffect, useState } from 'react';
import axios from 'axios';
import axiosClient from '../axiosClient';
import '../styles/catalog.css';

interface Product {
  id: number;
  name: string;
  price: number;
  image: string;
  category: string;
}

interface Category {
  id: number;
  name: string;
}

const CatalogPage: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [query, setQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<number | ''>('');
  const [minPrice, setMinPrice] = useState<number | ''>('');
  const [maxPrice, setMaxPrice] = useState<number | ''>('');


  useEffect(() => {
       axios.get('http://localhost:8000/api/products/')
      .then(res => setProducts(res.data))
      .catch(err => console.error(err));

    axios.get('http://localhost:8000/api/categories/')
      .then(res => setCategories(res.data))
      .catch(err => console.error(err));
  }, []);

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setQuery(value);
    const filtered = products.filter(p =>
      p.name.toLowerCase().includes(value.toLowerCase())
    );
    setFilteredProducts(filtered);
  };

  const handleCategoryChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedCategory(e.target.value === '' ? '' : parseInt(e.target.value));
  };

  const handleMaxPriceChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setMaxPrice(e.target.value === '' ? '' : parseInt(e.target.value));
  };
   const handleMinPriceChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setMinPrice(e.target.value === '' ? '' : parseInt(e.target.value));
  };

    const handleAddToCart = (productId: number) => {
      axiosClient.post(`cart/add/${productId}/`)
        .then(() => {
          alert('Товар добавлен в корзину');
        })
        .catch((error) => {
          console.error('Ошибка при добавлении в корзину:', error);
        });
    };

console.log(products.map(p => p.category));
// Вспомогательная функция
const getCategoryNameById = (id: number | ''): string => {
  const category = categories.find(cat => cat.id === id);
  return category ? category.name : '';
};

// Фильтрация товаров
const filteredProducts = products.filter(product => {
  const matchesQuery = product.name.toLowerCase().includes(query.toLowerCase());
  const matchesCategory =
    selectedCategory === '' || product.category.id === selectedCategory;
  const matchesPrice = maxPrice === '' || product.price <= maxPrice;
  const matchesPrice2 = minPrice === '' || product.price >= minPrice;
  return matchesQuery && matchesCategory && matchesPrice && matchesPrice2;
});


  return (
    <>
      <header>
        <a href="/" className="logo">HOMOSEM</a>
        <nav>
          <a href="/">Главная</a>
          <a href="/catalog">Каталог</a>
          <a href="/cart">Корзина</a>
        </nav>
      </header>

      <main>
        <div className="filters">
        <input
          type="text"
          placeholder="Поиск по названию"
          value={query}
          onChange={handleSearch}
        />
        <select value={selectedCategory} onChange={handleCategoryChange}>
          <option value="">Все категории</option>
          {categories.map(cat => (
            <option key={cat.id} value={cat.id}>{cat.name}</option>
          ))}
        </select>
        <input
          type="number"
          placeholder="Макс. цена"
          value={maxPrice}
          onChange={handleMaxPriceChange}
        />
        <input
            type="number"
            placeholder="Мин. цена"
            value={minPrice}
            onChange={handleMinPriceChange}
          />
      </div>

        <div className="catalog-container">
          {filteredProducts.map((product) => (
            <div className="product-card" key={product.id}>
              <div className="product-image-wrapper">
                <img
                  src={product.image}
                  alt={product.name}
                  className="product-image"
                />
              </div>
              <div className="product-content">
                <h3 className="product-name">{product.name}</h3>
                <p className="product-price">{product.price} ₽</p>
                <button
                  className="add-to-cart-btn"
                  onClick={() => handleAddToCart(product.id)}
                >
                  Добавить в корзину
                </button>
              </div>
            </div>
          ))}
        </div>
      </main>

      <footer>
        <div className="footer-content">
          <p>&copy; 2025 Магазин одежды. Все права защищены.</p>
          <p>Контакты: info@fashionstore.ru | +7 900 000 00 00</p>
        </div>
      </footer>
    </>
  );
};

export default CatalogPage;
