# User Monitoring - Task Management Web Application

Welcome to the **User Monitoring** project! This web application is designed to help users manage their tasks effectively, providing features such as task prioritization, a calendar view, and robust CRUD operations (Create, Read, Update, Delete). It also enables users to track and visualize their daily activities, offering insights into their productivity.

Built with **Django** for the backend and **JavaScript** for dynamic frontend behavior, this application serves as a powerful task management tool where users can manage their daily schedules, input activity data, and analyze it with visualizations.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Key Pages and Functionality](#key-pages-and-functionality)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Task Management**: Users can create, view, and delete tasks.
- **Task Prioritization**: Tasks can be categorized as High, Medium, or Important.
- **Calendar View**: A visual calendar interface to view tasks for each day.
- **CRUD Operations**: Full support for task creation, reading, updating, and deletion.
- **User Activity Input**: Users can log daily activities such as time spent on tasks, task completion status, etc.
- **Data Visualization**: Graphs and charts to visualize daily activity data and track productivity trends.
- **Responsive Design**: Optimized for different screen sizes, ensuring a smooth experience across devices.

## Installation

Follow the steps below to set up the project locally.

1. **Clone the repository**:

   ```bash
   git clone https://github.com/your-username/user_monitoring.git
   cd user_monitoring
   ```

2. **Set up a virtual environment** (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install the dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Apply database migrations**:

   ```bash
   python manage.py migrate
   ```

5. **Run the development server**:

   ```bash
   python manage.py runserver
   ```

6. Open your browser and go to `http://127.0.0.1:8000/` to access the application.

## Key Pages and Functionality

### 1. **Calendar View**:
   - The calendar displays tasks assigned to specific dates, color-coded based on priority (e.g., High, Medium, Important).
   - Users can click on any date to view tasks for that day.
   - From the calendar view, tasks can be added, edited, prioritized, or deleted.

### 2. **Task List**:
   - Displays all tasks in a list format, where each task can be marked as completed.
   - Tasks are categorized with priorities such as "High," "Medium," or "Important."
   - Tasks can be selected to modify their priority or delete them.

### 3. **Input Daily Activities**:
   - This page allows users to input data regarding their daily activities.
   - The form collects various types of information, such as hours spent on specific tasks and task completion status.
   - After submission, the data is stored in the database for future analysis.

### 4. **Data Visualization**:
   - This page visualizes the user’s daily activity data in graphical form (e.g., bar charts, pie charts).
   - The visualizations provide insights into how time is spent on different activities, helping users track productivity trends.
   - Users can analyze and compare data over different periods to improve their time management.

## Project Structure

Here’s an overview of the project’s file structure:

```
user_monitoring/
├── db.sqlite3               # SQLite database file for the project
├── manage.py                # Django's command-line utility for project management
├── monitor/                  # Main application folder
│   ├── admin.py              # Register models with Django Admin
│   ├── apps.py               # App configuration settings
│   ├── forms.py              # Forms for creating and editing tasks
│   ├── models.py             # Defines the database models for tasks and activities
│   ├── views.py              # Views for rendering templates and handling logic
│   ├── templates/            # HTML templates for rendering pages
│   │   ├── monitor/
│   │   │   ├── calendar.html # Calendar view for displaying tasks
│   │   │   ├── chart.html    # Visualizes activity data with charts
│   │   │   ├── home.html     # Home page displaying a dashboard
│   │   │   ├── input.html    # Form for inputting daily activity data
│   │   │   └── login.html    # Login page for authentication
│   └── static/               # Static files (CSS, JS, images)
├── requirements.txt         # Lists the Python dependencies for the project
├── staticfiles/              # Collected static files for production
├── TODO.md                   # To-do list for future project improvements
└── user_monitoring/          # Project configuration files
    ├── settings.py           # Django project settings
    ├── urls.py               # URL routing for the project
    └── wsgi.py               # WSGI configuration for deployment
```

## Contributing

We encourage contributions to enhance this project! To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Commit your changes and push them to your fork.
4. Open a pull request with a clear description of your changes.

We appreciate all contributions and feedback!

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
