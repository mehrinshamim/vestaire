### 1. **Django’s Built-in Users & Groups**

#### **Users**
- Django comes with a built-in `User` model (`django.contrib.auth.models.User`).
- Each user has fields like `username`, `password`, `email`, `first_name`, `last_name`, `is_staff`, `is_superuser`, etc.
- Used for authentication (login/logout), permissions, and associating data with users.
- You can manage users from the Django admin (as you see in your screenshot).

#### **Groups**
- Groups are a way to bundle permissions together.
- You can assign users to one or more groups.
- Each group can have a set of permissions (e.g., “Editors” can edit articles, “Moderators” can delete comments).
- This makes permission management easier for large projects.

**Summary:**  
- **Users:** Individual accounts for people using your app/admin.
- **Groups:** Collections of permissions you can assign to users.

---

### 2. **Is there a UI to test endpoints like Swagger UI in FastAPI?**

**Yes! Django REST Framework (DRF) provides a built-in browsable API and can be extended with Swagger or Redoc.**

#### **Browsable API (DRF)**
- If you use DRF, you automatically get a web UI for your API endpoints.
- Just go to your API URLs in the browser (e.g., `/api/items/`).
- You can view, filter, and test endpoints directly in the browser.

#### **Swagger UI / Redoc**
- For a more advanced, interactive API documentation (like FastAPI’s Swagger UI), you can use:
  - **drf-yasg** ([GitHub](https://github.com/axnsan12/drf-yasg)): Adds Swagger and Redoc UI to your Django project.
  - **drf-spectacular** ([GitHub](https://github.com/tfranzel/drf-spectacular)): Another OpenAPI/Swagger generator for DRF.


  --- drf-spectacular is better , yasg is older version