from flask import Flask, flash, redirect, render_template, request
import sqlite3

app = Flask(__name__)

con = sqlite3.connect('contacts.db', check_same_thread=False)

cur = con.cursor()
# cur.execute('''CREATE TABLE IF NOT EXISTS contacts(id integer primary key autoincrement, first_name text, last_name text, phone text, email text)''')


class Contact:
    def __init__(self, id, first, last, phone, email):
        self.id = id
        self.first = first
        self.last = last
        self.phone = phone
        self.email = email

    @staticmethod
    def from_dict(data):
        return Contact(
            id=data.get('id'),
            first=data.get('first_name'),
            last=data.get('last_name'),
            phone=data.get('phone'),
            email=data.get('email')
        )

    @property
    def errors(self):
        return {
            'first': 'First name is required.' if not self.first else None,
            'last': 'Last name is required.' if not self.last else None,
            'phone': 'Phone is required.' if not self.phone else None,
            'email': 'Email is required.' if not self.email else None
        }

    @classmethod
    def create(cls, contact):
        cur.execute('''INSERT INTO contacts(first_name, last_name, phone, email) VALUES(?, ?, ?, ?)''',
                    (contact.first, contact.last, contact.phone, contact.email))
        con.commit()
        return True

    @classmethod
    def get(cls, contact_id):
        cur.execute('''SELECT * FROM contacts WHERE id=?''', (contact_id,))
        return cls(*cur.fetchone())

    @classmethod
    def update(cls, contact):
        cur.execute('''UPDATE contacts SET first_name=?, last_name=?, phone=?, email=? WHERE id=?''',
                    (contact.first, contact.last, contact.phone, contact.email, contact.id))
        con.commit()
        return True

    @classmethod
    def delete(cls, contact_id):
        cur.execute('''DELETE FROM contacts WHERE id=?''', (contact_id,))
        con.commit()

    @classmethod
    def all(cls):
        cur.execute('''SELECT * FROM contacts''')
        return [cls(*row) for row in cur.fetchall()]

    @classmethod
    def search(cls, search_term):
        cur.execute('''SELECT * FROM contacts WHERE first_name LIKE ?
                        OR last_name LIKE ?
                        OR phone LIKE ?
                        OR email LIKE ?''',
                    ('%' + search_term + '%',) * 4)
        return [cls(*row) for row in cur.fetchall()]


@app.route("/")
def index():
    return redirect("/contacts")


@app.route("/contacts")
def contacts():
    search = request.args.get("q")
    if search is not None:
        contacts_set = Contact.search(search)
    else:
        contacts_set = Contact.all()
    return render_template("index.html", contacts=contacts_set)


@app.route("/contacts/new", methods=['GET'])
def contacts_new_get():
    contact = Contact(0, "", "", "", "")
    return render_template("new.html", contact=contact)


@app.route("/contacts/new", methods=['POST'])
def contacts_new():
    c = Contact(
        None,
        request.form['first_name'],
        request.form['last_name'],
        request.form['phone'],
        request.form['email'])
    if Contact.create(c):
        # flash("Created New Contact!")
        return redirect("/contacts")
    else:
        return render_template("new.html", contact=c)


@app.route("/contacts/<contact_id>")
def contacts_view(contact_id=0):
    contact = Contact.get(contact_id)
    return render_template("show.html", contact=contact)


@app.route("/contacts/<contact_id>/edit", methods=["GET"])
def contacts_edit_get(contact_id=0):
    contact = Contact.get(contact_id)
    return render_template("edit.html", contact=contact)


@app.route("/contacts/<contact_id>/edit", methods=["POST"])
def contacts_edit_post(contact_id=0):
    c = Contact.get(contact_id)
    c.first = request.form['first_name']
    c.last = request.form['last_name']
    c.phone = request.form['phone']
    c.email = request.form['email']
    if Contact.update(c):
        # flash("Updated Contact!")
        return redirect("/contacts/" + str(contact_id))
    else:
        return render_template("edit.html", contact=c)


@app.route("/contacts/<contact_id>/delete", methods=["POST"])
def contacts_delete(contact_id=0):
    contact = Contact.get(contact_id)
    contact.delete(contact.id)
    # flash("Deleted Contact!")
    return redirect("/contacts")
