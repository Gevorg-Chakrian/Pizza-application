from multiprocessing import Process, Lock
import threading
import datetime
import time
import random
from tkinter import *
import mysql.connector

database = mysql.connector.connect(
    host="localhost",
    user='root',
    password='89118132383gevA!',
    port='3306',
    database='pizza'
)

DEBUG = True
# DEBUG = False;

promo = ""
cursor = database.cursor(buffered=True)
# cursor.execute("INSERT into toppings values(20, 'vegan cheese', 1.5, 1)")
# database.commit()


from queue import Queue


def change_status(dp, status="idle"):
    cursor.execute(f"UPDATE deliveryperson SET status = '{status}' WHERE id = '{dp[0]}'")
    database.commit()


def to_lower(input):
    for i in input:
        i.lower()


def to_lists(input1, input2, input3):
    if input1 != "":
        input1_l = input1.split(", ")
        to_lower(input1_l)
    else:
        input1_l = []
    if input2 != "":
        input2_l = input2.split(", ")
        to_lower(input2_l)
    else:
        input2_l = []
    if input3 != "":
        input3_l = input3.split(", ")
        to_lower(input3_l)
    else:
        input3_l = []
    return input1_l, input2_l, input3_l


def get_order(input1, input2, input3, date=None, discount=None):
    input1_l, input2_l, input3_l = to_lists(input1, input2, input3)
    out = "-----------------------------------------------------------------------------------------------\n"
    out += "YOUR ORDER:"

    price = 0.00
    for i in input1_l:
        if i != "":
            i = str(i.title())
            cursor.execute(f"SELECT price FROM pizzas WHERE name = '{i}'")
            price_tmp = float(cursor.fetchone()[0])
            price += price_tmp
            out += "\n\t" + i + "\t€ " + str(price_tmp)

    for i in input2_l:
        if i != "":
            i = i.title()
            cursor.execute(f"SELECT price FROM desserts WHERE name = '{i}'")
            price_tmp = float(cursor.fetchone()[0])
            price += price_tmp
            out += "\n\t" + i + "\t€ " + str(price_tmp)

    for i in input3_l:
        if i != "":
            i = i.title()
            cursor.execute(f"SELECT price FROM drinks WHERE name = '{i}'")
            price_tmp = float(cursor.fetchone()[0])
            price += price_tmp
            out += "\n\t" + i + "\t€ " + str(price_tmp)
    if date:
        if discount:
            out += "\n-----------------------------------------------------------------------------------------------"
            out += "\nSubtotal:\t € " + str(round(price, 2))
            out += "\n-----------------------------------------------------------------------------------------------"
            out += "\nDiscount:\t € " + str(round(float(discount[1] / 100 * price), 2))
            out += "\n-----------------------------------------------------------------------------------------------"
            out += "\nTotal:\t\t € " + str(round(float(price - discount[1] / 100.0 * price), 2)) + "\t\t\t" + str(date)[
                                                                                                              :-7]
            out += "\n-----------------------------------------------------------------------------------------------"
        else:
            out += "\n\nTotal: \t€ " + str(round(price, 2)) + "\t\t\t\t\t" + str(date)[:-7]
            out += "\n-----------------------------------------------------------------------------------------------"
    else:
        out += "\n\nTotal: \t€ " + str(round(price, 2))
        out += "\n-----------------------------------------------------------------------------------------------"
    return out


