# Vestaire

Digital Wardrobe with AI-powered image analysis to extract clothing details from photos and tags.

- **Stack:** Django (backend), Flutter (mobile app), Gemini API (AI), Cloudinary (image storage)

---

## 🚦 Project Status & TODO

- [x] **Django Backend:** Core features complete (see below)
- [ ] **Flutter Mobile App:** To be started next
- [ ] **API Adaptation:** Modify/extend endpoints as needed for mobile app integration
- [ ] **End-to-End Testing:** After Flutter integration

---

## ✅ Django Backend: Features Implemented

- **User Authentication & Profiles**
  - JWT-based registration, login, logout, password change, and profile management
  - User profile extension (phone, DOB, preferences)
- **Wardrobe Management**
  - CRUD for clothing items, categories, and images
  - Soft delete for items
  - Category auto-creation if not present
- **Image Handling**
  - Upload up to 5 images per item
  - Image validation, optimization, and thumbnail generation
  - Cloudinary integration for secure, scalable image storage
- **AI Integration**
  - Gemini Vision API for automatic extraction of clothing details (category, brand, color, size, etc.)
  - AI-powered description generation
  - AI analysis results stored and linked to items
- **API Design**
  - RESTful endpoints for all resources
  - Filtering, search, and ordering for item lists
  - Custom endpoints: trigger AI analysis, wardrobe stats, etc.
  - Comprehensive error handling and validation
- **Background Processing**
  - Celery + Redis for async AI/image tasks
- **Admin & Docs**
  - Django admin for all models
  - Interactive API docs: [Swagger UI](/api/docs/) & [Redoc](/api/redoc/) via drf-spectacular
- **Security & Best Practices**
  - Environment-based config with python-decouple
  - CORS, JWT, and production-ready settings

---

## 🏁 Next Steps

- Start Flutter mobile app development
- Adjust/extend API endpoints for mobile needs
- Integrate and test end-to-end flows
- Add more advanced features as needed (notifications, analytics, etc.)

---

## 📂 Repo Structure

- `server/` — Django backend (see above for features)
- `app/` — Flutter mobile app (to be developed)

---

## 📚 Learning & Docs

- See `server/learn/` for detailed backend guides, architecture, and best practices.

---

_This project is for learning Django, Flutter, and backend optimization concepts._
