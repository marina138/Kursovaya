import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axiosClient from '../axiosClient';
import '../styles/index.css';

interface Product {
  id: number;
  name: string;
  price: number;
  image: string;
}

const Home = () => {
  const [products, setProducts] = useState<Product[]>([]);

  useEffect(() => {
    axiosClient
      .get('products/')
      .then((res) => {
        setProducts(res.data.slice(0, 10)); // Берем первые 10 товаров
      })
      .catch((err) => console.error('Ошибка загрузки товаров:', err));
  }, []);

  const handleAddToCart = (productId: number) => {
    axiosClient
      .post(`cart/add/${productId}/`)
      .then(() => {
        alert('Товар добавлен в корзину!');
      })
      .catch((error) => {
        console.error('Ошибка при добавлении в корзину:', error);
        alert('Ошибка при добавлении товара в корзину');
      });
  };

  return (
    <div>
      <header>
        <Link to="/" className="logo">HOMOSEM</Link>
        <nav>
          <Link to="/">Главная</Link>
          <Link to="/catalog">Каталог</Link>
          <Link to="/cart">Корзина</Link>
        </nav>
      </header>

      <section className="hero">
        <div className="hero-content"></div>
      </section>

      <section className="about">
        <h2>Немного о нас:</h2>
        <p>
          Московский бренд одежды, основанный в 2017 году, выпускающий вещи в лимитированном кол-ве.<br />
          Наша задача — создавать качественные и стильные вещи по доступной цене.<br />
          За всё время работы мы одели более 15 000 счастливых покупателей.<br />
          Ежедневно работаем над улучшением всех процессов. Если у вас есть предложения или идеи — обращайтесь в поддержку!
        </p>
      </section>

      <section className="popular-products">
        <h2>Популярные товары</h2>
        <div className="product-grid">
          {products.map((product) => (
            <div className="product-card" key={product.id}>
              <img src={product.image} alt={product.name} />
              <h3>{product.name}</h3>
              <p>{product.price} ₽</p>
              <button
                className="add-to-cart-btn"
                onClick={() => handleAddToCart(product.id)}
              >
                Добавить в корзину
              </button>
            </div>
          ))}
        </div>
      </section>

      <footer>
        <div className="footer-content">
          <p>&copy; 2025 Магазин одежды. Все права защищены.</p>
          <p>Контакты: info@fashionstore.ru | +7 900 000 00 00</p>
        </div>
      </footer>
    </div>
  );
};

export default Home;