def main():
    print("Welcome to the Pizza ordering app!")
    print("============================================ MENU ============================================")
    print("------------------------------------------- Pizzas -------------------------------------------")
    print("----------------------------------------------------------------------------------------------")
    out_pizza = ""
    cursor.execute(f"SELECT * FROM pizzas")
    pizzas = cursor.fetchall()
    for pizza_id in range(len(pizzas)):
        cursor.execute(f"SELECT name FROM pizzas WHERE id = {pizza_id + 1}")
        out_pizza += cursor.fetchone()[0] + "\t€ "
        cursor.execute(f"SELECT price FROM pizzas WHERE id = {pizza_id + 1}")
        out_pizza += str(cursor.fetchone()[0]) + "\n"
        cursor.execute(f"SELECT toppings FROM pizzas WHERE id = {pizza_id + 1}")
        toppings = str(cursor.fetchone()[0]).split(" ")
        top = ""
        for i in toppings:
            cursor.execute(f"SELECT name FROM toppings WHERE id = {i}")
            top += cursor.fetchone()[0] + ", "
        out_pizza += "Toppings: " + top[:-2] + " + "
        cursor.execute(f"SELECT sauce FROM pizzas WHERE id = {pizza_id + 1}")
        out_pizza += cursor.fetchone()[0]
        cursor.execute(f"SELECT vegetarian FROM pizzas WHERE id = {pizza_id + 1}")
        if cursor.fetchone()[0]:
            out_pizza += "\nVegetarian ✓"
        out_pizza += "\n-----------------------------------------------------------------------------------------------\n"
    print(out_pizza[:-2], )
    input1 = input("Enter your pizzas: ")
    out_desserts = "------------------------------------------ Desserts ------------------------------------------\n"
    cursor.execute(f"SELECT * FROM desserts")
    desserts = cursor.fetchall()
    for dessert_id in range(len(desserts)):
        cursor.execute(f"SELECT name FROM desserts WHERE id = {dessert_id + 1}")
        out_desserts += str(cursor.fetchone()[0]) + "\t€ "
        cursor.execute(f"SELECT price FROM desserts WHERE id = {dessert_id + 1}")
        out_desserts += cursor.fetchone()[0] + "\n"
    out_desserts += "-----------------------------------------------------------------------------------------------"
    print(out_desserts)
    input2 = input("Enter your desserts: ")
    out_drinks = "------------------------------------------- Drinks --------------------------------------------\n"
    cursor.execute(f"SELECT * FROM drinks")
    drinks = cursor.fetchall()
    for drink_id in range(len(drinks)):
        cursor.execute(f"SELECT name FROM drinks WHERE id = {drink_id + 1}")
        out_drinks += str(cursor.fetchone()[0]) + " "
        cursor.execute(f"SELECT lt FROM drinks WHERE id = {drink_id + 1}")
        out_drinks += str(cursor.fetchone()[0]) + "LT \t€ "
        cursor.execute(f"SELECT price FROM drinks WHERE id = {drink_id + 1}")
        out_drinks += str(cursor.fetchone()[0]) + "\n"
    out_drinks += "-----------------------------------------------------------------------------------------------"
    print(out_drinks)
    input3 = input("Enter your drinks: ")
    print(get_order(input1, input2, input3))
    editing = False
    request = ""
    while not editing:
        if request != "add":
            request = input(
                "Enter the word\n\t'Delete' to delete the undesired item(s),\n\t'Add' to add another item to your order,\n\t'Confirm' to confirm the order\nhere: ")
        request = request.lower()
        input1_l, input2_l, input3_l = to_lists(input1, input2, input3)
        if request == "delete":
            to_del = []
            print(get_order(input1, input2, input3))
            item = input("Enter the name(s) of the undesired item(s): ")
            item = item.split(", ")
            for i in item:

                i.lower()
            for i in item:
                for j in input1_l:
                    if i == j:
                        to_del.append(i)
                        break
            for i in to_del:
                input1_l.remove(i)
            to_del = []
            for i in item:
                for j in input2_l:
                    if i == j:
                        to_del.append(j)
                        break
            for i in to_del:
                input2_l.remove(i)
            to_del = []
            for i in item:
                for j in input3_l:
                    if i == j:
                        to_del.append(j)
                        break
            for i in to_del:
                input3_l.remove(i)
            to_del = []
            input1 = ", ".join(input1_l)
            input2 = ", ".join(input2_l)
            input3 = ", ".join(input3_l)
            print(get_order(input1, input2, input3))
        elif request == "add":
            checker = input("Type the category of the item(s) | Pizza | Dessert | Drink |: ")
            checker = checker.lower()
            if checker == "pizza":
                print(out_pizza)
                if input1 == "":
                    item = input("Enter the name(s) of the desired item(s): ")
                else:
                    item = input("Enter the name(s) of the desired item(s): " + input1 + ", ")
                if item != "":
                    if input1 == "":
                        input1 = item
                    else:
                        input1 = input1 + ", " + item
            elif checker == "dessert":
                print(out_desserts)
                if input2 == "":
                    item = input("Enter the name(s) of the desired item(s): ")
                else:
                    item = input("Enter the name(s) of the desired item(s): " + input2 + ", ")
                if item != "":
                    if input2 == "":
                        input2 = item
                    else:
                        input2 = input2 + ", " + item
            elif checker == "drink":
                print(out_drinks)
                if input3 == "":
                    item = input("Enter the name(s) of the desired item(s): ")
                else:
                    item = input("Enter the name(s) of the desired item(s): " + input3 + ", ")
                if item != "":
                    if input3 == "":
                        input3 = item
                    else:
                        input3 = input3 + ", " + item
            else:
                pass
            request = ""
            print(get_order(input1, input2, input3))
        elif request == "confirm":
            if len(input1) < 1:
                print("Each order must include at least one pizza. Please, order some pizza!")
                request = "add"
            else:
                name = ""
                print("-----------------------------------------------------------------------------------------------")
                print("-----------------------------------------------------------------------------------------------")
                order_time = datetime.datetime.now()
                print(get_order(input1, input2, input3, order_time))
                print("-----------------------------------------------------------------------------------------------")
                checker = input("Type\n\tSign up\t\tif first time\n\tLog in\t\tif you have ordered before\nhere: ")
                checker.lower()
                a, b, c = to_lists(input1, input2, input3)
                orders = len(a)
                customer = None
                if checker == "log in":
                    print(
                        "-----------------------------------------------------------------------------------------------")
                    phone = input("Enter your phone: ")
                    print(
                        "-----------------------------------------------------------------------------------------------")
                    cursor.execute(f"SELECT name, address, orders, phone FROM customer WHERE phone = {phone}")
                    customer = cursor.fetchone()
                    while not customer and checker != "sign up":
                        print(
                            "-----------------------------------------------------------------------------------------------")
                        phone = input("Wrong phone number! Try again or type 'Sign up': ")
                        print(
                            "-----------------------------------------------------------------------------------------------")
                        cursor.execute(f"SELECT name, address, orders, phone FROM customer WHERE phone = '{phone}'")
                        customer = cursor.fetchone()
                        if phone == "sign up":
                            checker = "sign up"
                    # if customer:
                    #     name = customer[0]
                    #     orders += int(customer[2])
                    #     cursor.execute(f"UPDATE customer SET orders = {orders} WHERE phone = '{customer[3]}'")
                    #     database.commit()
                if checker == "sign up":
                    print(
                        "-----------------------------------------------------------------------------------------------")
                    name = input("Enter your name: ")
                    phone = input("Enter your phone: ")
                    while True:
                        address = input("Enter your address: ")
                        cursor.execute(f"SELECT * FROM deliveryperson WHERE areacode = '{address}'")
                        post = cursor.fetchone()
                        if post:
                            break
                        else:
                            print("Your address is not correct. Please, try again.")
                    print(
                        "-----------------------------------------------------------------------------------------------")
                    cursor.execute(f"INSERT into customer values('{name}', '{phone}', '{address}', {orders})")
                    database.commit()
                cursor.execute(f"SELECT name, address, orders, phone FROM customer WHERE phone = {phone}")
                customer = cursor.fetchone()
                promocode = input(f"Welcome, {customer[0]}! Enter the promo-code if you have one: ")
                discount = None
                if promocode:
                    cursor.execute(f"SELECT * FROM promocodes WHERE code = '{promocode}'")
                    discount = cursor.fetchone()
                    while not discount and promocode:
                        promocode = input("Wrong promocode! Try again : ")
                        cursor.execute(f"SELECT * FROM promocodes WHERE code = '{promocode}'")
                        discount = cursor.fetchone()
                    if discount:
                        print(f"You have been awarded {discount[1]} % discount")
                        print(get_order(input1, input2, input3, order_time, discount))
                        cursor.execute(f"DELETE FROM promocodes WHERE code = '{discount[0]}' LIMIT 1")
                        database.commit()
                    else:
                        print(get_order(input1, input2, input3, order_time))
                else:
                    print(get_order(input1, input2, input3, order_time))

                editing = True

                cursor.execute(f"SELECT * FROM deliveryperson WHERE areacode = '{customer[1]}' and status = 'idle'")
                dp = cursor.fetchone()
                if dp:
                    cursor.execute(f"UPDATE deliveryperson SET status = 'in process' WHERE id = '{dp[0]}'")
                    database.commit()
                else:
                    print("Unfortunately, all delivery persons are busy, we are looking for a free rider!")
                    while not dp:
                        cursor.execute(
                            f"SELECT * FROM deliveryperson WHERE areacode = '{customer[1]}' and status = 'idle'")
                        dp = cursor.fetchone()
                        time.sleep(5)
                    cursor.execute(f"UPDATE deliveryperson SET status = 'in process' WHERE id = '{dp[0]}'")
                    database.commit()
                print("-------------------------------- Your courier is on their way! --------------------------------")

                def do():
                    if orders >= 10:
                        random.seed()
                        global promo
                        promo = str(customer[0]) + str(int(random.random() * 1000.0))
                        cursor.execute(f"INSERT into promocodes values('{promo}', 10)")
                        cursor.execute(f"UPDATE customer SET orders = {orders - 10} WHERE phone = '{customer[3]}'")
                        database.commit()
                        lbl.configure(text=f"{min_sec_format} remaining !!\n{get_order(input1, input2, input3, order_time, discount)}"
                                 f"\nYou have reached a milestone of 10 ordered pizzas! \nYou received a 10% discount on your next order with this fine promo-code!"
                                 f"\nPromo-code: {promo}")
                    else:
                        cursor.execute(f"UPDATE customer SET orders = {orders+int(customer[2])} WHERE phone = '{customer[3]}'")
                        database.commit()

                threading.Thread(target=main, daemon=True).start()
                time.sleep(1)
                window = Tk()
                window.title("Delivery app")
                window.after(900000, lambda: endtime(dp))
                window.after(300000, lambda: change_status(dp, "out for delivery"))
                window.after(301000, lambda: do())
                window.geometry('490x500')
                start = time.time()
                num_of_secs = 900
                m, s = divmod(num_of_secs, 60)
                min_sec_format = '{:02d} mins {:02d} seconds'.format(m, s)
                lbl = Label(window,
                            text=f"Hello, {min_sec_format}\n{get_order(input1, input2, input3, order_time, discount)}")
                lbl.grid(column=0, row=0)

                def clicked():
                    time_now = num_of_secs - int(time.time() - start)
                    m, s = divmod(time_now, 60)
                    min_sec_format = '{:02d} mins {:02d} seconds'.format(m, s)
                    if promo:
                        lbl.configure(
                            text=f"{min_sec_format} remaining!\n{get_order(input1, input2, input3, order_time, discount)}"
                                 f"\nYou have reached a milestone of 10 ordered pizzas! \nYou received a 10% discount on your next order with this fine promo-code!"
                                 f"\nPromo-code: {promo}")
                    else:
                        lbl.configure(
                            text=f"{min_sec_format} remaining!\n{get_order(input1, input2, input3, order_time, discount)}")

                def cancel():
                    time_now = num_of_secs - int(time.time() - start)
                    m, s = divmod(time_now, 60)
                    min_sec_format = '{:02d} mins {:02d} seconds'.format(m, s)
                    if time_now < 600:
                        if promo:
                            lbl.configure(
                                text=f"{min_sec_format} remaining! You cannot cancel your order. \n{get_order(input1, input2, input3, order_time, discount)}"
                                     f"\nYou have reached a milestone of 10 ordered pizzas! \nYou received a 10% discount on your next order with this fine promo-code!"
                                     f"\nPromo-code: {promo}")
                        else:
                            lbl.configure(
                                text=f"{min_sec_format} remaining! You cannot cancel your order. \n{get_order(input1, input2, input3, order_time, discount)}")
                        btn1.destroy()
                    else:

                        lbl.configure(text=f"your order is canceled!")
                        btn2.grid(column=0, row=1)
                        btn.destroy()
                        btn1.destroy()
                        change_status(dp, "idle")
                        # NUMBER OF ORDERS SHOULD BE DECREASED BU THE NUMBER OF ORDERED PIZZAS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

                def endtime(dp):
                    lbl.configure(text=f"Your order has arrived!")
                    btn.destroy()
                    btn1.destroy()
                    btn2.grid(column=0, row=1)
                    window.after(900000, change_status, dp)

                btn = Button(window, text="Status", command=clicked)
                btn.grid(column=0, row=1)
                btn1 = Button(window, text="Cancel the order", command=cancel)
                btn1.grid(column=0, row=2)
                btn2 = Button(window, text="Close", command=window.quit)
                window.mainloop()


