from flask import Flask, render_template, jsonify
import socket
import json
from datetime import datetime, timedelta

app = Flask(__name__)

# Server IP and Port for communication
SERVER_IP = '34.47.222.9'  # Replace with actual server IP when deploying
SERVER_PORT = 12346

# Helper function to communicate with the server
def admin_communicate_with_server(request_data):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_IP, SERVER_PORT))
        client_socket.send(json.dumps(request_data).encode('utf-8'))
        
        response = client_socket.recv(4096).decode('utf-8')
        client_socket.close()
        return json.loads(response)
    except Exception as e:
        print(f"Error communicating with server: {e}")
        return None

# Route to display admin dashboard
@app.route('/')
def admin_dashboard():
    # Fetch employee data from the server
    employee_data_request = {'action': 'fetch_employee_data'}
    employee_data_response = admin_communicate_with_server(employee_data_request)
    
    # Add a check if the server response is None or invalid
    if employee_data_response is None:
        print("Failed to fetch employee data. Check server connection.")
        employees = []
    else:
        employees = employee_data_response.get('employee_data', [])
    
    dashboard_data = []

    for employee in employees:
        # Fetch current task status for each employee
        task_request = {'action': 'fetch_task_status', 'employee_name': employee}
        task_response = admin_communicate_with_server(task_request)
        if task_response is None:
            print(f"Failed to fetch task status for {employee}.")
            task_status = 'Ideal'
        else:
            task_status = task_response.get('task_status', 'Ideal')
        
        # Fetch break of the day log for each employee
        current_date = datetime.now().strftime('%Y-%m-%d')
        break_request = {'action': 'fetch_break_of_the_day', 'employee_name': employee, 'date': current_date}
        break_response = admin_communicate_with_server(break_request)
        if break_response is None:
            print(f"Failed to fetch break of the day for {employee}.")
            break_of_the_day = '00:00:00'
        else:
            break_of_the_day = break_response.get('break_of_the_day', '00:00:00')
        
        # Extract product and microservice
        product = task_status.get('Product', 'N/A') if isinstance(task_status, dict) else 'N/A'
        micro_service = task_status.get('Micro Service', 'N/A') if isinstance(task_status, dict) else 'N/A'
        
        # Format the task and break data for dashboard display
        task_description = task_status if isinstance(task_status, str) else task_status['Task Description']
        check_in_time = task_status.get('Check-In Time', 'Ideal') if isinstance(task_status, dict) else 'Ideal'

        # Add logic to convert check_in_time from UTC to IST
        if check_in_time != 'Ideal':
            check_in_time_obj = datetime.strptime(check_in_time, '%H:%M:%S')  # Assuming the format is 'HH:MM:SS'
            check_in_time_obj += timedelta(hours=5, minutes=30)  # Add 5 hours and 30 minutes for IST
            check_in_time = check_in_time_obj.strftime('%H:%M:%S')  # Convert it back to a string

        activity = task_status.get('Activity', 'Ideal') if isinstance(task_status, dict) else ''
        utilization = task_status.get('Utilization', '') if isinstance(task_status, dict) else ''
        
        # Check if the employee is on break (all fields are 'NA')
        if product == 'NA' and micro_service == 'NA' and task_description == 'NA' and activity == 'NA' and utilization == 'NA':
            product = ''
            micro_service = ''
            task_description = 'On Break'
            activity = ''
            utilization = ''
        
        # Add to dashboard data
        dashboard_data.append({
            'employee': employee,
            'product': product,
            'micro_service': micro_service,
            'task_description': task_description,
            'check_in_time': check_in_time,
            'activity': activity,
            'utilization': utilization,
            'break_of_the_day': break_of_the_day
        })
    
    # Render the dashboard page with the fetched data
    return render_template('dashboard.html', dashboard_data=dashboard_data)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
