from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
from dateutil.relativedelta import relativedelta
from tkcalendar import *
import json
import os

class GymSubscriptionApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Πρόγραμμα συνδρομών")
        self.root.iconbitmap('aboutbody.ico')
        self.customer_list = []

        self.my_tree = ttk.Treeview(root, selectmode='extended')
        self.month_list = ["Όνομα", "Ημ Πληρωμής", "Λήξη", "Ιανουάριος", "Φεβρουάριος", "Μάρτιος", "Απρίλιος", 
                           "Μάϊος", "Ιούνιος", "Ιούλιος", "Αύγουστος", "Σεπτέμβριος", "Οκτώβριος", "Νοέμβριος", "Δεκέμβριος"]

        self.create_widgets()

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=10)
        self.root.grid_rowconfigure(3, weight=1)
        
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_columnconfigure(3, weight=1)
        self.root.grid_columnconfigure(4, weight=1)

        # Φόρτωση πελατών από αρχείο
        self.data_file = "customers.json"
        self.load_customers()

        # Δέσμευση αποθήκευσης κατά το κλείσιμο της εφαρμογής
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.reset_monthly_payments_if_new_year()  # Κλήση της συνάρτησης κατά την εκκίνηση

    def add_customer(self):
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Προσθήκη Πελάτη")
        edit_window.iconbitmap('aboutbody.ico')
        edit_window.geometry("600x600")  # Προσαρμογή μεγέθους παραθύρου

        # Διαμόρφωση πλέγματος
        edit_window.grid_rowconfigure(0, weight=1)
        edit_window.grid_rowconfigure(1, weight=10)
        edit_window.grid_rowconfigure(2, weight=1)
        edit_window.grid_rowconfigure(3, weight=1)
       
        edit_window.grid_columnconfigure(0, weight=1)
        edit_window.grid_columnconfigure(1, weight=10)
        edit_window.grid_columnconfigure(2, weight=10)
        edit_window.grid_columnconfigure(3, weight=10)

        # Μεταβλητές
        customer_name_var = StringVar()
        global paid_months
        paid_months=0
        def paid_months_plus():
            global paid_months  # Χρησιμοποιούμε τη global μεταβλητή
            paid_months += 1  # Αυξάνουμε κατά 1
            # Ενημέρωση της ετικέτας με την νέα τιμή
            label_paid_months.config(text=str(paid_months))
            
        def paid_months_minus():
            global paid_months
            if paid_months > 0:  # Μη επιτρέπεις αρνητικούς μήνες
                paid_months -= 1
                label_paid_months.config(text=str(paid_months))

        # Στοιχεία εισαγωγής
        Label(edit_window, text="Όνομα Πελάτη:", font=( 24)).grid(row=0, column=0, sticky="w")
        name_entry = Entry(edit_window, textvariable=customer_name_var)
        name_entry.grid(row=0, column=1, sticky="w",ipadx=100)

        cal = Calendar(edit_window, selectmode='day', year=datetime.now().year, month=datetime.now().month, day=datetime.now().day)
        cal.grid(row=1, column=0, columnspan=3, pady=10, sticky="nswe")

        Label(edit_window, text="Πληρωμένοι μήνες:", font=( 100)).grid(row=2, column=0,sticky='w')

        minus_button=Button(edit_window,text="-", height=2, bg="grey",command=paid_months_minus).grid(row=2, column=1,sticky='w',ipadx=10)
        label_paid_months = Label(edit_window, text=str(paid_months), font=(100))
        label_paid_months.grid(row=2, column=2, sticky='w')
        plus_button=Button(edit_window,text="+", height=2, bg="grey",command=paid_months_plus).grid(row=2, column=3,sticky='w',ipadx=10)
        

        
        

        

        # Συνάρτηση για την προσθήκη πελάτη
        def add_customer_to_list():
            name = customer_name_var.get().strip()
            payment_date_str = cal.get_date()
            payment_date = datetime.strptime(payment_date_str, "%m/%d/%y")

            

            if not name:
                messagebox.showerror("Σφάλμα", "Το όνομα του πελάτη δεν μπορεί να είναι κενό.")
                return

            try:
                # Προσαρμόστε το format αν χρειάζεται, το tkcalendar δίνει mm/dd/yyyy
                payment_date = datetime.strptime(payment_date_str, "%m/%d/%y")
            except ValueError:
                try:
                    payment_date = datetime.strptime(payment_date_str, "%m/%d/%Y")
                except ValueError:
                    messagebox.showerror("Σφάλμα", "Μη έγκυρη ημερομηνία.")
                    return
            if  paid_months==0:
                messagebox.showerror("Σφάλμα", "Παρακαλώ επιλέξτε τουλάχιστον έναν μήνα.")
                return

            # Υπολογισμός ημερομηνίας λήξης βάσει των πληρωμένων μηνών
            expiry_date = payment_date + relativedelta(months=paid_months)

            payment_date_format= payment_date.strftime("%d/%m/%Y")
            print("payment date="+str(payment_date_format))
            expiry_date_format = expiry_date.strftime("%d/%m/%Y")
            print("expiry date="+str(expiry_date_format))
            
            
            # Δημιουργία πίνακα με τους μήνες πληρωμής
            months_paid = ['-'] * 12  # Δημιουργούμε κενή λίστα για 12 μήνες
            start_month = payment_date.month - 1  # Η Python ξεκινά τους μήνες από το 0 (Ιανουάριος = 0)

            # Συμπλήρωση με "X" στους σωστούς μήνες
            for i in range(0,paid_months):
                month_index = (start_month + i) % 12  # Υπολογισμός του σωστού μήνα (εξασφαλίζει κυκλικότητα)
                months_paid[month_index] = 'Yes'

            # Δημιουργία του πελάτη με τα δεδομένα του
            customer_data = [name, payment_date_format, expiry_date_format] + months_paid

            # Προσθήκη του πελάτη στη λίστα και ενημέρωση του Treeview
            self.customer_list.append(customer_data)
            
            self.my_tree.insert('', 'end', values=customer_data)
            
            #Η μέθοδος delete χρησιμοποιείται για να διαγράψει το περιεχόμενο του πεδίου κειμένου.
            #Δεν είναι απαραίτητο καθώς μετά την προσθήκη καταστρέφεται το παράθυρο λόγω edit_window.destroy()
            name_entry.delete(0, END)

            # Έλεγχος λήξης συνδρομής

            self.check_expiry()

            # Αποθήκευση πελατών
            self.save_customers()

            # Κλείσιμο του παραθύρου μετά την επιτυχή προσθήκη
            messagebox.showinfo("Επιτυχία", "Ο πελάτης προστέθηκε με επιτυχία.")
            edit_window.destroy()

            


            
        # Κουμπί προσθήκης
        add_btn = Button(edit_window, text="Προσθήκη", command=add_customer_to_list)
        add_btn.grid(row=5, column=1, pady=20)

    def sort_customers(self, selection):

        # Καθαρισμός του Treeview
        for item in self.my_tree.get_children():
            self.my_tree.delete(item)
        
        # Ταξινόμηση πελατών ανάλογα με την επιλογή
        if selection == "Αλφαβητικά":
            sorted_list = sorted(self.customer_list, key=lambda x: x[0].lower())
        elif selection == "Ημερομηνία Πληρωμής":
            sorted_list = sorted(self.customer_list, key=lambda x: datetime.strptime(x[1], "%d/%m/%Y"))
        elif selection == "Ημερομηνία Λήξης":
            sorted_list = sorted(self.customer_list, key=lambda  x: datetime.strptime(x[2], "%d/%m/%Y"))
        
        # Εισαγωγή των ταξινομημένων πελατών στο Treeview
        for customer in sorted_list:
            self.my_tree.insert('', 'end', values=customer)
        self.check_expiry()  # Ελέγχει για ληγμένους πελάτες

    def search_customer(self, *args):
        query = self.search_var.get().strip().lower()
        for item in self.my_tree.get_children():
            self.my_tree.delete(item)

        filtered_customers = [customer for customer in self.customer_list if query in customer[0].lower()]
        for customer in filtered_customers:
            self.my_tree.insert('', 'end', values=customer)
        self.check_expiry()  # Ελέγχει για ληγμένους πελάτες

    def check_expiry(self):
        today = datetime.now()
        for child in self.my_tree.get_children():
            values = self.my_tree.item(child, 'values')
            expiry_date_str = values[2]
            expiry_date = datetime.strptime(expiry_date_str, "%d/%m/%Y")
            if expiry_date < today:
                self.my_tree.item(child, tags=('expired',))
            else:
                self.my_tree.item(child, tags=())

        self.my_tree.tag_configure('expired', background='lightcoral')  # Χρώμα για ληγμένες συνδρομές

    def create_widgets(self):
        # Ετικέτα Πελάτη
        customer_label = Label(self.root, text="Πελάτης")
        customer_label.grid(column=0, row=0, sticky="ew", padx=10)

        # Διαμόρφωση Treeview
        self.my_tree['columns'] = self.month_list
        self.my_tree.column("#0", width=0, stretch=NO)

        for month in self.month_list:
            self.my_tree.column(month, anchor=W, width=100, stretch=YES)
            self.my_tree.heading(month, text=month, anchor=W)

        self.my_tree.grid(row=2, column=0, columnspan=12, sticky='nsew')

        # Κουμπιά Προσθήκης, Διαγραφής και Επεξεργασίας
        add_button = Button(self.root, text="Προσθήκη", command=self.add_customer)
        add_button.grid(row=0, column=2, sticky="ew", padx=10)

        delete_button = Button(self.root, text="Διαγραφή", command=self.delete_customer)
        delete_button.grid(row=0, column=3, sticky="ew", padx=10)

        

        # Μενού επιλογής ταξινόμησης
        clicked = StringVar()
        options = ["Αλφαβητικά", "Ημερομηνία Πληρωμής", "Ημερομηνία Λήξης"]
        clicked.set(options[0])
        drop = OptionMenu(self.root, clicked, *options, command=self.sort_customers)
        drop.grid(row=1, column=0, padx=10, pady=10)

        # Πεδίο αναζήτησης
        self.search_var = StringVar()
        self.search_var.trace_add('write', self.search_customer)
        search_entry = Entry(self.root, textvariable=self.search_var)
        search_entry.grid(row=0, column=1, padx=10, pady=10)

    def delete_customer(self):
        selected = self.my_tree.selection()
        if not selected:
            messagebox.showwarning("Προειδοποίηση", "Δεν έχει επιλεγεί πελάτης για διαγραφή.")
            return
        for item in selected:
            values = self.my_tree.item(item, 'values')
            # Επιβεβαίωση διαγραφής
            confirm = messagebox.askyesno("Επιβεβαίωση", f"Είστε σίγουροι ότι θέλετε να διαγράψετε τον πελάτη '{values[0]}';")
            if confirm:
                self.my_tree.delete(item)
                # Εύρεση και αφαίρεση από τη λίστα πελατών
                self.customer_list = [customer for customer in self.customer_list if customer[0] != values[0]]
        # Αποθήκευση μετά τη διαγραφή
        self.save_customers()
        messagebox.showinfo("Επιτυχία", "Οι επιλεγμένοι πελάτες διαγράφηκαν επιτυχώς.")

    def save_customers(self):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.customer_list, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Σφάλμα Αποθήκευσης", f"Προέκυψε σφάλμα κατά την αποθήκευση των δεδομένων:\n{e}")

    def load_customers(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.customer_list = json.load(f)
                for customer in self.customer_list:
                    self.my_tree.insert('', 'end', values=customer)
                self.check_expiry()
            except Exception as e:
                messagebox.showerror("Σφάλμα Φόρτωσης", f"Προέκυψε σφάλμα κατά τη φόρτωση των δεδομένων:\n{e}")

    def on_closing(self):
        # Αποθήκευση πριν κλείσει η εφαρμογή
        self.save_customers()
        self.root.destroy()

    def reset_monthly_payments_if_new_year(self):
        current_year = datetime.now().year

        for customer in self.customer_list:
            # Υποθέτω ότι το 2ο στοιχείο είναι η ημερομηνία πληρωμής (πρώτη πληρωμή)
            date_str = customer[1]
            try:
                registration_date = datetime.strptime(date_str, "%d/%m/%Y")
            except ValueError:
                # Αν δεν είναι σωστή η ημερομηνία, συνέχισε με τον επόμενο πελάτη
                continue

            payment_year = registration_date.year

            # Αν το τρέχον έτος είναι μεγαλύτερο από το έτος πληρωμής, τότε μηδενίζουμε τις πληρωμές
            if current_year > payment_year:
                # Θέτουμε όλες τις μηνιαίες πληρωμές σε "-"
                 for i in range(len(customer) - 1, 2, -1):  # range(start, stop, step) σταματά στο Ιανουαριος και δεν περιεχει ημ ληξης κτλ  
                    if customer[i] == "Yes":
                        customer[i] = "-"
                    elif customer[i] == "-":
                        break
        
        # Αποθήκευση μετά τις αλλαγές
        self.save_customers()

        # Καθαρισμός του Treeview και επανεισαγωγή δεδομένων
        for item in self.my_tree.get_children():
            self.my_tree.delete(item)

        for customer in self.customer_list:
            self.my_tree.insert('', 'end', values=customer)
            self.check_expiry()
            



if __name__ == "__main__":
    root = tk.Tk()
    app = GymSubscriptionApp(root)
    root.mainloop()
