import mysql.connector
from mysql.connector import Error
from datetime import datetime
import math



import re
from PIL import Image
import pytesseract

# IMPORTANT: If Tesseract is not in your system's PATH, you must specify its location.
# Uncomment and update the line below if you're on Windows.
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def read_plate_from_image(image_path):
    """Reads a vehicle number plate from an image file using OCR."""
    try:
        # Use Pillow to open the image
        image = Image.open(image_path)
        
        # Use pytesseract to extract text from the image
        raw_text = pytesseract.image_to_string(image)
        
        # Clean the extracted text to get a more accurate plate number.
        # This regex removes all non-alphanumeric characters.
        plate_number = re.sub(r'[\W_]+', '', raw_text).strip().upper()
        
        if not plate_number:
            print("## OCR could not detect any characters. ##")
            return None
            
        print(f"## OCR Result: '{plate_number}'")
        return plate_number
        
    except FileNotFoundError:
        print(f"## Error: Image file not found at '{image_path}'")
        return None
    except Exception as e:
        print(f"## An error occurred during OCR processing: {e}")
        return None
    
    
    

# --- Configuration ---
# Define separate parking capacities for each vehicle type.
PARKING_CAPACITIES = {"Car": 50, "Bike": 100, "Van": 20, "Cycle": 30}

# Hourly rates for different vehicle types.
HOURLY_RATES = {"Car": 40, "Bike": 20, "Van": 60, "Cycle": 10}


def get_db_connection():
    """Connects to the MySQL database with hardcoded credentials."""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password="Yeshu@2004", 
            database="ParkingDB",
            use_pure=True
        )
        return connection
    except Error as err:
        print(f"Error connecting to database: {err}")
        return None

