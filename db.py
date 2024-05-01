import sqlite3
from tkinter import messagebox


class Database:
    def __init__(self, db):
        self.conn = sqlite3.connect(db,check_same_thread=False)
        self.cur = self.conn.cursor()
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS settings (id INTEGER PRIMARY KEY, part text, customer text, retailer text, price text)")
        self.conn.commit()

    def fetchSetting(self):
        self.cur.execute("SELECT * FROM settings")
        rows = self.cur.fetchone()
        return rows
    def getStatus(self):
        self.cur.execute("SELECT * FROM status")
        rows = self.cur.fetchone()
        return rows

    def insert(self, part, customer, retailer, price):
        self.cur.execute("INSERT INTO settings VALUES (NULL, ?, ?, ?, ?)",
                         (part, customer, retailer, price))
        self.conn.commit()

    def remove(self, id):
        self.cur.execute("DELETE FROM settings WHERE id=?", (id,))
        self.conn.commit()

    def update(self, id, cccode, ip_server, pos_vendor_code, port):
        try:
            self.cur.execute("UPDATE settings SET cccode = ?, pos_vendor_code = ?, autopoll_ip_server = ?, port=? WHERE id = ?",
                            (cccode, pos_vendor_code, ip_server, port, id))
            self.conn.commit()
            messagebox.showinfo('Success', 'Settings Updated!')
        except:
            messagebox.showerror('Error','Error Updating.')
    def __del__(self):
        self.conn.close()
