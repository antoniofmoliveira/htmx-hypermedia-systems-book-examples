from os import environ
from flask import Flask, flash, redirect, render_template, request
import sqlite3

app = Flask(__name__)

app.config['SECRET_KEY'] = environ.get('SECRET_KEY')
app.config['SESSION_TYPE'] = 'memcached'


con = sqlite3.connect('contacts.db', check_same_thread=False)
cur = con.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS contacts(id integer primary key autoincrement, first_name text, last_name text, phone text, email text)''')

"""


Here is a succinct explanation of the `Contact` class definition:

**Class Methods:**

1. `__init__`: Initializes a new `Contact` object with `id`, `first`, `last`, `phone`, 
and `email` attributes.
2. `from_dict`: Creates a new `Contact` object from a dictionary containing contact data.
3. `errors`: Returns a dictionary of error messages for missing contact data.
4. `create`: Inserts a new contact into the database.
5. `get`: Retrieves a contact from the database by `id`.
6. `update`: Updates an existing contact in the database.
7. `delete`: Deletes a contact from the database by `id`.
8. `all`: Retrieves a list of all contacts from the database, paginated by `page`.
9. `search`: Retrieves a list of contacts from the database that match a search term.
10. `email_exists`: Checks if an email address already exists in the database.

Note that this class appears to be designed to interact with a SQLite database, and uses 
the `cur` and `con` objects to execute SQL queries.
"""


class Contact:
    def __init__(self, id, first, last, phone, email):
        """
        Initializes a new Contact object with the given attributes.

        Args:
            id (int): The unique identifier of the contact.
            first (str): The first name of the contact.
            last (str): The last name of the contact.
            phone (str): The phone number of the contact.
            email (str): The email address of the contact.

        Returns:
            None
        """
        self.id = id
        self.first = first
        self.last = last
        self.phone = phone
        self.email = email

    def __str__(self):
        """
        Returns a string representation of the contact object.
        """
        return f"{self.id}: {self.first} {self.last}, | {self.email} | {self.phone}"

    @staticmethod
    def from_dict(data):
        """
        Creates a new Contact object from a dictionary containing contact data.

        Args:
            data (dict): A dictionary containing contact data with keys 'id', 'first_name', 'last_name', 'phone', and 'email'.

        Returns:
            Contact: A new Contact object with the given attributes.
        """
        return Contact(
            id=data.get('id'),
            first=data.get('first_name'),
            last=data.get('last_name'),
            phone=data.get('phone'),
            email=data.get('email')
        )

    @property
    def errors(self):
        """
        Returns a dictionary of error messages for the contact's attributes.

        The dictionary contains error messages for the 'first', 'last', 'phone', and 'email' attributes.
        If an attribute is not empty, its corresponding error message is None.

        Returns:
            dict: A dictionary of error messages for the contact's attributes.
        """
        return {
            'first': 'First name is required.' if not self.first else None,
            'last': 'Last name is required.' if not self.last else None,
            'phone': 'Phone is required.' if not self.phone else None,
            'email': 'Email is required.' if not self.email else None
        }

    @classmethod
    def create(cls, contact):
        """
        Creates a new contact in the database.

        Args:
            contact (Contact): The contact object to be created.

        Returns:
            bool: True if the contact was successfully created, False otherwise.
        """
        cur.execute('''INSERT INTO contacts(first_name, last_name, phone, email) VALUES(?, ?, ?, ?)''',
                    (contact.first, contact.last, contact.phone, contact.email))
        con.commit()
        return True

    @classmethod
    def get(cls, contact_id):
        """
        Retrieves a contact from the database by its ID.

        Args:
            contact_id (int): The ID of the contact to be retrieved.

        Returns:
            Contact: The contact object retrieved from the database.
        """
        cur.execute('''SELECT * FROM contacts WHERE id=?''', (contact_id,))
        return cls(*cur.fetchone())

    @classmethod
    def update(cls, contact):
        """
        Updates an existing contact in the database.

        Args:
            contact (Contact): The contact object to be updated.

        Returns:
            bool: True if the contact was successfully updated, False otherwise.
        """
        cur.execute('''UPDATE contacts SET first_name=?, last_name=?, phone=?, email=? WHERE id=?''',
                    (contact.first, contact.last, contact.phone, contact.email, contact.id))
        con.commit()
        return True

    @classmethod
    def delete(cls, contact_id):
        """
        Deletes a contact from the database by its ID.

        Args:
            contact_id (int): The ID of the contact to be deleted.

        Returns:
            None
        """
        cur.execute('''DELETE FROM contacts WHERE id=?''', (contact_id,))
        con.commit()

    @classmethod
    def all(cls, page=1):
        """
        Retrieves all contacts from the database, paginated by a specified page number.

        Args:
            page (int, optional): The page number to retrieve. Defaults to 1.

        Returns:
            list: A list of Contact objects representing the contacts on the specified page.
        """
        cur.execute('''SELECT * FROM contacts LIMIT 10 OFFSET ?''',
                    ((page - 1) * 10,))
        return [cls(*row) for row in cur.fetchall()]

    @classmethod
    def search(cls, search_term):
        """
        Searches for contacts in the database based on a given search term.

        Args:
            search_term (str): The term to search for in the contacts' first name, last name, phone, and email.

        Returns:
            list: A list of Contact objects representing the contacts that match the search term.
        """
        cur.execute('''SELECT * FROM contacts WHERE first_name LIKE ?
                        OR last_name LIKE ?
                        OR phone LIKE ?
                        OR email LIKE ?''',
                    ('%' + search_term + '%',) * 4)
        return [cls(*row) for row in cur.fetchall()]

    @classmethod
    def email_exists(cls, email):
        """
        Checks if a given email address already exists in the database.

        Args:
            email (str): The email address to check for.

        Returns:
            bool: True if the email address exists, False otherwise.
        """
        cur.execute('''SELECT COUNT(*) FROM contacts WHERE email=?''', (email,))
        return cur.fetchone()[0] > 0


@app.route("/")
def index():
    """
    Defines a route for the root URL ("/") of the application.

    Returns:
        redirect: A redirect to the "/contacts" URL.
    """
    return redirect("/contacts")


@app.route("/contacts")
def contacts():
    """
    Defines a route for the "/contacts" URL of the application.

    Handles GET requests to the "/contacts" URL, retrieving a list of contacts
    based on a search term and pagination. If a search term is provided, it
    searches for contacts matching the term. Otherwise, it retrieves a list of
    contacts for the specified page.

    Args:
        q (str): The search term to search for in the contacts' first name, last name, phone, and email.
        page (int): The page number to retrieve contacts for.

    Returns:
        render_template: A rendered HTML template ("index.html") with a list of contacts and the current page number.
    """
    search = request.args.get("q")
    page = int(request.args.get("page", 1))
    if search is not None:
        contacts_set = Contact.search(search)
        if request.headers.get('HX-Trigger') == 'search':
            return render_template("rows.html", contacts=contacts_set)
    else:
        contacts_set = Contact.all(page)
    return render_template("index.html", contacts=contacts_set, page=page)


@app.route("/contacts/new", methods=['GET'])
def contacts_new_get():
    """
    Defines a route for the "/contacts/new" URL of the application, handling GET requests.

    Returns a rendered HTML template ("new.html") with a new contact object.

    Returns:
        render_template: A rendered HTML template ("new.html") with a new contact object.
    """
    contact = Contact(0, "", "", "", "")
    return render_template("new.html", contact=contact)


@app.route("/contacts/new", methods=['POST'])
def contacts_new():
    """
    Creates a new contact by extracting the first name, last name, phone number, and email from the request form.
    If the contact is successfully created, a flash message is displayed and the user is redirected to the contacts page.
    If the contact creation fails, the user is returned to the new contact form with the contact object and an error message.

    Parameters:
        None

    Returns:
        If the contact is successfully created, the user is redirected to the contacts page.
        If the contact creation fails, the user is returned to the new contact form with the contact object and an error message.
    """
    c = Contact(
        None,
        request.form['first_name'],
        request.form['last_name'],
        request.form['phone'],
        request.form['email'])
    if Contact.create(c):
        flash("Created New Contact!")
        return redirect("/contacts")
    else:
        return render_template("new.html", contact=c)


@app.route("/contacts/<contact_id>")
def contacts_view(contact_id=0):
    """
    Defines a route for the "/contacts/<contact_id>" URL of the application.

    Parameters:
        contact_id (int): The ID of the contact to be viewed.

    Returns:
        render_template: A rendered HTML template ("show.html") with the contact object.
    """
    contact = Contact.get(contact_id)
    return render_template("show.html", contact=contact)


@app.route("/contacts/<contact_id>/edit", methods=["GET"])
def contacts_edit_get(contact_id=0):
    """
    Defines a route for the "/contacts/<contact_id>/edit" URL of the application, handling GET requests.

    Parameters:
        contact_id (int): The ID of the contact to be edited.

    Returns:
        render_template: A rendered HTML template ("edit.html") with the contact object.
    """
    contact = Contact.get(contact_id)
    return render_template("edit.html", contact=contact)


@app.route("/contacts/<contact_id>/edit", methods=["POST"])
def contacts_edit_post(contact_id=0):
    """
    Defines a route for the "/contacts/<contact_id>/edit" URL of the application, handling POST requests.

    Parameters:
        contact_id (int): The ID of the contact to be edited.

    Returns:
        redirect: Redirects to the contact's page if the contact is successfully updated.
        render_template: Renders the "edit.html" template with the contact object if the update fails.
    """
    c = Contact.get(contact_id)
    c.first = request.form['first_name']
    c.last = request.form['last_name']
    c.phone = request.form['phone']
    c.email = request.form['email']
    if Contact.update(c):
        flash("Updated Contact!")
        return redirect("/contacts/" + str(contact_id))
    else:
        return render_template("edit.html", contact=c)


@app.route("/contacts/<contact_id>", methods=["DELETE"])
def contacts_delete(contact_id=0):
    """
    Deletes a contact from the database by its ID.

    Parameters:
        contact_id (int): The ID of the contact to be deleted. Defaults to 0.

    Returns:
        redirect: A redirect response to the "/contacts" URL with a status code of 303.
    """
    contact = Contact.find(contact_id)
    contact.delete()
    flash("Deleted Contact!")
    return redirect("/contacts", 303)


@app.route("/contacts/<contact_id>/email", methods=["GET"])
def contacts_email_get(contact_id=0):
    """
    Defines a route for the "/contacts/<contact_id>/email" URL of the application, handling GET requests.

    Parameters:
        contact_id (int): The ID of the contact. Defaults to 0.

    Returns:
        str: An error message if the email exists, otherwise an empty string.
    """
    c = Contact(0, "", "", "", "")
    c.email = request.args.get('email')
    if Contact.email_exists(c.email):
        errors = c.errors
        errors['email'] = 'Email already exists.'
    return errors.get('email') or ""
