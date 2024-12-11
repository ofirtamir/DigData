# SQLAlchemy System - Assignment 2

## 📄 Project Overview
This project implements a database management system using **SQLAlchemy**, focusing on user interactions, media items, and history tracking. The system adheres to the principles of object-relational mapping (ORM) and showcases secure user authentication and dynamic data handling.

---

## 🛠️ Features
1. **User Management**:
   - Securely store user passwords using the `bcrypt` library.
   - Add user history and calculate media item title lengths.

2. **Media Items**:
   - Manage media items with properties like title, production year, and title length.

3. **History Tracking**:
   - Track user interactions with media items, including timestamps.

4. **Repositories**:
   - User and MediaItem repositories for database operations.
   - User validation and statistical queries.

5. **Services**:
   - Entry points for managing users and media items.
   - Functions for user creation, history management, and data retrieval.

---

## 📋 System Architecture
The system is built with three main components:
1. **Entities**: Define the database models (`User`, `MediaItem`, and `History`).
2. **Repositories**: Handle data access logic for each entity.
3. **Services**: Implement business logic for use-case scenarios.

---

## 🚀 How to Use
1. Clone the repository:
   ```bash
   git clone <repository-url>
