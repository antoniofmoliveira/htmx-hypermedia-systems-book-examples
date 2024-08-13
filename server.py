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

Here is a succinct explanation of the `Contact` class and its methods:

**Class Overview**

The `Contact` class represents a contact with attributes such as `id`, `first_name`, 
`last_name`, `phone`, and `email`. It provides methods for creating, retrieving, 
updating, and deleting contacts from a database.

**Methods**

1. `__init__(self, id, first, last, phone, email)`:
	* Initializes a `Contact` object with the provided attributes.
2. `from_dict(data)`:
	* Creates a `Contact` object from a dictionary containing contact information.
3. `errors`:
	* Returns a dictionary containing error messages for invalid contact information.
4. `create(cls, contact)`:
	* Creates a new contact in the database.
5. `get(cls, contact_id)`:
	* Retrieves a contact from the database based on the provided contact ID.
6. `update(cls, contact)`:
	* Updates an existing contact in the database.
7. `delete(cls, contact_id)`:
	* Deletes a contact from the database based on the provided contact ID.
8. `all(cls)`:
	* Retrieves all contacts from the database.
9. `search(cls, search_term)`:
	* Searches for contacts in the database based on the provided search term.

Note that the `cur` and `con` variables used in the methods are assumed to be a database 
cursor and connection object, respectively, which are not defined in the provided code snippet.
"""


class Contact:
    def __init__(self, id, first, last, phone, email):
        """
        Initializes a Contact object.

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

    @staticmethod
    def from_dict(data):
        """
        Creates a Contact object from a dictionary.

        Args:
            data (dict): A dictionary containing the contact information.
                It should have the following keys:
                - 'id' (int): The unique identifier of the contact.
                - 'first_name' (str): The first name of the contact.
                - 'last_name' (str): The last name of the contact.
                - 'phone' (str): The phone number of the contact.
                - 'email' (str): The email address of the contact.

        Returns:
            Contact: A Contact object created from the dictionary data.
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
        Returns a dictionary containing error messages for invalid contact information.

        The dictionary keys are the field names ('first', 'last', 'phone', 'email') and the values are the corresponding error messages.
        If a field is valid, its corresponding value in the dictionary will be None.

        Returns:
            dict: A dictionary containing error messages for invalid contact information.
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
            cls (class): The Contact class.
            contact (Contact): A Contact object containing the contact information.

        Returns:
            bool: True if the contact is created successfully.
        """
        cur.execute('''INSERT INTO contacts(first_name, last_name, phone, email) VALUES(?, ?, ?, ?)''',
                    (contact.first, contact.last, contact.phone, contact.email))
        con.commit()
        return True

    @classmethod
    def get(cls, contact_id):
        """
        Retrieves a contact from the database based on the provided contact ID.

        Parameters:
            cls (class): The class object.
            contact_id (int): The ID of the contact to retrieve.

        Returns:
            Contact: An instance of the Contact class representing the retrieved contact.

        Raises:
            None
        """
        cur.execute('''SELECT * FROM contacts WHERE id=?''', (contact_id,))
        return cls(*cur.fetchone())

    @classmethod
    def update(cls, contact):
        """
        Updates an existing contact in the database.

        Args:
            cls (class): The Contact class.
            contact (Contact): A Contact object containing the updated contact information.

        Returns:
            bool: True if the contact is updated successfully.
        """
        cur.execute('''UPDATE contacts SET first_name=?, last_name=?, phone=?, email=? WHERE id=?''',
                    (contact.first, contact.last, contact.phone, contact.email, contact.id))
        con.commit()
        return True

    @classmethod
    def delete(cls, contact_id):
        """
        Deletes a contact from the database based on the provided contact ID.

        Parameters:
            cls (class): The class object.
            contact_id (int): The ID of the contact to delete.

        Returns:
            None
        """
        cur.execute('''DELETE FROM contacts WHERE id=?''', (contact_id,))
        con.commit()

    @classmethod
    def all(cls):
        """
        Retrieves all contacts from the database.

        Parameters:
            cls (class): The Contact class.

        Returns:
            list: A list of Contact objects representing all contacts in the database.
        """
        cur.execute('''SELECT * FROM contacts''')
        return [cls(*row) for row in cur.fetchall()]

    @classmethod
    def search(cls, search_term):
        """
        Searches for contacts in the database based on the provided search term.

        Args:
            cls (class): The Contact class.
            search_term (str): The term to search for in the contacts.

        Returns:
            list: A list of Contact objects matching the search term.
        """
        cur.execute('''SELECT * FROM contacts WHERE first_name LIKE ?
                        OR last_name LIKE ?
                        OR phone LIKE ?
                        OR email LIKE ?''',
                    ('%' + search_term + '%',) * 4)
        return [cls(*row) for row in cur.fetchall()]