def price_calculator():
    for pizza_id in range(10):
        price = 5  # initial price for dough
        cursor.execute(f"SELECT toppings FROM pizzas WHERE id = {pizza_id + 1}")
        recipe = cursor.fetchone()[0]
        toppings = str(recipe).split(" ")
        if DEBUG:
            print("toppings' ids: " + recipe)
        for i in toppings:
            cursor.execute(f"SELECT price FROM toppings WHERE id = {i}")
            topping = cursor.fetchone()[0]
            if DEBUG:
                print("topping's price: " + recipe)
            price += float(topping)
        cursor.execute(
            f"UPDATE pizzas SET price = {round(price + price * 0.09 + price * 0.4) + 0.99} WHERE id = {pizza_id + 1}")
        database.commit()


def vegetarian_calculator():
    for pizza_id_ in range(10):
        vegetarian_ = None
        cursor.execute(f"SELECT toppings FROM pizzas WHERE id = {pizza_id_ + 1}")
        recipe = cursor.fetchone()[0]
        if DEBUG:
            print("toppings' ids: " + recipe)
        toppings_ = str(recipe).split(" ")
        for i in toppings_:
            cursor.execute(f"SELECT vegetarian FROM toppings WHERE id = {i}")
            vegetarian_ = cursor.fetchone()[0]
            if not vegetarian_:
                if DEBUG:
                    print("PIZZA IS NOT VEGETARIAN")
                cursor.execute(f"UPDATE pizzas SET vegetarian = False WHERE id = {pizza_id_ + 1}")
                break
        if vegetarian_:
            if DEBUG:
                print("PIZZA IS VEGETARIAN")
            cursor.execute(f"UPDATE pizzas SET vegetarian = True WHERE id = {pizza_id_ + 1}")
        database.commit()


# vegetarian_calculator()
# price_calculator()


thread1 = threading.Thread(target=main, daemon=True)

thread1.start()
while True:
    time.sleep(1)
