
from flask import Flask, redirect, render_template, request, session, url_for
import pymysql
import pymysql.cursors
import bcrypt
import os
import sys

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "default_key_for_development")

# Configure MySQL
connection = pymysql.connect(
    host="localhost",           # Your database host (default is localhost)
    user="root",                # Your MySQL username
    password="root",            # Your MySQL password
    database="project3f",            # Your database name
    port=3306,
    connect_timeout=600,
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

@app.route("/")
def h():
    # Render the home page
    return render_template("index.html")

@app.route('/register')
def register():
    # Render the registration page
    return render_template('register.html')

@app.route('/login')
def login():
    # Render the login page
    return render_template('login.html')

@app.route('/registerAuth', methods=['POST'])
def registerAuth():
    # Grab form data
    username = request.form['username']
    password = request.form['password']
    fname = request.form['fname']
    lname = request.form['lname']
    email = request.form['email']
    phone = request.form['phone']
    role = request.form['role']

    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    cursor = connection.cursor()

    # Check if the user already exists
    query = 'SELECT * FROM user WHERE username = %s'
    cursor.execute(query, (username,))
    data = cursor.fetchone()

    if data:
        error = "User already exists"
        cursor.close()
        return render_template('register.html', error=error)
    else:
        try:
            # Insert into user table
            cursor.execute('INSERT INTO user (username, password, fname, lname, email) VALUES (%s, %s, %s, %s, %s)',
                           (username, hashed_password, fname, lname, email))

            # Insert phone number into PersonPhone table
            cursor.execute('INSERT INTO PersonPhone (username, phone) VALUES (%s, %s)', (username, phone))

            # Insert into the appropriate role table
            if role == 'staff':
                cursor.execute('INSERT INTO staff (username, staff_details) VALUES (%s, %s)', (username, ''))
            elif role == 'client':
                cursor.execute('INSERT INTO client (username, client_details) VALUES (%s, %s)', (username, ''))
            elif role == 'volunteer':
                cursor.execute('INSERT INTO volunteer (username, volunteer_details) VALUES (%s, %s)', (username, ''))

            connection.commit()
            log_action(username, role, "Registered as " + role)
        except pymysql.MySQLError as e:
            connection.rollback()
            error = f"Database error: {e}"
            return render_template('register.html', error=error)
        finally:
            cursor.close()

        return redirect(url_for('login'))



    
@app.route('/loginAuth', methods=['POST'])
def loginAuth():
    username = request.form['username']
    password = request.form['password']
    role = request.form['role']

    cursor = connection.cursor()
    
    # Validate user credentials
    query = 'SELECT password FROM user WHERE username = %s'
    cursor.execute(query, (username,))
    data = cursor.fetchone()
    
    if data and bcrypt.checkpw(password.encode('utf-8'), data['password'].encode('utf-8')):
        # Check if user exists in the appropriate role table
        role_query = f'SELECT * FROM {role} WHERE username = %s'
        cursor.execute(role_query, (username,))
        role_data = cursor.fetchone()
        
        if role_data:
            session['username'] = username
            session['role'] = role
            log_action(username, role, "Logged in")
            return redirect(url_for('home'))
        else:
            error = f"User does not exist in the {role} role."
    else:
        error = "Invalid username or password"
    
    cursor.close()
    return render_template('login.html', error=error)


@app.route('/home')
def home():
    if 'username' not in session or 'role' not in session:
        return redirect(url_for('login'))  # Redirect to login if not authenticated

    user = session['username']
    role = session['role']

    if role == 'client':
        return render_template('clientHome.html', username=user)
    elif role == 'staff':
        return render_template('staffHome.html', username=user)
    
    else:
        cursor = connection.cursor()
        query = '''
        SELECT orderID, status, deliveryDate
        FROM Delivered
        WHERE username = %s
        '''
        cursor.execute(query, (user,))
        deliveries = cursor.fetchall()
        cursor.close()
        return render_template('volunteerHome.html', username=user, deliveries=deliveries)


@app.route('/findSingleItem')
def findSingleItem():
    return render_template('findSingleItem.html')

@app.route('/findSingleItemResult', methods=['POST'])
def findSingleItemResult():
    item_id = request.form['itemID']
    cursor = connection.cursor()
    query = '''
        SELECT p.pieceNum, l.roomNum, l.shelfNum, l.shelfDescription
        FROM Piece p
        JOIN Location l ON p.roomNum = l.roomNum AND p.shelfNum = l.shelfNum
        WHERE p.itemID = %s
    '''
    cursor.execute(query, (item_id,))
    data = cursor.fetchall()
    cursor.close()
    
    if data:
        return render_template('findSingleItemResult.html', results=data, itemID=item_id)
    else:
        error = f"No locations found for Item ID: {item_id}"
        return render_template('findSingleItem.html', error=error)

@app.route('/logout')
def logout():
    session.pop('username')
    return redirect('/')



@app.route('/findOrderItemsResult', methods=['POST'])
def findOrderItemsResult():
    if 'role' not in session or 'username' not in session:
        return redirect(url_for('login'))  # Redirect if session is invalid

    order_id = request.form['orderID']
    role = session['role']
    username = session['username']

    cursor = connection.cursor()
    query = None

    # Role-specific query
    if role == 'client':
        query = '''
            SELECT i.itemID, i.iDescription, p.pieceNum, l.roomNum, l.shelfNum, l.shelfDescription
            FROM ItemIn ii
            JOIN Item i ON ii.itemID = i.itemID
            JOIN Piece p ON i.itemID = p.itemID
            JOIN Location l ON p.roomNum = l.roomNum AND p.shelfNum = l.shelfNum
            JOIN Ordered o ON ii.orderID = o.orderID
            WHERE ii.orderID = %s AND o.client = %s
        '''
        cursor.execute(query, (order_id, username))
    elif role == 'staff':
        query = '''
            SELECT i.itemID, i.iDescription, p.pieceNum, l.roomNum, l.shelfNum, l.shelfDescription
            FROM ItemIn ii
            JOIN Item i ON ii.itemID = i.itemID
            JOIN Piece p ON i.itemID = p.itemID
            JOIN Location l ON p.roomNum = l.roomNum AND p.shelfNum = l.shelfNum
            WHERE ii.orderID = %s
        '''
        cursor.execute(query, (order_id,))
    elif role == 'volunteer':
        query = '''
            SELECT i.itemID, i.iDescription, p.pieceNum, l.roomNum, l.shelfNum, l.shelfDescription
            FROM ItemIn ii
            JOIN Item i ON ii.itemID = i.itemID
            JOIN Piece p ON i.itemID = p.itemID
            JOIN Location l ON p.roomNum = l.roomNum AND p.shelfNum = l.shelfNum
            JOIN Delivered d ON d.orderID = ii.orderID
            WHERE ii.orderID = %s AND d.username = %s
        '''
        cursor.execute(query, (order_id, username))
    else:
        cursor.close()
        error = "Access Denied: Your role does not permit viewing order items."
        return render_template('clientHome.html', username=username, error=error)

    data = cursor.fetchall()
    cursor.close()

    # Check if data exists
    if data:
        log_action(session['username'], session['role'], f"Viewed order ID {order_id}")
        return render_template('findOrderItemsResult.html', results=data, orderID=order_id)
    else:
        error = f"No items found for Order ID: {order_id}."
        return render_template('clientHome.html', username=username, error=error)


@app.route('/checkDonor')
def checkDonor():
    if 'role' not in session or session['role'] != 'staff':
        return redirect(url_for('login'))  # Redirect if unauthorized

    return render_template('checkDonor.html')  # Ask for donorID


@app.route('/verifyDonor', methods=['POST'])
def verifyDonor():
    if 'role' not in session or session['role'] != 'staff':
        return redirect(url_for('login'))  # Ensure only staff can access

    donorID = request.form['donorID']  # Get donorID from form

    cursor = connection.cursor()
    query = 'SELECT * FROM Donor WHERE donorID = %s'
    cursor.execute(query, (donorID,))
    donor_data = cursor.fetchone()

    if donor_data:
        # Redirect to accept donation if donorID is valid
        return redirect(url_for('acceptDonation', donorID=donorID))
    else:
        # Prompt to register the donor
        return render_template('registerDonor.html', error="Donor ID not found. Please register the donor.", donorID=donorID)


@app.route('/registerDonor', methods=['POST'])
def registerDonor():
    donorID = request.form['donorID']
    donorDetails = request.form['donorDetails']
    username = request.form['username']  # Assume username is provided

    cursor = connection.cursor()
    query = 'INSERT INTO Donor (donorID, username, donorDetails) VALUES (%s, %s, %s)'
    try:
        cursor.execute(query, (donorID, username, donorDetails))
        connection.commit()
        return redirect(url_for('checkDonor'))  # Redirect to verify donor
    except pymysql.MySQLError as e:
        connection.rollback()
        return render_template('registerDonor.html', error=f"Error registering donor: {e}")
    finally:
        cursor.close()


@app.route('/acceptDonation', methods=['GET'])
def acceptDonation():
    if 'role' not in session or session['role'] != 'staff':
        return redirect(url_for('login'))  # Redirect if unauthorized

    donorID = request.args.get('donorID')
    if not donorID:
        return render_template('acceptDonation.html', error="Donor ID is missing.")

    return render_template('acceptDonation.html', donorID=donorID)


@app.route('/saveDonation', methods=['POST'])
def saveDonation():
    if 'role' not in session or session['role'] != 'staff':
        return redirect(url_for('login'))  # Redirect if unauthorized

    # Retrieve form data
    donorUsername = request.form.get('donorUsername')
    iDescription = request.form.get('iDescription')
    photo = request.form.get('photo')
    color = request.form.get('color')
    isNew = request.form.get('isNew') == 'yes'
    hasPieces = request.form.get('hasPieces') == 'yes'
    material = request.form.get('material')
    mainCategory = request.form.get('mainCategory')
    subCategory = request.form.get('subCategory')
    locationData = request.form.getlist('locations')

    cursor = connection.cursor()
    try:
        # Validate donor
        query_check_donor = '''
            SELECT * FROM Donor WHERE username = %s
        '''
        cursor.execute(query_check_donor, (donorUsername,))
        donor_data = cursor.fetchone()

        if not donor_data:
            return render_template('acceptDonation.html', error="Donor username not found. Please register the donor.")

        # Insert item
        query_item = '''
            INSERT INTO Item (iDescription, photo, color, isNew, hasPieces, material, mainCategory, subCategory)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        '''
        cursor.execute(query_item, (iDescription, photo, color, isNew, hasPieces, material, mainCategory, subCategory))
        itemID = cursor.lastrowid

        # Insert donation
        query_donation = '''
            INSERT INTO Donation (donorUsername, donationDate, itemID)
            VALUES (%s, CURDATE(), %s)
        '''
        cursor.execute(query_donation, (donorUsername, itemID))

        # Handle piece data and ensure location exists
        for location in locationData:
            try:
                roomNum, shelfNum, shelfDescription = location.split(',')

                # Ensure the location exists in the Location table
                query_check_location = '''
                    SELECT * FROM Location WHERE roomNum = %s AND shelfNum = %s
                '''
                cursor.execute(query_check_location, (roomNum, shelfNum))
                location_exists = cursor.fetchone()

                if not location_exists:
                    # Insert missing location
                    query_insert_location = '''
                        INSERT INTO Location (roomNum, shelfNum, shelfDescription)
                        VALUES (%s, %s, %s)
                    '''
                    cursor.execute(query_insert_location, (roomNum, shelfNum, shelfDescription))

                # Insert piece
                query_piece = '''
                    INSERT INTO Piece (itemID, pieceNum, pDescription, roomNum, shelfNum, pNotes)
                    VALUES (%s, %s, %s, %s, %s, %s)
                '''
                cursor.execute(query_piece, (itemID, 1, iDescription, roomNum, shelfNum, shelfDescription))
            except ValueError:
                connection.rollback()
                return render_template('acceptDonation.html', error="Invalid location data format.")

        connection.commit()
        return render_template('donationSuccess.html', itemID=itemID, iDescription=iDescription)
    except pymysql.MySQLError as e:
        connection.rollback()
        return render_template('acceptDonation.html', error=f"Database error: {e}")
    finally:
        cursor.close()






def log_action(username, role, action):
    cursor = connection.cursor()
    query = '''
        INSERT INTO TransactionLog (username, role, action)
        VALUES (%s, %s, %s)
    '''
    cursor.execute(query, (username, role, action))
    connection.commit()
    cursor.close()


@app.route('/viewLogs')
def viewLogs():
    if 'role' not in session or session['role'] != 'staff':
        return redirect(url_for('login'))  # Only staff can view logs

    cursor = connection.cursor()
    query = 'SELECT * FROM TransactionLog ORDER BY timestamp DESC'
    cursor.execute(query)
    logs = cursor.fetchall()
    cursor.close()

    return render_template('viewLogs.html', logs=logs)


@app.route('/myOrders', methods=['GET'])
def myOrders():
    if 'username' not in session or 'role' not in session:
        return redirect(url_for('login'))  # Ensure user is logged in

    username = session['username']
    role = session['role']
    cursor = connection.cursor()

    # if role == 'client':
    #     query = '''
    #         SELECT orderID, orderDate, orderNotes
    #         FROM Ordered
    #         WHERE client = %s;
    #     '''
    # elif role == 'volunteer':
    query = '''
    SELECT 
        o.orderID, o.orderDate, o.orderNotes, d.status, d.deliveryDate, d.username AS volunteer, 
        o.client, o.supervisor,
        client_user.fname AS client_fname, client_user.lname AS client_lname,
        supervisor_user.fname AS supervisor_fname, supervisor_user.lname AS supervisor_lname
    FROM Ordered o
    LEFT JOIN Delivered d ON o.orderID = d.orderID
    LEFT JOIN user client_user ON o.client = client_user.username
    LEFT JOIN user supervisor_user ON o.supervisor = supervisor_user.username
    WHERE d.username = %s OR o.client = %s OR o.supervisor = %s;
    '''
    # elif role == 'staff':
    #     query = '''
    #         SELECT orderID, orderDate, orderNotes, client
    #         FROM Ordered
    #         WHERE supervisor = %s;
    #     '''
    # else:
        # return "Access Denied"  # Handle invalid roles

    cursor.execute(query, (username,username,username))
    orders = cursor.fetchall()
    ## to do WHERE d.username = %s OR o.client= %s OR o.supervisor=%s;
    print(orders,file=sys.stdout)
    cursor.close()
    neworders=[]
    for order in orders:
    # Assign role based on the logged-in user's relationship with the order
        if order.get("client") == username:
            order['role'] = "client"
        elif order.get("volunteer") == username:
            order['role'] = "volunteer"
        elif order.get("supervisor") == username:
            order['role'] = "supervisor"
        else:
            order['role'] = "unknown"  # Just in case, for debugging

        neworders.append(order)

    return render_template('myOrders.html', orders=neworders, username=username)


@app.route('/popularCategories', methods=['GET', 'POST'])
def popularCategories():
    if 'role' not in session or session['role'] != 'staff':
        return redirect(url_for('login'))  # Only staff can view this page

    rankings = None
    error = None
    message = None

    if request.method == 'POST':
        # Get the date range from the form
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        cursor = connection.cursor()

        try:
            # Execute the ranking query
            query = '''
                SELECT 
                    c.mainCategory,
                    c.subCategory,
                    COUNT(DISTINCT ii.orderID) AS num_orders
                FROM 
                    Category c
                JOIN 
                    Item i ON c.mainCategory = i.mainCategory AND c.subCategory = i.subCategory
                JOIN 
                    ItemIn ii ON i.itemID = ii.itemID
                JOIN 
                    Ordered o ON ii.orderID = o.orderID
                WHERE 
                    o.orderDate BETWEEN %s AND %s
                GROUP BY 
                    c.mainCategory, c.subCategory
                ORDER BY 
                    num_orders DESC
                LIMIT 10;
            '''
            cursor.execute(query, (start_date, end_date))
            rankings = cursor.fetchall()

            if not rankings:
                message = "No products found between these dates. Please select a different date range."
        except pymysql.MySQLError as e:
            error = f"Database error: {e}"
        finally:
            cursor.close()

    return render_template(
        'popularCategories.html',
        rankings=rankings,
        error=error,
        message=message,
        enumerate=enumerate
    )


@app.route('/yearEndReport', methods=['GET'])
def yearEndReport():
    if 'role' not in session or session['role'] != 'staff':
        return redirect(url_for('login'))  # Only staff can access this page

    cursor = connection.cursor()
    error = None

    try:
        # Query 1: Number of Clients Served
        query_clients_served = '''
            SELECT COUNT(DISTINCT o.client) AS clients_served
            FROM Ordered o;
        '''
        cursor.execute(query_clients_served)
        clients_served = cursor.fetchone()['clients_served']

        # Query 2: Number of Items Donated by Category
        query_items_donated = '''
            SELECT 
                c.mainCategory, 
                c.subCategory, 
                COUNT(i.itemID) AS total_items
            FROM 
                Category c
            LEFT JOIN 
                Item i ON c.mainCategory = i.mainCategory AND c.subCategory = i.subCategory
            GROUP BY 
                c.mainCategory, c.subCategory;
        '''
        cursor.execute(query_items_donated)
        items_donated = cursor.fetchall()

        # Query 3: Summary of How Clients Were Helped
        query_clients_helped = '''
            SELECT 
                o.client AS client_username, 
                COUNT(DISTINCT o.orderID) AS total_orders, 
                COUNT(ii.itemID) AS total_items_received
            FROM 
                Ordered o
            LEFT JOIN 
                ItemIn ii ON o.orderID = ii.orderID
            GROUP BY 
                o.client;
        '''
        cursor.execute(query_clients_helped)
        clients_helped_summary = cursor.fetchall()

    except pymysql.MySQLError as e:
        error = f"Database error: {e}"
    finally:
        cursor.close()

    return render_template(
        'yearEndReport.html',
        clients_served=clients_served,
        items_donated=items_donated,
        clients_helped_summary=clients_helped_summary,
        error=error
    )


@app.route('/updateOrderStatus', methods=['GET', 'POST'])
def updateOrderStatus():
    if 'role' not in session or 'username' not in session:
        return redirect(url_for('login'))  # Redirect if not logged in

    username = session['username']
    role = session['role']

    cursor = connection.cursor()

    try:
        if request.method == 'GET':
            # Check orders supervised by the staff
            supervised_orders = []
            if role == 'staff':
                query_supervised = '''
                    SELECT o.orderID, o.orderDate, o.orderNotes, o.status
                    FROM Ordered o
                    WHERE o.supervisor = %s
                '''
                cursor.execute(query_supervised, (username,))
                supervised_orders = cursor.fetchall()

            # Check orders delivered by the volunteer
            delivered_orders = []
            if role == 'volunteer':
                query_delivered = '''
                    SELECT d.orderID, o.orderDate, o.orderNotes, o.status
                    FROM Delivered d
                    JOIN Ordered o ON d.orderID = o.orderID
                    WHERE d.username = %s
                '''
                cursor.execute(query_delivered, (username,))
                delivered_orders = cursor.fetchall()

            return render_template(
                'updateOrderStatus.html',
                supervised_orders=supervised_orders,
                delivered_orders=delivered_orders,
                role=role
            )

        elif request.method == 'POST':
            # Handle status update
            order_id = request.form['orderID']
            new_status = request.form['status']

            # Ensure the user is allowed to update the order
            allowed = False
            if role == 'staff':
                query_check = '''
                    SELECT * FROM Ordered
                    WHERE orderID = %s AND supervisor = %s
                '''
                cursor.execute(query_check, (order_id, username))
                allowed = cursor.fetchone()
            elif role == 'volunteer':
                query_check = '''
                    SELECT * FROM Delivered
                    WHERE orderID = %s AND username = %s
                '''
                cursor.execute(query_check, (order_id, username))
                allowed = cursor.fetchone()

            if allowed:
                # Update the order status
                query_update = '''
                    UPDATE Ordered
                    SET status = %s
                    WHERE orderID = %s
                '''
                cursor.execute(query_update, (new_status, order_id))
                connection.commit()

                return redirect(url_for('updateOrderStatus'))
            else:
                error = "You are not authorized to update this order."
                return render_template('updateOrderStatus.html', error=error)

    except pymysql.MySQLError as e:
        error = f"Database error: {e}"
        return render_template('updateOrderStatus.html', error=error)

    finally:
        cursor.close()



if __name__ == "__main__":
    app.run(debug=True)