@app.route("/")
def index():
    """
    A function that serves as the route handler for the root URL ("/").
    It redirects the user to the "/contacts" URL.

    Returns:
        A redirect response object that redirects the user to the "/contacts" URL.
    """
    return redirect("/contacts")


@app.route("/contacts")
def contacts():
    """
    A route handler function for the "/contacts" URL.

    Retrieves the search query parameter "q" from the request arguments.
    If the search query is not None, it searches for contacts in the database
    based on the provided search term. Otherwise, it retrieves all contacts
    from the database.

    Parameters:
        None

    Returns:
        A rendered HTML template ("index.html") with the contacts data.
    """
    search = request.args.get("q")
    if search is not None:
        contacts_set = Contact.search(search)
    else:
        contacts_set = Contact.all()
    return render_template("index.html", contacts=contacts_set)


@app.route("/contacts/new", methods=['GET'])
def contacts_new_get():
    """
    A route handler function for the "/contacts/new" URL that handles GET requests.

    Creates a new Contact object with default values and renders the "new.html" template,
    passing the new Contact object as a parameter.

    Parameters:
        None

    Returns:
        A rendered HTML template ("new.html") with the new Contact object data.
    """
    contact = Contact(0, "", "", "", "")
    return render_template("new.html", contact=contact)


@app.route("/contacts/new", methods=['POST'])
def contacts_new():
    """
    A route handler function for the "/contacts/new" URL that handles POST requests.

    Creates a new Contact object with the provided form data and attempts to create it in the database.
    If the creation is successful, a flash message is displayed and the user is redirected to the "/contacts" URL.
    If the creation fails, the user is shown the "new.html" template with the new Contact object data.

    Parameters:
        None

    Returns:
        - If the creation is successful: A redirect to the "/contacts" URL.
        - If the creation fails: A rendered HTML template ("new.html") with the new Contact object data.
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
    A route handler function for the "/contacts/<contact_id>" URL.

    Retrieves a contact from the database based on the provided contact ID and renders the "show.html" template,
    passing the retrieved contact as a parameter.

    Parameters:
        contact_id (int): The ID of the contact to retrieve.

    Returns:
        A rendered HTML template ("show.html") with the retrieved contact data.
    """
    contact = Contact.get(contact_id)
    return render_template("show.html", contact=contact)


@app.route("/contacts/<contact_id>/edit", methods=["GET"])
def contacts_edit_get(contact_id=0):
    """
    Retrieves a contact from the database based on the provided contact ID and renders the "edit.html" template,
    passing the retrieved contact as a parameter.

    Parameters:
        contact_id (int, optional): The ID of the contact to retrieve. Defaults to 0.

    Returns:
        str: The rendered HTML template ("edit.html") with the retrieved contact data.
    """
    contact = Contact.get(contact_id)
    return render_template("edit.html", contact=contact)


@app.route("/contacts/<contact_id>/edit", methods=["POST"])
def contacts_edit_post(contact_id=0):
    """
    A route handler function for the "/contacts/<contact_id>/edit" URL that handles POST requests.

    Retrieves a contact from the database based on the provided contact ID, updates its details with the provided form data,
    and attempts to update it in the database. If the update is successful, a flash message is displayed and the user is
    redirected to the "/contacts/<contact_id>" URL. If the update fails, the user is shown the "edit.html" template with the
    updated contact data.

    Parameters:
        contact_id (int): The ID of the contact to update.

    Returns:
        - If the update is successful: A redirect to the "/contacts/<contact_id>" URL.
        - If the update fails: A rendered HTML template ("edit.html") with the updated contact data.
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


@app.route("/contacts/<contact_id>/delete", methods=["POST"])
def contacts_delete(contact_id=0):
    """
    A route handler function for the "/contacts/<contact_id>/delete" URL that handles POST requests.

    Deletes a contact from the database based on the provided contact ID.

    Parameters:
        contact_id (int): The ID of the contact to delete.

    Returns:
        A redirect to the "/contacts" URL.
    """
    contact = Contact.get(contact_id)
    contact.delete(contact.id)
    flash("Deleted Contact!")
    return redirect("/contacts")
