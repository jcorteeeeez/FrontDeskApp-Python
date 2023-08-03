import tkinter as tk
import sqlite3
from tkinter import messagebox
import datetime
import pytz

def create_customer():
    global selected_storage
    first_name = entry_first_name.get()
    last_name = entry_last_name.get()
    phone_number = entry_phone_number.get()

    if not first_name or not last_name or not phone_number:
        messagebox.showerror("Error", "Please fill in all fields.")
        return

    if selected_storage.get() is None:
        messagebox.showerror("Error", "Please select storage space.")
        return

    conn = sqlite3.connect('customer_database.db')
    cursor = conn.cursor()

    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                phone_number TEXT
            )
        ''')

        # Check if the customer's first name or last name already exists
        cursor.execute('SELECT * FROM customers WHERE first_name=? AND last_name=? AND phone_number=?', (first_name, last_name, phone_number))
        existing_customer = cursor.fetchone()

        if existing_customer:
            # If the customer already exists, display a popup window with a button to store the box again
            None

        else:
            storage_space = selected_storage.get()  # Fetch the selected storage space
            cursor.execute('INSERT INTO customers (first_name, last_name, phone_number) VALUES (?, ?, ?)',
                           (first_name, last_name, phone_number))
            conn.commit()

       

        messagebox.showinfo("Success", "Customer created successfully!")
        entry_first_name.delete(0, tk.END)
        entry_last_name.delete(0, tk.END)
        entry_phone_number.delete(0, tk.END)
        selected_storage.set(None)

        record_box_event(first_name, last_name, "stored")

        open_storage_space_window()

              # Call the storage space window after customer creation

    except sqlite3.Error as e:
        messagebox.showerror("Database Error", str(e))

    finally:
        conn.close()

def create_box_events_table():
    conn = sqlite3.connect('customer_database.db')
    cursor = conn.cursor()

    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS box_events (
                id INTEGER PRIMARY KEY,
                customer_id INTEGER,
                first_name TEXT,
                last_name TEXT,
                timestamp TEXT,
                status TEXT,
                space TEXT
            )
        ''')
        conn.commit()

    except sqlite3.Error as e:
        messagebox.showerror("Database Error", str(e))

    finally:
        conn.close()

def delete_stored_status(customer_id):
    conn = sqlite3.connect('customer_database.db')
    cursor = conn.cursor()

    try:
        cursor.execute('DELETE FROM box_events WHERE customer_id=? AND status="stored"', (customer_id,))
        conn.commit()

    except sqlite3.Error as e:
        messagebox.showerror("Database Error", str(e))

    finally:
        conn.close()

def count_small_spaces():
    conn = sqlite3.connect('customer_database.db')
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT COUNT(*) FROM box_events WHERE space="Small"')
        count = cursor.fetchone()[0]
        return count
    finally:
        conn.close()

def count_medium_spaces():
    conn = sqlite3.connect('customer_database.db')
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT COUNT(*) FROM box_events WHERE space="Medium"')
        count = cursor.fetchone()[0]
        return count
    finally:
        conn.close()

def count_large_spaces():
    conn = sqlite3.connect('customer_database.db')
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT COUNT(*) FROM box_events WHERE space="Large"')
        count = cursor.fetchone()[0]
        return count
    finally:
        conn.close()



def record_box_event(first_name, last_name, status):
    conn = sqlite3.connect('customer_database.db')
    cursor = conn.cursor()
    
    try:
        local_timezone = pytz.timezone('Asia/Singapore')
        local_timestamp = datetime.datetime.now(local_timezone).strftime('%Y-%m-%d %H:%M:%S')

        cursor.execute('SELECT id FROM customers WHERE first_name=? AND last_name=?', (first_name, last_name))
        customer_id = cursor.fetchone()

        if customer_id:
            customer_id = customer_id[0]  # Extract the customer_id value from the tuple
            cursor.execute('INSERT INTO box_events (customer_id, first_name, last_name, timestamp, status) VALUES (?, ?, ?, ?, ?)',
                           (customer_id, first_name, last_name, local_timestamp, status))
            conn.commit()

        else:
            messagebox.showerror("Error", "Customer not found. Please check first name and last name.")

        if status == "retrieved" and customer_id:
            delete_stored_status(customer_id)  # Pass the individual customer_id value to the function

    except sqlite3.Error as e:
        messagebox.showerror("Database Error", str(e))

    finally:
        conn.close()

