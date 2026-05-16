# Role-Based Access Control Testing Guide

## Overview
This document provides instructions for testing the role-based access control (RBAC) implementation in the Carbook application.

## Demo Accounts

Two demo accounts have been created and seeded into the database:

### Admin Account
- **Username:** `luxury_admin`
- **Email:** `admin@luxurydrive.com`
- **Password:** `admin123`
- **Role:** Admin

### Customer Account
- **Username:** `luxury_user`
- **Email:** `user@luxurydrive.com`
- **Password:** `user123`
- **Role:** Customer

## Testing Checklist

### ADMIN ACCOUNT TESTS

#### Navigation & Sidebar
- [ ] Login with admin account
- [ ] Verify sidebar shows:
  - Dashboard
  - **Manage Cars** (not "Browse Cars")
  - Bookings
  - Users
  - Profile
  - Logout

#### Dashboard (Admin)
- [ ] Dashboard loads and shows welcome message
- [ ] Statistics cards are displayed

#### Car Management (Admin)
- [ ] "Manage Cars" page loads
- [ ] "Add Car" button is visible
- [ ] Can click "Add Car" button to open dialog
- [ ] Can add a new car with the form:
  - Brand, Model, Year, License Plate (required)
  - Category, Status, Transmission, Fuel Type
  - Daily Rate, Seats, Color, Description
  - Image upload
- [ ] After adding car, it appears in the list
- [ ] Each car card shows "Book", "Edit", and "Delete" buttons
- [ ] Can click "Edit" button to modify car details
- [ ] Can click "Delete" button to remove car (with confirmation)
- [ ] After editing, changes are reflected in the list

#### Car Search & Filtering (Admin)
- [ ] Search by brand, model, license plate, or color works
- [ ] Category dropdown filters cars correctly
- [ ] Status dropdown filters by availability status

#### Profile
- [ ] Profile page loads

#### Logout
- [ ] Can logout with confirmation dialog
- [ ] Returns to landing page after logout
- [ ] Can log back in with admin account

---

### CUSTOMER ACCOUNT TESTS

#### Navigation & Sidebar
- [ ] Login with customer account
- [ ] Verify sidebar shows:
  - Dashboard
  - **Browse Cars** (not "Manage Cars")
  - My Bookings
  - Profile
  - Logout
- [ ] **Verify "Bookings" and "Users" menu items are NOT visible**

#### Dashboard (Customer)
- [ ] Dashboard loads and shows welcome message
- [ ] Statistics cards are displayed

#### Browse Cars (Customer)
- [ ] "Browse Cars" page loads
- [ ] "Add Car" button is **NOT visible** (admin-only feature)
- [ ] Search and filtering work the same as for admins
- [ ] Each car card shows **ONLY** the "Book" button
- [ ] **Verify "Edit" and "Delete" buttons are NOT visible**
- [ ] Can click "Book" button to book a car (if available)

#### Booking Dialog
- [ ] Booking form opens when clicking "Book"
- [ ] Can select start and end dates
- [ ] Can enter pickup and dropoff locations
- [ ] Total price is calculated correctly
- [ ] Can confirm booking
- [ ] Booking confirmation dialog appears
- [ ] Booked car status changes to "rented"

#### My Bookings
- [ ] "My Bookings" page loads
- [ ] Shows only the customer's own bookings
- [ ] Can view booking details
- [ ] Can cancel their own bookings (with confirmation)

#### Profile
- [ ] Profile page loads

#### Logout
- [ ] Can logout with confirmation dialog
- [ ] Returns to landing page after logout
- [ ] Can log back in with customer account

---

### BACKEND ACCESS CONTROL TESTS

#### Prevent Unauthorized Car Modifications
- [ ] If somehow a customer attempts to add/edit/delete a car via API/service call:
  - Expected: Service returns error message: "Admin access required to [add/edit/delete] cars"
  - Actual: _Test during development_

#### Prevent Booking Cross-Access
- [ ] Customer cannot view/cancel bookings of other users
  - Expected: Service returns error message: "You can only cancel your own bookings"
  - Customer bookings query only returns their own bookings

#### Session Management
- [ ] Admin role persists during session
- [ ] Customer role persists during session
- [ ] Logging out clears session
- [ ] Sidebar updates when logging in/out

---

## Implementation Details

### Files Modified

1. **utils/auth.py**
   - Added `Session.is_customer()` method
   - Added `Session.get_role()` method
   - Added `Session.has_role()` method
   - Added `@require_admin` decorator
   - Added `@require_role()` decorator factory

2. **services/car_service.py**
   - Added admin-only checks to `create()`, `update()`, `delete()` methods
   - Returns error messages for unauthorized access

3. **services/booking_service.py**
   - Enhanced `cancel_booking()` to check user owns the booking
   - Admins can cancel any booking; customers can only cancel their own

4. **ui/pages/browse_cars_page.py**
   - Added `is_admin` parameter to constructor
   - Conditionally shows/hides "Add Car" button
   - Conditionally shows/hides "Edit" and "Delete" buttons on each car card
   - Updated page title to "Manage Cars" for admins, "Browse Cars" for customers

5. **app.py**
   - Added `_get_nav_items_for_user()` method
   - Modified `_init_pages()` to load role-specific pages
   - Updated `_on_login_success()` to rebuild UI with role-specific navigation
   - Sidebar is now dynamic based on user role

---

## Expected Behavior Summary

| Feature | Admin | Customer |
|---------|-------|----------|
| Dashboard | ✓ | ✓ |
| Browse/Manage Cars | ✓ (Manage) | ✓ (Browse only) |
| Add Cars | ✓ | ✗ |
| Edit Cars | ✓ | ✗ |
| Delete Cars | ✓ | ✗ |
| Book Cars | ✓ | ✓ |
| View Bookings | ✓ (All) | ✓ (Own only) |
| Cancel Bookings | ✓ (All) | ✓ (Own only) |
| Manage Users | ✓ | ✗ |
| View Analytics | ✓ | ✗ |
| Profile | ✓ | ✓ |

---

## Notes

- The database `users` table already had a `role` column with ENUM('admin', 'customer')
- New registrations default to 'customer' role
- Admin accounts must be manually set in the database or created via demo data seeding
- All permission checks happen both in UI and backend service layer
- Backend protection ensures users cannot bypass UI restrictions via direct service calls