def setup_database(connection):
    """Creates the database and table with the new schema."""
    if not connection:
        return
    
    cursor = connection.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ParkingRecords(
                parking_id INT AUTO_INCREMENT PRIMARY KEY,
                vehicle_number VARCHAR(30) NOT NULL,
                owner_name VARCHAR(50),
                vehicle_type VARCHAR(20),
                entry_time DATETIME,
                exit_time DATETIME NULL,
                status VARCHAR(5) DEFAULT 'in',
                final_fee DECIMAL(10, 2) NULL
            )
        """)
        connection.commit()
        print("Database and table are ready.")
    except Error as err:
        print(f"Error during database setup: {err}")
    finally:
        cursor.close()

def get_current_occupancy(connection):
    """Counts parked vehicles for each type and returns a dictionary."""
    occupancy = {v_type: 0 for v_type in PARKING_CAPACITIES}
    cursor = connection.cursor()
    try:
        query = "SELECT vehicle_type, COUNT(*) FROM ParkingRecords WHERE status = 'in' GROUP BY vehicle_type"
        cursor.execute(query)
        results = cursor.fetchall()
        for v_type, count in results:
            if v_type in occupancy:
                occupancy[v_type] = count
        return occupancy
    except Error as err:
        print(f"Database Error: {err}")
        return {}
    finally:
        cursor.close()

def add_vehicle(connection):
    """
    UPDATED: Checks for existing vehicle details before asking for them.
    """
    # This part remains the same: Display availability and get vehicle number
    current_occupancy = get_current_occupancy(connection)
    print(f"\n--- Add Vehicle ---")
    print("Parking Availability:")
    for v_type, max_capacity in PARKING_CAPACITIES.items():
        occupied = current_occupancy.get(v_type, 0)
        available = max_capacity - occupied
        print(f"  - {v_type}s: {available}/{max_capacity} available")

    image_path = input("\nEnter the path to the vehicle's number plate image: ").strip().strip('\'"')
    v_no = read_plate_from_image(image_path)

    if not v_no:
        print("\n## OCR failed. Please enter the number plate manually. ##")
        v_no = input("Enter Vehicle Number: ").strip()
    else:
        confirm = input(f"Is the vehicle number '{v_no}' correct? (y/n): ").strip().lower()
        if confirm != 'y':
            v_no = input("Please enter the correct vehicle number manually: ").strip()
    
    if not v_no:
        print("\n## Vehicle number cannot be empty. Check-in cancelled. ##")
        return
    
    # Convert to lowercase for consistent database storage and lookup
    v_no = v_no.lower()

    # ## --- NEW: Check for existing vehicle details --- ##
    name = None
    v_type = None
    cursor = connection.cursor()
    try:
        # Find the most recent record for this vehicle number
        find_query = "SELECT owner_name, vehicle_type FROM ParkingRecords WHERE vehicle_number = %s ORDER BY entry_time DESC LIMIT 1"
        cursor.execute(find_query, (v_no,))
        record = cursor.fetchone()
        if record:
            name, v_type = record
            print(f"\n## Welcome back, {name}! Details found for vehicle type: {v_type}. ##")
    except Error as err:
        print(f"## Database error while checking vehicle history: {err} ##")
    finally:
        cursor.close()

    # ## --- UPDATED: Prompt for details only if they weren't found --- ##
    if not name:
        name = input("Enter Owner's Name: ").strip()
    
    if not v_type:
         v_type = input(f"Enter Vehicle Type ({', '.join(HOURLY_RATES.keys())}): ").strip().capitalize()

    # --- Validation and Insertion Logic ---
    if not name:
        print("\n## Owner name is required. Record not saved. ##")
        return
            
    if v_type not in PARKING_CAPACITIES:
        print(f"\n## Invalid vehicle type '{v_type}'. Please use one of: {list(PARKING_CAPACITIES.keys())} ##")
        return
    
    occupied_count = current_occupancy.get(v_type, 0)
    max_capacity = PARKING_CAPACITIES[v_type]
    if occupied_count >= max_capacity:
        print(f"\n## Sorry, the parking area for '{v_type}' is full. ##")
        return

    # Insert the new check-in record
    cursor = connection.cursor()
    try:
        query = """
            INSERT INTO ParkingRecords 
            (vehicle_number, owner_name, vehicle_type, entry_time) 
            VALUES (%s, %s, %s, NOW())
        """
        values = (v_no, name, v_type)
        cursor.execute(query, values)
        connection.commit()
        print(f"\n## {v_type} with number plate '{v_no.upper()}' checked in successfully! ##")
    except Error as err:
        print(f"Database Error: {err}")
        connection.rollback()
    finally:
        cursor.close()

def update_vehicle_status(connection):
    """
    UPDATED: First checks if any vehicles are parked before proceeding.
    """
    # --- NEW: Check if any vehicle is parked before starting the process ---
    # We can reuse our existing function for this.
    total_parked = sum(get_current_occupancy(connection).values())
    if total_parked == 0:
        print("\n## There are no vehicles currently parked. Cannot proceed with checkout. ##")
        return # Exit the function immediately

    # --- The checkout process starts here if vehicles are present ---
    print("\n--- Vehicle Checkout ---")
    print("Please select a vehicle from the list below to check out.")

    # Display the list of currently parked vehicles for the user's convenience
    cursor = connection.cursor()
    try:
        query = "SELECT * FROM ParkingRecords WHERE status = 'in' ORDER BY entry_time DESC"
        cursor.execute(query)
        display_records(cursor)
    except Error as err:
        print(f"Database Error: {err}")
        cursor.close()
        return
    finally:
        cursor.close()
    
    # Get vehicle number via OCR or manual entry
    # Note: This logic uses a file path. To use the camera, we would call capture_image_from_camera() here.
    image_path = input("\nEnter the path to the vehicle's number plate image: ").strip().strip('\'"')
    v_no = read_plate_from_image(image_path)

    if not v_no:
        print("\n## OCR failed. Please enter the number plate manually. ##")
        v_no = input("Enter Vehicle Number: ").strip()
    else:
        confirm = input(f"Is the vehicle number '{v_no.upper()}' correct? (y/n): ").strip().lower()
        if confirm != 'y':
            v_no = input("Please enter the correct vehicle number manually: ").strip()
    
    if not v_no:
        print("Vehicle number cannot be empty. Checkout cancelled.")
        return

    v_no = v_no.lower()

    # Proceed with checkout in the database
    cursor = connection.cursor()
    try:
        find_query = "SELECT owner_name, entry_time, vehicle_type FROM ParkingRecords WHERE vehicle_number = %s AND status = 'in'"
        cursor.execute(find_query, (v_no,))
        record = cursor.fetchone()

        if not record:
            print(f"\n## No active parked vehicle found with number '{v_no.upper()}'. ##")
            return

        owner_name, entry_time, vehicle_type = record
        exit_time = datetime.now()
        
        duration_seconds = (exit_time - entry_time).total_seconds()
        # Use math.ceil to round up to the next full hour
        duration_hours = math.ceil(duration_seconds / 3600)
        
        if duration_hours < 1:
            duration_hours = 1
            
        rate_per_hour = HOURLY_RATES.get(vehicle_type, 0)
        final_fee = round(duration_hours * rate_per_hour, 2)
        
        print(f"\n  Duration: {duration_hours} hour(s)")
        print(f"  Rate: Rs.{rate_per_hour}/hr")
        print(f"  Total Fee: Rs.{final_fee:.2f}")

        update_query = """
            UPDATE ParkingRecords 
            SET status = 'out', exit_time = %s, final_fee = %s
            WHERE vehicle_number = %s AND status = 'in'
        """
        cursor.execute(update_query, (exit_time, final_fee, v_no))
        connection.commit()
        print("\n## Vehicle checked out successfully! ##")

        # Generate the PDF receipt
        receipt_details = {
            "vehicle_number": v_no, "owner_name": owner_name, "entry_time": entry_time,
            "exit_time": exit_time, "duration": duration_hours, "fee": final_fee
        }
        generate_pdf_receipt(receipt_details)

    except Error as err:
        print(f"Database Error: {err}")
        connection.rollback()
    finally:
        cursor.close()
        
def display_records(cursor):
    """Helper function to display fetched records in a formatted way."""
    results = cursor.fetchall()
    if not results:
        print("\n## No records found. ##")
        return
    
    print("\n--- Parking Records ---")
    print(f"{'ID':<5} {'Vehicle No.':<15} {'Owner':<20} {'Type':<10} {'Status':<8} {'Fee':<10} {'Entry Time':<20} {'Exit Time'}")
    print("-" * 125)

    for row in results:
        parking_id, v_no, name, v_type, entry, exit_t, status, fee = row
        
        entry_t_str = entry.strftime('%Y-%m-%d %H:%M') if entry else 'N/A'
        exit_t_str = exit_t.strftime('%Y-%m-%d %H:%M') if exit_t else 'N/A'
        fee_str = f"Rs.{fee}" if fee is not None else 'N/A'
        
        print(f"{parking_id:<5} {v_no:<15} {name:<20} {v_type:<10} {status:<8} {fee_str:<10} {entry_t_str:<20} {exit_t_str}")
    print("-" * 125)

def search_vehicles(connection):
    """Searches for vehicles based on user criteria."""
    print("\n--- Search Options ---")
    print("1. Show all currently parked vehicles")
    print("2. Show all records (including departed)")
    print("3. Search by vehicle number")
    
    try:
        choice = int(input("Enter your choice: "))
    except ValueError:
        print("## Invalid choice. Please enter a number. ##")
        return
        
    cursor = connection.cursor()
    
    columns = "parking_id, vehicle_number, owner_name, vehicle_type, entry_time, exit_time, status, final_fee"
    query = ""
    params = ()

    if choice == 1:
        query = f"SELECT {columns} FROM ParkingRecords WHERE status = 'in' ORDER BY entry_time DESC"
    elif choice == 2:
        query = f"SELECT {columns} FROM ParkingRecords ORDER BY entry_time DESC"
    elif choice == 3:
        v_no = input("Enter vehicle number to search for: ").strip().lower()
        if not v_no:
            print("Vehicle number cannot be empty.")
            cursor.close()
            return
        query = f"SELECT {columns} FROM ParkingRecords WHERE vehicle_number = %s ORDER BY entry_time DESC"
        params = (v_no,)
    else:
        print("## Invalid choice. ##")
        cursor.close()
        return

    try:
        cursor.execute(query, params)
        display_records(cursor)
    except Error as err:
        print(f"Database Error: {err}")
    finally:
        cursor.close()
        
        
def display_availability(connection):
    """Calculates and displays the number of available parking spots for each vehicle type."""
    try:
        current_occupancy = get_current_occupancy(connection)
        
        print("\n--- Parking Availability ---")
        total_available = 0
        total_capacity = 0

        # Display availability for each vehicle type
        for v_type, max_capacity in PARKING_CAPACITIES.items():
            occupied = current_occupancy.get(v_type, 0)
            available = max_capacity - occupied
            print(f"  - {v_type}s: {available} out of {max_capacity} spots available.")
            total_available += available
            total_capacity += max_capacity
        
        # Display total availability
        print("-" * 45)
        print(f"  - Total: {total_available} out of {total_capacity} spots available.")
        print("-" * 45)

    except Exception as e:
        print(f"## An error occurred while fetching availability: {e}")
        

def run_parking_system():
    """Main function to run the application loop."""
    connection = get_db_connection()
    if not connection:
        print("## Exiting program due to connection failure. ##")
        return
        
    setup_database(connection)

    while True:
        print("\n======== Parking Management System ========")
        print("1. Check-In a New Vehicle")
        print("2. Check-Out a Vehicle")
        print("3. Search & View Records")
        print("4. View Parking Availability")  # <-- New menu option
        print("0. Exit")
        
        try:
            choice = int(input("Enter your choice: "))
        except ValueError:
            print("\n## Invalid input. Please enter a number. ##")
            continue

        if choice == 1:
            add_vehicle(connection)
        elif choice == 2:
            update_vehicle_status(connection)
        elif choice == 3:
            search_vehicles(connection)
        elif choice == 4:  # <-- New logic to call the function
            display_availability(connection)
        elif choice == 0:
            print("\n## Thank you for using the system! ##")
            break
        else:
            print("\n## Invalid choice, please try again. ##")

    connection.close()


# --- Entry point of the program ---
if __name__ == "__main__":
    run_parking_system()
