import React, { useState, useEffect } from 'react';
import axios from 'axios';
import '../styles/Checkout.css';

// Функция для получения CSRF-токена из cookies
function getCookie(name: string): string | null {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + '=') {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function OrderForm({ onOrderPlaced }: { onOrderPlaced: () => void }) {
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [email, setEmail] = useState('');
  const [address, setAddress] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [csrfToken, setCsrfToken] = useState<string | null>(null);
  const [isLoadingToken, setIsLoadingToken] = useState(true); // Флаг загрузки токена

  // Получение CSRF-токена при загрузке компонента
  useEffect(() => {
    const fetchCsrfToken = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/get-csrf-token/', {
          withCredentials: true,
        });
        console.log('CSRF-токен получен:', response.data.csrfToken);
        setCsrfToken(response.data.csrfToken);
      } catch (error: any) {
        console.error('Ошибка получения CSRF-токена:', error.response || error);
        setError('Не удалось получить CSRF-токен');
      } finally {
        setIsLoadingToken(false); // Завершаем загрузку токена
      }
    };
    fetchCsrfToken();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Проверка валидации формы
    if (!name || !phone || !email || !address) {
      setError('Все поля обязательны');
      return;
    }
    if (name.length < 3) {
      setError('ФИО должно быть не короче 3 символов');
      return;
    }
    if (!phone.match(/^\+7\d{10}$/)) {
      setError('Введите номер в формате +7XXXXXXXXXX');
      return;
    }
    if (!email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
      setError('Введите корректный адрес электронной почты');
      return;
    }
    if (address.length < 10) {
      setError('Адрес слишком короткий, укажите более подробный адрес');
      return;
    }

    // Проверка загрузки токена
    if (isLoadingToken) {
      setError('CSRF-токен ещё загружается. Пожалуйста, подождите.');
      console.error('CSRF-токен ещё загружается');
      return;
    }

    // Используем CSRF-токен из состояния или cookies
    const token = csrfToken || getCookie('csrftoken');
    if (!token) {
      setError('CSRF-токен не найден. Пожалуйста, обновите страницу.');
      console.error('CSRF-токен отсутствует');
      return;
    }

    try {
      const cartResponse = await axios.get('http://localhost:8000/api/cart/', {
        withCredentials: true,
      });
      const cartItems = Object.entries(cartResponse.data.cart || {}).map(([id, item]: any) => ({
        product_id: parseInt(id),
        name: item.name,
        price: item.price,
        quantity: item.quantity,
      }));

      if (!cartItems.length) {
        setError('Корзина пуста');
        return;
      }

      const payload = { name, phone, email, address, items: cartItems };
      console.log('Отправляемые данные:', payload);
      console.log('Используемый CSRF-токен:', token);

      const res = await axios.post('http://localhost:8000/api/order/', payload, {
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': token, // Используем токен
        },
        withCredentials: true,
      });

      console.log('Ответ сервера:', res.data);
      setSuccess(res.data.message);
      setError('');
      setName('');
      setPhone('');
      setEmail('');
      setAddress('');
      onOrderPlaced();
    } catch (err: any) {
      console.error('Ошибка при отправке заказа:', err.response || err);
      setError(
        err.response?.data?.error ||
        err.response?.data?.detail ||
        'Ошибка оформления заказа'
      );
    }
  };

  return (
    <div className="order-form">
      <h2>Оформление заказа</h2>
      <input
        type="text"
        placeholder="ФИО"
        className="block w-full mb-2 p-2 border rounded"
        value={name}
        onChange={e => setName(e.target.value)}
      />
      <input
        type="text"
        placeholder="Телефон (+7XXXXXXXXXX)"
        className="block w-full mb-2 p-2 border rounded"
        value={phone}
        onChange={e => setPhone(e.target.value)}
      />
      <input
        type="email"
        placeholder="Электронная почта"
        className="block w-full mb-2 p-2 border rounded"
        value={email}
        onChange={e => setEmail(e.target.value)}
      />
      <input
        type="text"
        placeholder="Адрес доставки"
        className="block w-full mb-2 p-2 border rounded"
        value={address}
        onChange={e => setAddress(e.target.value)}
      />
      {error && <p className="text-red-500">{error}</p>}
      {success && <p className="text-green-600">{success}</p>}
      <button onClick={handleSubmit} className="submit-button" disabled={isLoadingToken}>
        {isLoadingToken ? 'Загрузка...' : 'Оформить заказ'}
      </button>
    </div>
  );
}

export default OrderForm;