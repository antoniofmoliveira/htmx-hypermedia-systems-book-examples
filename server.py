from os import environ
import time
from flask import Flask, flash, jsonify, redirect, render_template, request, send_file
import sqlite3

app = Flask(__name__)

app.config['SECRET_KEY'] = environ.get('SECRET_KEY')
app.config['SESSION_TYPE'] = 'memcached'


con = sqlite3.connect('contacts.db', check_same_thread=False)
cur = con.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS contacts(id integer primary key autoincrement, first_name text, last_name text, phone text, email text)''')

pos = 0

"""" 
Fake Archiver Class

Here is a succinct explanation of the class definition and its methods:

**Class Archiver:**

* This class appears to manage the state of an archiving process, tracking its progress and status.

**Class Methods:**

* `__init__(self, user_id)`: Initializes a new Archiver instance with a given user ID and sets 
its internal progress to 0.0.
* `status(self)`: Returns the current status of the archiving process as a string ('Waiting', 
'Running', or 'Complete') based on its internal progress.
* `progress(self)`: Returns the current progress of the archiving process as a float value 
between 0.0 and 1.0.
* `run(cls)`: Increments the internal progress of the archiving process and resets it to 0.0 
if it exceeds 10.0.
* `reset(cls)`: Resets the internal progress of the archiving process to 0.0.
* `archive_file(self)`: Returns a fixed string 'archive.zip', likely representing the name of 
the archived file.
* `get(cls)`: Returns an instance of the Archiver class, creating a new one if none exists, 
and runs the archiving process if an instance already exists.

Note that the `user_id` parameter in the `__init__` method is not used anywhere in the class, 
and the `archive_file` method always returns the same fixed string.
"""


class Archiver:

    instance = None

    def __init__(self, user_id):
        """
        Initializes a new Archiver instance with a given user ID and sets its internal progress to 0.0.

        Args:
            user_id: The ID of the user associated with this archiver instance.

        Returns:
            None
        """
        self.internal_progress = 0.0
        self.user_id = user_id

    def status(self):
        """
        Returns the current status of the archiving process as a string.

        The status can be one of three values:
        - 'Waiting' if the internal progress is 0.0.
        - 'Complete' if the internal progress is 10.0.
        - 'Running' for any other value of internal progress.

        Returns:
            str: The current status of the archiving process.
        """
        if self.internal_progress == 0.0:
            return 'Waiting'
        elif self.internal_progress == 10.:
            return 'Complete'
        else:
            return 'Running'

    def progress(self):
        """
        Returns the current progress of the archiving process as a floating point number between 0.0 and 1.0.

        Returns:
            float: The current progress of the archiving process.
        """
        return self.internal_progress/10.0

    @classmethod
    def run(cls):
        global pos
        pos += 1
        if cls.instance:
            cls.instance.internal_progress = pos
            if cls.instance.internal_progress > 10.0:
                cls.instance.reset()
                pos = 0

    @classmethod
    def reset(cls):
        """
        Resets the internal progress of the archiving process to 0.0.

        Args:
            None

        Returns:
            bool: True if the reset was successful.
        """
        if cls.instance:
            cls.instance.internal_progress = 0.0
        return True

    def archive_file(self):
        return 'archive.zip'

    @classmethod
    def get(cls):
        """
        Retrieves the Archiver instance associated with the class.

        If an instance does not exist, it creates a new Archiver instance with a default user ID of 1.
        Otherwise, it runs the Archiver instance and updates its internal progress.

        Returns:
            Archiver: The Archiver instance associated with the class.
        """
        if cls.instance == None:
            cls.instance = Archiver(user_id=1)
        else:
            Archiver.run()
        return cls.instance


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

    @classmethod
    def count(cls):
        """
        Returns the count of contacts in the database.

        Returns:
            int: The count of contacts in the database.
        """
        cur.execute('''SELECT COUNT(*) FROM contacts''')
        time.sleep(1.5)  # Add a 1.5 second delay
        return cur.fetchone()[0]


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
            return render_template("rows.html", contacts=contacts_set, page=page)
    else:
        contacts_set = Contact.all(page)
    return render_template("index.html", contacts=contacts_set, page=page, archiver=Archiver.get())


@app.route("/contacts", methods=["DELETE"])
def contacts_delete_all():
    """
    Deletes multiple contacts from the database.

    Retrieves a list of contact IDs from the request form, finds each contact by ID, 
    and deletes them from the database. After deletion, it retrieves a list of all 
    contacts and renders the "index.html" template with the updated list.

    Parameters:
        selected_contact_ids (list): A list of contact IDs to be deleted.

    Returns:
        render_template: A rendered HTML template ("index.html") with a list of contacts.
    """
    # this dont worked
    # contact_ids = [
    #     int(id) for id in request.form.getlist("selected_contact_ids")
    # ]

    # this worked
    # added hx-include to button
    contact_ids = [
        int(id) for id in request.args.getlist("selected_contact_ids")
    ]
    for contact_id in contact_ids:
        contact = Contact.get(contact_id)
        Contact.delete(contact_id)
    flash("Deleted Contacts!")
    contacts_set = Contact.all()
    return render_template("index.html", contacts=contacts_set)


@app.route("/contacts/archive", methods=["GET"])
def archive_status():
    """
    Retrieves the status of the archiving process.

    Returns:
        render_template: A rendered HTML template ("archive_ui.html") with the archiver status.
    """
    archiver = Archiver.get()
    return render_template("archive_ui.html", archiver=archiver)


@app.route("/contacts/archive/file", methods=["GET"])
def archive_content():
    """
    Retrieves the archived contact data as a downloadable JSON file.

    Returns:
        send_file: A JSON file containing the archived contact data.
    """
    manager = Archiver.get()
    return send_file(
        manager.archive_file(), "archive.json", as_attachment=True)


@app.route("/contacts/archive", methods=["DELETE"])
def reset_archive():
    """
    Resets the archiving process by retrieving the current archiver instance and calling its reset method.

    Returns:
        render_template: A rendered HTML template ("archive_ui.html") with the reset archiver status.
    """
    archiver = Archiver.get()
    Archiver.reset()
    return render_template("archive_ui.html", archiver=archiver)


@app.route("/contacts/archive", methods=["POST"])
def start_archive():
    """
    Starts the archiving process by retrieving the current archiver instance and rendering the archive UI template.

    Returns:
        render_template: A rendered HTML template ("archive_ui.html") with the archiver status.
    """
    archiver = Archiver.get()
    return render_template("archive_ui.html", archiver=archiver)


@app.route("/contacts/count")
def contacts_count():
    """
    Defines a route for the "/contacts/count" URL of the application.

    Retrieves the total count of contacts in the database and returns it as a string.

    Returns:
        str: A string containing the total count of contacts in the format "(X total Contacts)".
    """
    count = Contact.count()
    return "(" + str(count) + " total Contacts)"


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
    contact = Contact.get(contact_id)
    Contact.delete(contact.id)
    if request.headers.get('HX-Trigger') == 'delete-btn':
        flash("Deleted Contact!")
        return redirect("/contacts", 303)
    else:
        return ""


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
    c.email = request.args.get('email') or ""
    if Contact.email_exists(c.email):
        errors = c.errors
        errors['email'] = 'Email already exists.'
    return errors.get('email') or ""


@app.route("/api/v1/contacts", methods=["GET"])
def json_contacts():
    """
    Defines a route for the "/api/v1/contacts" URL of the application, handling GET requests.

    Retrieves a list of all contacts from the database and returns them as a JSON response.

    Returns:
        dict: A dictionary containing a list of contact dictionaries.
    """
    contacts_set = Contact.all()
    contacts_dicts = [c.__dict__ for c in contacts_set]
    return {"contacts": contacts_dicts}


@app.route("/api/v1/contacts", methods=["POST"])
def json_contacts_new():
    """
    Defines a route for the "/api/v1/contacts" URL of the application, handling POST requests.

    Creates a new contact based on the provided form data and attempts to insert it into the database.

    Parameters:
        first_name (str): The first name of the contact.
        last_name (str): The last name of the contact.
        phone (str): The phone number of the contact.
        email (str): The email address of the contact.

    Returns:
        dict: A dictionary containing the newly created contact's data if the creation is successful.
        tuple: A tuple containing a dictionary with error messages and a 400 status code if the creation fails.
    """
    c = Contact(None,
                request.form.get('first_name'),
                request.form.get('last_name'),
                request.form.get('phone'),
                request.form.get('email'))
    if Contact.create(c):
        return c.__dict__
    else:
        return {"errors": c.errors}, 400


@app.route("/api/v1/contacts/<contact_id>", methods=["GET"])
def json_contacts_view(contact_id=0):
    """
    Retrieves a contact from the database and returns it as a JSON response.

    Parameters:
        contact_id (int): The ID of the contact to be retrieved. Defaults to 0.

    Returns:
        dict: A dictionary containing the contact's data.
    """
    contact = Contact.get(contact_id)
    return contact.__dict__


@app.route("/api/v1/contacts/<contact_id>", methods=["PUT"])
def json_contacts_edit(contact_id):
    """
    Defines a route for the "/api/v1/contacts/<contact_id>" URL of the application, handling PUT requests.

    Updates an existing contact in the database based on the provided form data.

    Parameters:
        contact_id (int): The ID of the contact to be updated.

    Returns:
        dict: A dictionary containing the updated contact's data if the update is successful.
        tuple: A tuple containing a dictionary with error messages and a 400 status code if the update fails.
    """
    c = Contact.get(contact_id)
    c.first = request.form['first_name']
    c.last = request.form['last_name']
    c.phone = request.form['phone']
    c.email = request.form['email']
    if Contact.update(c):
        return c.__dict__
    else:
        return {"errors": c.errors}, 400


@app.route("/api/v1/contacts/<contact_id>", methods=["DELETE"])
def json_contacts_delete(contact_id=0):
    """
    Defines a route for the "/api/v1/contacts/<contact_id>" URL of the application, handling DELETE requests.

    Deletes a contact from the database by its ID.

    Parameters:
        contact_id (int): The ID of the contact to be deleted. Defaults to 0.

    Returns:
        dict: A dictionary containing a success message.
    """
    contact = Contact.get(contact_id)
    Contact.delete(contact.id)
    return jsonify({"success": True})
