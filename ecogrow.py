import mysql.connector # type: ignore
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk



def connect_db():
    return mysql.connector.connect(
        host="localhost",  
        user="root", 
        password="",  
        database="ecogrow_db"  
    )

class AdminPanel:
    def __init__(self, root, db_connection):
        self.root = root
        self.root.title("Admin Panel")
        self.root.geometry("720x550")

        self.db_connection = db_connection
        self.db_cursor = self.db_connection.cursor()

        self.tree_options = self.get_tree_choices()
        self.location_options = self.get_location_choices()


        self.create_widgets()
        self.load_donation_history()

    def create_widgets(self):
 
        self.tree = ttk.Treeview(
            self.root,
            columns=("Donator Name", "Tree Name", "Location", "Date", "Amount"),
            show="headings",
            height=20,
        )
        self.tree.heading("Donator Name", text="Donator Name")
        self.tree.heading("Tree Name", text="Tree Name")
        self.tree.heading("Location", text="Location")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Amount", text="Amount")
        self.tree.column("Donator Name", width=200)
        self.tree.column("Tree Name", width=150)
        self.tree.column("Location", width=150)
        self.tree.column("Date", width=100)
        self.tree.column("Amount", width=100)
        self.tree.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

        self.edit_button = tk.Button(self.root, text="Edit Selected", command=self.edit_entry, width=20)
        self.edit_button.grid(row=1, column=0, padx=10, pady=10)

        self.delete_button = tk.Button(self.root, text="Delete Selected", command=self.delete_entry, width=20)
        self.delete_button.grid(row=1, column=1, padx=10, pady=10)

        self.refresh_button = tk.Button(self.root, text="Refresh", command=self.load_donation_history, width=20)
        self.refresh_button.grid(row=1, column=2, padx=10, pady=10)

        self.show_total_donations_button = tk.Button(self.root, text="Show Total Donations by Tree", command=self.show_total_donations, width=30)
        self.show_total_donations_button.grid(row=2, column=0, columnspan=3, pady=10)

    def get_tree_choices(self):
        query = "SELECT tree_name FROM tree_types"
        self.db_cursor.execute(query)
        return [row[0] for row in self.db_cursor.fetchall()]

    def get_location_choices(self):
        query = "SELECT location_choice FROM donation_location"
        self.db_cursor.execute(query)
        return [row[0] for row in self.db_cursor.fetchall()]

    def load_donation_history(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        query = """
        SELECT d.name, t.tree_name, l.location_choice, dh.donation_date, dh.amount
        FROM donation_history dh
        JOIN donators d ON dh.donator_id = d.donator_id
        JOIN tree_types t ON dh.tree_id = t.tree_type_id
        JOIN donation_location l ON dh.location_id = l.location_id
        """
        self.db_cursor.execute(query)
        for row in self.db_cursor.fetchall():
            self.tree.insert("", tk.END, values=row)

    def edit_entry(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "Please select an entry to edit.")
            return

        values = self.tree.item(selected_item, "values")
        self.open_edit_window(values)

    def open_edit_window(self, values):
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Entry")
        edit_window.geometry("400x300")

        tk.Label(edit_window, text="Donator Name:").grid(row=0, column=0, padx=10, pady=10)
        tk.Label(edit_window, text=values[0]).grid(row=0, column=1, padx=10, pady=10)

        tk.Label(edit_window, text="Tree Name:").grid(row=1, column=0, padx=10, pady=10)
        self.edit_tree_name = ttk.Combobox(edit_window, values=self.tree_options, width=30)
        self.edit_tree_name.set(values[1])  
        self.edit_tree_name.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(edit_window, text="Location:").grid(row=2, column=0, padx=10, pady=10)
        self.edit_location = ttk.Combobox(edit_window, values=self.location_options, width=30)
        self.edit_location.set(values[2])  
        self.edit_location.grid(row=2, column=1, padx=10, pady=10)

        tk.Label(edit_window, text="Amount:").grid(row=3, column=0, padx=10, pady=10)
        self.edit_amount = tk.Entry(edit_window, width=30)
        self.edit_amount.insert(0, values[4])
        self.edit_amount.grid(row=3, column=1, padx=10, pady=10)

        save_button = tk.Button(edit_window, text="Save Changes", command=lambda: self.save_edit(values, edit_window))
        save_button.grid(row=4, column=0, columnspan=2, pady=20)

    def save_edit(self, old_values, edit_window):
        new_tree = self.edit_tree_name.get()
        new_location = self.edit_location.get()
        try:
            new_amount = float(self.edit_amount.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount.")
            return

        try:
            self.db_cursor.execute(
                """
                UPDATE donation_history dh
                JOIN tree_types t ON dh.tree_id = t.tree_type_id
                JOIN donation_location l ON dh.location_id = l.location_id
                SET t.tree_name = %s, l.location_choice = %s, dh.amount = %s
                WHERE t.tree_name = %s AND l.location_choice = %s AND dh.amount = %s
                """,
                (new_tree, new_location, new_amount, old_values[1], old_values[2], old_values[4])
            )
            self.db_connection.commit()
            messagebox.showinfo("Success", "Entry updated successfully.")
            edit_window.destroy()
            self.load_donation_history()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Database Error: {err}")

    def delete_entry(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "Please select an entry xto delete.")
            return

        values = self.tree.item(selected_item, "values")
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this entry?")
        if confirm:
            try:
                self.db_cursor.execute(
                    """
                    DELETE dh
                    FROM donation_history dh
                    JOIN tree_types t ON dh.tree_id = t.tree_type_id
                    JOIN donation_location l ON dh.location_id = l.location_id
                    WHERE t.tree_name = %s AND l.location_choice = %s AND dh.amount = %s
                    """,
                    (values[1], values[2], values[4])
                )
                self.db_connection.commit()
                messagebox.showinfo("Success", "Entry deleted successfully.")
                self.load_donation_history()
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Database Error: {err}")

    def show_total_donations(self):
        query = """
        SELECT t.tree_name, SUM(dh.amount) AS total_donated
        FROM donation_history dh
        JOIN tree_types t ON dh.tree_id = t.tree_type_id
        GROUP BY t.tree_name
        """
        self.db_cursor.execute(query)
        result = self.db_cursor.fetchall()

        if result:
            message = "Total Donations per Tree:\n\n"
            for row in result:
                message += f"{row[0]}: ₱{row[1]:,.2f}\n"
            messagebox.showinfo("Total Donations by Tree", message)
        else:
            messagebox.showinfo("Total Donations by Tree", "No donations found.")

class AdminLogin:
    def __init__(self, root, db_connection):
        self.root = root
        self.db_connection = db_connection
        self.root.title("Admin Login")
        self.root.geometry("300x200")
        
        tk.Label(self.root, text="Enter Access Code:").pack(pady=10)
        self.access_code_entry = tk.Entry(self.root, show="*", width=30)
        self.access_code_entry.pack(pady=10)

        self.login_button = tk.Button(self.root, text="Login", command=self.verify_access_code)
        self.login_button.pack(pady=20)
    
    def verify_access_code(self):
        access_code = self.access_code_entry.get().strip()
        correct_code = "ecogrow2003"  
        
        if access_code == correct_code:
            self.root.destroy()
            admin_root = tk.Toplevel()
            AdminPanel(admin_root, self.db_connection)
        else:
            messagebox.showerror("Error", "Invalid access code. Please try again.")

class DonationApp:
    
    def __init__(self, root):
        self.root = root
        self.root.title("EcoGrow Donation System")
        self.root.geometry("800x600")

        self.db_connection = connect_db()
        self.db_cursor = self.db_connection.cursor()
        
        self.tree_options = self.get_tree_choices()
        self.tree_details = self.get_tree_details()
        self.location_options = self.get_location_choices()


        self.create_widgets()

    def create_widgets(self):

        tk.Label(self.root, text="Name:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.donor_name = tk.Entry(self.root, width=40)
        self.donor_name.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self.root, text="Email:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.donor_email = tk.Entry(self.root, width=40)
        self.donor_email.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(self.root, text="Phone Number:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.donor_phone = tk.Entry(self.root, width=40)
        self.donor_phone.grid(row=2, column=1, padx=10, pady=10)

        tk.Label(self.root, text="Select Tree:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.tree_choice = ttk.Combobox(self.root, values=list(self.tree_options.keys()), width=37)
        self.tree_choice.set(list(self.tree_options.keys())[0])
        self.tree_choice.grid(row=3, column=1, padx=10, pady=10)
        self.view_details_button = tk.Button(self.root, text="View Tree Details", command=self.show_tree_details)
        self.view_details_button.grid(row=3, column=2, padx=10, pady=10)

        tk.Label(self.root, text="Select Location:").grid(row=4, column=0, padx=10, pady=10, sticky="w")
        self.location_choice = ttk.Combobox(self.root, values=self.location_options, width=37)
        self.location_choice.set(self.location_options[0])
        self.location_choice.grid(row=4, column=1, padx=10, pady=10)

        tk.Label(self.root, text="Amount to Donate:").grid(row=5, column=0, padx=10, pady=10, sticky="w")
        self.donation_amount = tk.Entry(self.root, width=40)
        self.donation_amount.grid(row=5, column=1, padx=10, pady=10)

        self.donate_button = tk.Button(self.root, text="Donate", command=self.donate, width=20)
        self.donate_button.grid(row=6, column=0, columnspan=2, pady=20)

        self.admin_button = tk.Button(self.root, text="Admin Panel", command=self.open_admin_panel, width=20)
        self.admin_button.grid(row=7, column=0, columnspan=2, pady=10)

    def get_tree_choices(self):
        query = "SELECT tree_name FROM tree_types"
        self.db_cursor.execute(query)
        return {row[0]: None for row in self.db_cursor.fetchall()}

    def get_tree_details(self):
        query = "SELECT tree_name, description, price FROM tree_types"
        self.db_cursor.execute(query)
        return {row[0]: {"description": row[1], "price": row[2]} for row in self.db_cursor.fetchall()}

    def get_location_choices(self):
        query = "SELECT location_choice FROM donation_location"
        self.db_cursor.execute(query)
        return [row[0] for row in self.db_cursor.fetchall()]

    def show_tree_details(self):
        selected_tree =  self.tree_choice.get()
        if not selected_tree:
            messagebox.showerror("Error", "Please select a tree to view details.")
            return
        
        tree_details =  self.tree_details.get(selected_tree, None)
        if tree_details:
            details = tree_details["description"]
            price = tree_details["price"]
            messagebox.showinfo("Tree Details", f"{selected_tree}:\n\n{details}\n\nPrice: ₱{price:,.2f}")
        else:
            messagebox.showinfo("Tree Details", "No details available.")
        
    def donate(self):
        name = self.donor_name.get().strip()
        email = self.donor_email.get().strip()
        phone = self.donor_phone.get().strip()
        tree = self.tree_choice.get().strip()
        location = self.location_choice.get().strip()

        if "@" not in email or "." not in email:
            messagebox.showerror("Error", "Please enter a valid email address.")
            return
        
        if not phone.isdigit():
            messagebox.showerror("Error", "Please enter a valid phone number.")
            return

        try:
            amount = float(self.donation_amount.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid donation amount.")
            return

        if not all([name, email, phone, tree, location, amount]):
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        try:
            self.db_cursor.execute("SELECT donator_id FROM donators WHERE email = %s", (email,))
            donator_id = self.db_cursor.fetchone()

            if not donator_id:
                self.db_cursor.execute(
                    "INSERT INTO donators (name, email, phone_number, registration_date) VALUES (%s, %s, %s, CURDATE())",
                    (name, email, phone)
                )
                self.db_connection.commit()
                donator_id = self.db_cursor.lastrowid
            else:
                donator_id = donator_id[0]

            self.db_cursor.execute("SELECT tree_type_id FROM tree_types WHERE tree_name = %s", (tree,))
            tree_id = self.db_cursor.fetchone()[0]
            self.db_cursor.execute("SELECT location_id FROM donation_location WHERE location_choice = %s", (location,))
            location_id = self.db_cursor.fetchone()[0]

            self.db_cursor.execute(
                "INSERT INTO donation_history (donator_id, tree_id, location_id, donation_date, amount) VALUES (%s, %s, %s, CURDATE(), %s)",
                (donator_id, tree_id, location_id, amount)
            )
            self.db_connection.commit()
            messagebox.showinfo("Success", "Donation recorded successfully.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    def open_admin_panel(self):
        admin_login_root = tk.Toplevel(self.root)
        AdminLogin(admin_login_root, self.db_connection)


if __name__ == "__main__":
    root = tk.Tk()
    app = DonationApp(root)
    root.mainloop()
