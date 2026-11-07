# 🌿 GreenNest – Online Plant Nursery

GreenNest is a plant nursery e-commerce website developed using Python and Django. It provides a platform where users can explore different plants, browse categories, add products to their shopping cart, and place orders online.

## ✨ Features

- Browse indoor and outdoor plants.
- Explore plants by category.
- User registration and login.
- Add products to the shopping cart.
- Update quantities and remove products.
- Checkout with delivery details.
- Razorpay payment integration (Test Mode).
- View order history.
- Admin panel to manage products and orders.

## 🛠️ Technologies Used

- **Frontend:** HTML, CSS
- **Backend:** Python, Django
- **Database:** SQLite
- **Payment Integration:** Razorpay (Test Mode)
- **Development Tool:** Visual Studio Code

## 📂 Project Structure

```text
GreenNest/
│
├── greennest/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── store/
│   ├── migrations/
│   ├── static/
│   ├── templates/
│   ├── models.py
│   ├── views.py
│   └── urls.py
│
├── manage.py
├── .gitignore
└── README.md
```

## 🚀 How to Run the Project

1. Clone the repository:

   `git clone https://github.com/vjyothsna2312-maker/GreenNest.git`

2. Navigate to the project directory:

   `cd GreenNest`

3. Create and activate a virtual environment:

   `python -m venv venv`

   Windows:

   `venv\Scripts\activate`

4. Install dependencies:

   `pip install django python-dotenv razorpay`

5. Configure environment variables in a `.env` file.

6. Apply database migrations:

   `python manage.py migrate`

7. Start the development server:

   `python manage.py runserver`

8. Open `http://127.0.0.1:8000/` in your browser.

## 🌱 Future Enhancements

- Product search and filtering.
- Product reviews and ratings.
- Improved order tracking.
- Deployment to a cloud hosting platform.

## 👩‍💻 Developed By

**Vanapalli Jyothsna**

Electronics and Communication Engineering