def save_storage_space_box():
    selected_space = selected_storage.get()

    if not selected_space:
        messagebox.showerror("Error", "Please select a storage space.")
        return

    if selected_space == "Small":
        small_space_count = count_small_spaces()
        if small_space_count >= 6:
            messagebox.showerror("Insufficient Space", "The Small Box space is already full. Please choose another space.")
            return
    
    if selected_space == "Medium":
        medium_space_count = count_medium_spaces()
        if medium_space_count >= 4:
            messagebox.showerror("Insufficient Space", "The Medium Box space is already full. Please choose another space.")
            return
    
    if selected_space == "Large":
        large_space_count = count_large_spaces()
        if large_space_count >= 2:
            messagebox.showerror("Insufficient Space", "The Large Box space is already full. Please choose another space.")
            return
  

    conn = sqlite3.connect('customer_database.db')
    cursor = conn.cursor()

    try:
        # Check if the 'space' column exists in the 'box_events' table
        cursor.execute("PRAGMA table_info(box_events)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'space' not in columns:
            # Add the 'space' column to the 'box_events' table if it doesn't exist
            cursor.execute('ALTER TABLE box_events ADD COLUMN space TEXT')

        # Update the 'space' column for the most recently added customer
        cursor.execute('UPDATE box_events SET space=? WHERE id=(SELECT MAX(id) FROM box_events)', (selected_space,))
        conn.commit()

        #if selected_space != "Small":
            # Record box storage for the most recently added customer
            #record_box_event(entry_first_name.get(), entry_last_name.get(), "stored")  # Use the values from the entry widgets

        messagebox.showinfo("Success", f"Storage space '{selected_space}' selected and saved successfully!")
        storage_window.destroy()
        root.deiconify()  # Close the root window after the storage space window is closed

    except sqlite3.Error as e:
        messagebox.showerror("Database Error", str(e))

    finally:
        conn.close()


def open_storage_space_window():
    global storage_window, selected_storage
    storage_window = tk.Toplevel()
    storage_window.title("Select Storage Space")

    selected_storage = tk.StringVar()
    tk.Radiobutton(storage_window, text="Small", variable=selected_storage, value="Small").pack(anchor=tk.W)
    tk.Radiobutton(storage_window, text="Medium", variable=selected_storage, value="Medium").pack(anchor=tk.W)
    tk.Radiobutton(storage_window, text="Large", variable=selected_storage, value="Large").pack(anchor=tk.W)


    
    save_button = tk.Button(storage_window, text="Save", command=save_storage_space_box)
    save_button.pack()

def retrieve_customer_data():
    conn = sqlite3.connect('customer_database.db')
    cursor = conn.cursor()

    try:
        
        cursor.execute('SELECT first_name, last_name, timestamp, status, space FROM box_events')
        data = cursor.fetchall()

        # Create a new window to show the retrieved data
        retrieve_window = tk.Toplevel()
        retrieve_window.title("Retrieve Customer Data")

        # Create a listbox to display the customer information
        listbox = tk.Listbox(retrieve_window, width=100, height=20)
        listbox.pack()

        for item in data:
            listbox.insert(tk.END, f"{item[0]} {item[1]} - {item[2]} - {item[3]} - {item[4]}")

        def on_customer_select(event):
            selected_item = listbox.get(listbox.curselection())
            name = selected_item.split(" - ")[0]
            first_name, last_name = name.split(" ")
            record_box_event(first_name, last_name, "retrieved")
            messagebox.showinfo("Success", f"Recorded retrieval for {first_name} {last_name}.")
            retrieve_window.destroy()

        listbox.bind("<<ListboxSelect>>", on_customer_select)

    except sqlite3.Error as e:
        messagebox.showerror("Database Error", str(e))

    finally:
        conn.close()



def main():
    global entry_first_name, entry_last_name, entry_phone_number, selected_storage, root

    root = tk.Tk()
    root.title("FrontDeskApp")

    label_first_name = tk.Label(root, text="First Name:")
    label_first_name.grid(row=0, column=0, padx=10, pady=5)

    entry_first_name = tk.Entry(root)  # Define entry widget as a global variable
    entry_first_name.grid(row=0, column=1, padx=10, pady=5)

    label_last_name = tk.Label(root, text="Last Name:")
    label_last_name.grid(row=1, column=0, padx=10, pady=5)

    entry_last_name = tk.Entry(root)  # Define entry widget as a global variable
    entry_last_name.grid(row=1, column=1, padx=10, pady=5)

    label_phone_number = tk.Label(root, text="Phone Number:")
    label_phone_number.grid(row=2, column=0, padx=10, pady=5)

    entry_phone_number = tk.Entry(root)  # Define entry widget as a global variable
    entry_phone_number.grid(row=2, column=1, padx=10, pady=5)

    selected_storage = tk.StringVar()  # Initialize selected_storage

    button_create_customer = tk.Button(root, text="Store Box", command=create_customer)
    button_create_customer.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    button_retrieve = tk.Button(root, text="Retrieve Box", command=retrieve_customer_data)
    button_retrieve.grid(row=5, column=0, columnspan=2, padx=10, pady=10)


    # Create the box_events table
    create_box_events_table()
   
    root.mainloop()

if __name__ == "__main__":
    main()