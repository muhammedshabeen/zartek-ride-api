# 🚖 Ride Sharing API (Django REST Framework)

A backend REST API for ride-sharing functionality built using Django and Django REST Framework. Supports role-based actions for Riders and Drivers including ride creation, driver matching, ride acceptance, and ride status updates.

---

## 📦 Features

- User registration and authentication (Token-based)
- Rider and Driver roles
- Ride creation with nearest driver assignment (Haversine distance)
- Driver ride acceptance flow
- Ride status updates: STARTED, COMPLETED, CANCELLED
- Fetch rides by role
- Unit tests for core functionalities

---

## 🧰 Tech Stack

- Python 3.10+
- Django 4.x
- Django REST Framework
- Postgres
- Token Authentication (DRF built-in)
- Haversine formula for geolocation
- `unittest` for test cases

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/muhammedshabeen/zartek-ride-api.git
cd ride-share-api
```

### 2. Create Virtual Environment and Install Requirements

```bash
python -m venv venv
source venv/Scripts/activate  # Windows
pip install -r requirements.txt
```

### 3. Apply Migrations and Create Superuser

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 4. Run the Development Server

```bash
python manage.py runserver
```

---

## 🔐 Authentication

- Token-based (DRF `TokenAuthentication`)
- Pass token as header:  
  `Authorization: Token <your-token>`

---

## 🔗 API Endpoints

| Method | Endpoint                            | Description                         |
|--------|-------------------------------------|-------------------------------------|
| POST   | `/register`                         | Register a new user                 |
| POST   | `/login`                            | Login and get auth token            |
| POST   | `/rides/`                           | Create a ride (Rider only)          |
| POST   | `rides/<id>/accept/`                | Accept a ride (Driver only)         |
| POST   | `rides/<id>/update-status/`         | Update ride status (Driver only)    |
| GET    | `rides/my-rides`                    | Get rides related to user           |
| GET    | `rides`                             | Get All Rides                       |
| GET    | `rides/<id>/`                       | Get Detail Page                     |
| POST   | `rides/<pk>/match-driver/`          | If there is no driver to use this   |
| POST   | `/logot`                            | Logout Api                          |


---

## 🧪 Run Tests

```bash
python manage.py test
```

Test Cases:
- Login
- Register
- Logout
- Ride acceptance logic
- Ride matching logic
- Real time location update
- User-specific ride views

---

## 📁 Project Structure

```
ride-share-api/
├── ride_share_api/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── urls.py
│   ├── tests/
├── manage.py
├── requirements.txt
└── README.md
```

---

## 🙋 Author

**Muhammed Shabeen**  
📧 muhammedshabeen982@gmail.com  
📍 Python Django Developer  
🌐 [LinkedIn](https://www.linkedin.com/in/muhammadshabeenj/)

---

## 📝 Notes

- Roles: `'1'` for Rider, `'2'` for Driver
- Only drivers can accept or update ride status
- Riders automatically get matched to the closest available driver if coordinates are provided