We need a backend system that can manage sales invoices and record related transactions. The system should allow users to create, update, view, and manage invoices. Additionally, it should keep track of basic transaction records whenever an invoice is created or paid. A very simple frontend is optional, but not mandatory.

---

### **Backend Requirements (Django \+ DRF)**

Use Django and Django REST Framework.

* **Core Features**:  
  * **Invoice Creation**:  create new invoices with customer details and invoice items.  
  * **Invoice Listing & Retrieval**: List invoices and view details of a single invoice.  
  * **Invoice Payment**: Mark invoices as paid and record a related transaction.  
  * **Transactions**: When an invoice is created, record a *Sale* transaction. When an invoice is paid, record a *Payment* transaction.

* **Business Logic**:  
  * Total amount should be auto-calculated from items.  
  * Invoice must have at least one item.  
  * Payment should only be allowed if the invoice is in **Pending** status.  
  * Totals should always match with items.

* **Validation**:  
  * Each invoice must have unique reference/number.  
  * Totals cannot be negative.  
  * Payment status must update correctly.

* **Authentication**: Add basic token authentication. Only authenticated users should access invoice APIs. (JWT)

  ---

  ### 

  ### 

  ### 

  ### 

  ### **Optional Frontend (Bonus)**

  ### A simple UI is optional but will be considered a plus.

* **Functions**:  
  * Create invoice form  
  * List invoices in a table  
  * View invoice details  
  * Button to mark invoice as paid

* **Stack**: Can be ReactJS, NextJS, or simple HTML \+ JavaScript fetch calls.

  ---

  ### **Deliverables**

1. Django project with working APIs (Invoices \+ Transactions).  
2. Database migrations and seed data if needed.  
3. API documentation (Swagger/OpenAPI or DRF built-in).  
4. Minimal test coverage for invoice creation and payment.  
5. (Optional) A lightweight frontend demo.

   ---

   ### **Submission**

* Upload the project code to **GitHub** with a proper commit history (not a single bulk upload).  
* Document API usage clearly in README or Swagger.  
* A short live test/demo (hosted on PythonAnywhere/Heroku) or a quick video walkthrough is strongly encouraged.  
* Share the GitHub link and any demo link/video once complete.

  ---


**Timeline**

The expected duration for this task is **72 hours**. Focus on getting the main functionality working first; refinements can follow.