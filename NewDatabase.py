import mysql.connector
import datetime
import json
import secrets
import time

class Database:
    cursor = None
    def __init__(self):
        try:
            self.connection = mysql.connector.connect(
                host="localhost",
                user ="root",
                password="system",
                database="carparking"
            )
            self.cursor = self.connection.cursor()
        except mysql.connector.Error as err: 
            print("Error : ", err)     
            
    def fetchRTO(self,no):
        with open('RTO/API.json', 'r') as file:
            dataset = json.load(file)
        rescords = dataset.get("RTO_Records",[])
        for rec in rescords:
            reg = rec.get("registration_number","")
            if reg == no:
                return rec
        return None

    def findslot(self):
        try:
            self.cursor.execute("SELECT slot_id FROM slot WHERE status = 'Empty' LIMIT 1")
            return self.cursor.fetchone()[0]
        except mysql.connector.Error as err:
            print("Error : ",err)
            
    def fetchparkingExit(self,carno):
        try:
            self.cursor.execute("SELECT duration FROM parkingexit WHERE entry_id = (SELECT entry_id FROM parkingentry WHERE vehicle_id=%s)",(carno,))
            return self.cursor.fetchone()
        except mysql.connector.Error as err:
            print("Error : ",err)

    def fetchBill(self):
        try:
            self.cursor.execute("SELECT total_amount,duration FROM bill order by bill_id DESC LIMIT 1")
            return self.cursor.fetchone()
        except mysql.connector.Error as err:
            print("Error : ",err)

    def fetchBillsfromID(self,bill_id):
        try:
            self.cursor.execute("SELECT * FROM bill WHERE bill_id=%s",(bill_id,))
            return self.cursor.fetchone()
        except mysql.connector.Error as err:
            print("Error : ",err)

    def fetchAllBills(self):
        try:
            self.cursor.execute("SELECT * FROM bill order by exit_id ASC")
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print("Error : ",err)

    # main Function
    def insertVehicle(self,carno):
        try:
            if self.findslot():
                data = self.fetchRTO(carno)
                if data:
                    self.cursor.execute("INSERT INTO vehicle(vehicle_id,owner_name,model,color,contact,address) VALUES (%s,%s,%s,%s,%s,%s)",
                                        (carno,
                                        data["owner_name"],
                                        data["model"],
                                        data["color"],
                                        data["contact_number"],
                                        data["address"]
                                        ))
                    self.connection.commit()
                    self.insertParkingEntery(carno)
                else:
                    print("No RTO Data Found...!")
            else: 
                print("No Slot Available...!")
        except mysql.connector.Error as err:
            print("Error : ",err)
     
    def updateSlotStatus(self,status,slot):
        try:
            if status == 1:
                self.cursor.execute("UPDATE slot SET status = 'Occupied' WHERE slot_id = %s",(slot,))
                self.connection.commit()
            elif status == 0:
                self.cursor.execute("UPDATE slot SET status = 'Empty' WHERE slot_id = %s",(slot,))
                self.connection.commit()
        except mysql.connector.Error as err:
            print("Error : ",err)
    
    def insertParkingEntery(self,carno):
        try:
            slot = self.findslot()
            self.cursor.execute("INSERT INTO parkingentry(entry_id,vehicle_id,entry_time,slot_id) VALUES (%s,%s,%s,%s)",
                               (secrets.randbelow(10**6),
                                carno,
                                datetime.datetime.now(),
                                slot))
            self.connection.commit()
            
            # update the slot status
            self.updateSlotStatus(1,slot)
        except mysql.connector.Error as err:
            print("Error : ",err)       
            
    def fetchCarEntry(self,carno):
        try:
            self.cursor.execute("SELECT entry_id,entry_time,slot_id FROM parkingentry WHERE vehicle_id=%s",(carno,))
            return self.cursor.fetchone()
        except mysql.connector.Error as err:
            print("Error : ",err)
            
    def insertParkingExit(self,carno):
        try:
            result = self.fetchCarEntry(carno)
            duration = datetime.datetime.now() - result[1]
            if duration:
                self.cursor.execute("INSERT INTO parkingexit(exit_id,entry_id,exit_time,duration) VALUES (%s,%s,%s,%s)",
                                (result[0],
                                    result[0],
                                    datetime.datetime.now(),
                                    duration
                                    ))
                self.connection.commit()
                self.insertBill(carno,result[0])
            else:
                print("Error in calculating duration...!")
        except mysql.connector.Error as err:
            print("Error : ",err) 
    
    def insertBill(self,carno,id):
        try:
            duration = self.fetchparkingExit(carno)[0]
            amount = duration.total_seconds() / 3600 * 50  # Example: 50 currency units per hour
            amount = round(amount,2)
            
            self.cursor.execute("INSERT INTO bill(exit_id,total_amount,payment_time,vehicle_id,duration,entrytime) VALUES (%s,%s,%s,%s,%s,%s)",
                                (id,
                                 amount,
                                 datetime.datetime.now(),
                                 carno,
                                 duration,
                                 self.fetchCarEntry(carno)[1]))
            self.connection.commit()
            
            self.updateSlotStatus(0,self.fetchCarEntry(carno)[2])
            self.deleteAll(carno,self.fetchCarEntry(carno)[0])
        except mysql.connector.Error as err:
            print("Error :",err)
    
    def deleteAll(self,carno,id):
        try:
            self.cursor.execute("DELETE FROM parkingentry WHERE vehicle_id=%s",(carno,))
            self.connection.commit()
            self.cursor.execute("DELETE FROM vehicle WHERE vehicle_id=%s",(carno,))
            self.connection.commit()
            self.cursor.execute("DELETE FROM parkingexit WHERE entry_id=%s",(id,))
            self.connection.commit()
        except mysql.connector.Error as err:
            print("Error : ",err)        
            
    def fetchlogin(self,username,password):
        try:
            self.cursor.execute("SELECT * FROM login WHERE loginid=%s AND password=%s",(username,password))
            if self.cursor.fetchone():
                return True
            else:
                return False
        except mysql.connector.Error as err:
            print("Error : ",err)
            
    def updatebillpayment(self,bill_id):
        try:
            self.cursor.execute("DELETE FROM bill WHERE bill_id=%s",(bill_id,))
            self.connection.commit()
        except mysql.connector.Error as err:
            print("Error : ",err)      
            
    def close(self):
        if self.connection.is_connected():
            self.cursor.close()
            self.connection.close()