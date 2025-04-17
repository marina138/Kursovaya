import { useEffect, useState } from 'react';
import axios from 'axios';
import OrderForm from './Checkout';
import '../styles/cart.css';

export default function Cart() {
  const [cart, setCart] = useState({});
  const [total, setTotal] = useState(0);
  const [showOrderForm, setShowOrderForm] = useState(false);

  const fetchCart = () => {
    axios
      .get('http://localhost:8000/api/cart/', { withCredentials: true })
      .then(res => {
        setCart(res.data.cart);
        setTotal(res.data.total);
      })
      .catch(err => console.error(err));
  };

  useEffect(() => {
    fetchCart();
  }, []);

  const updateQuantity = (productId: string, action: 'increment' | 'decrement') => {
    axios
      .post(
        `http://localhost:8000/api/cart/update/${productId}/`,
        { action },
        { withCredentials: true }
      )
      .then(() => fetchCart())
      .catch(err => console.error(err));
  };

  const removeItem = (productId: string) => {
    axios
      .post(
        `http://localhost:8000/api/cart/remove/${productId}/`,
        {},
        { withCredentials: true }
      )
      .then(() => fetchCart())
      .catch(err => console.error(err));
  };

  return (
    <div>
      <header>
        <a href="/" className="logo">HOMOSEM</a>
        <nav>
          <a href="/">Главная</a>
          <a href="/catalog">Каталог</a>
          <a href="/cart">Корзина</a>
        </nav>
      </header>

      <div className="page-container">
        <main>
          {Object.keys(cart).length === 0 ? (
            <p>Корзина пуста</p>
          ) : (
            <>
              <div className="catalog-container">
                {Object.entries(cart).map(([id, item]: any) => (
                  <div className="product-card" key={id}>
                    <div className="product-image-wrapper">
                      <img
                        src={`http://localhost:8000${item.image}`}
                        alt={item.name}
                        className="product-image"
                      />
                    </div>
                    <div className="product-content">
                      <h3 className="product-name">{item.name}</h3>
                      <p className="product-price">{item.price} ₽</p>
                    </div>
                    <p>Количество: {item.quantity}</p>
                    <div className="button">
                      <button onClick={() => updateQuantity(id, 'increment')}>+</button>
                      <button onClick={() => updateQuantity(id, 'decrement')}>-</button>
                      <button onClick={() => removeItem(id)}>Удалить</button>
                    </div>
                  </div>
                ))}
              </div>

              <h3>Итого: {total} ₽</h3>

              {Object.keys(cart).length > 0 && (
                <>
                  <button
                    onClick={() => setShowOrderForm(true)}
                    className="add-to-cart-btn"
                  >
                    Оформить заказ
                  </button>

                  {showOrderForm && (
                    <OrderForm
                      onOrderPlaced={() => {
                        setCart({});
                        setTotal(0);
                        setShowOrderForm(false);
                      }}
                    />
                  )}
                </>
              )}
            </>
          )}
        </main>
      </div>
      <footer>
        <div className="footer-content">
          <p>© 2025 Магазин одежды. Все права защищены.</p>
          <p>Контакты: info@fashionstore.ru | +7 900 000 00 00</p>
        </div>
      </footer>
    </div>
  );
}