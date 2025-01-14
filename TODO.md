1. Confirmation Box while deleting the task in the TODO task



const renderCalendar = async () => {
            calendarGrid.innerHTML = ''; // Clear the calendar grid

            // Getting current year and month 
            const year = currentDate.getFullYear();
            const month = currentDate.getMonth();

            // Setting Month and Year Text 
            monthYear.textContent = ${currentDate.toLocaleString('default', { month: 'long' })} ${year};

            // Calculating the First Day and Total Days in the month
            const firstDay = new Date(Date.UTC(year, month, 1)).getUTCDay(); // First day of the month in UTC
            const daysInMonth = new Date(Date.UTC(year, month + 1, 0)).getUTCDate(); // Total days in the month (UTC)

            const today = new Date(); // Today's date

            // Fetch tasks for the current month
            let monthTasks = [];
            try {
                const response = await fetch(/api/calendar-tasks/?month=${month + 1}&year=${year});
                if (!response.ok) throw new Error('Failed to fetch tasks');
                monthTasks = await response.json(); // Store tasks for the month
            } catch (error) {
                console.error('Error fetching tasks:', error);
            }

            // Add empty cells for days before the 1st of the month
            for (let i = 0; i < firstDay; i++) {
                const emptyCell = document.createElement('div');
                emptyCell.classList.add('calendar-cell', 'inactive');
                calendarGrid.appendChild(emptyCell);
            }

            // Add cells for each day of the month
            for (let day = 1; day <= daysInMonth; day++) {
                const dayCell = document.createElement('div');
                dayCell.classList.add('calendar-cell'); // Add CSS class for the cell
                dayCell.textContent = day; // Set the cell's text to the current day number

                // Highlight today's date
                if (
                    day === today.getDate() &&
                    month === today.getMonth() &&
                    year === today.getFullYear()
                ) {
                    dayCell.classList.add('today');
                }

                // Get the current date in 'YYYY-MM-DD' format
                const currentDay = ${year}-${(month + 1).toString().padStart(2, '0')}-${day.toString().padStart(2, '0')};

                // Filter tasks for the current date
                const tasks = monthTasks.filter(task => task.date === currentDay);

                // If tasks exist for the day, add indicators to the cell
                if (tasks.length > 0) {
                    const indicator = document.createElement('div');
                    indicator.classList.add('task-indicator');
                    let hasNormalTask = false;
                    let hasDayTask = false;

                    // Check for task types
                    tasks.forEach(task => {
                        if (task.task_type === 'normal') hasNormalTask = true;
                        if (task.task_type === 'day') hasDayTask = true;
                    });

                    // Add normal task indicator
                    if (hasNormalTask) {
                        const normalDot = document.createElement('span');
                        normalDot.classList.add('normal');
                        indicator.appendChild(normalDot);
                        dayCell.classList.add('task-day-normal');
                    }

                    // Add day task indicator
                    if (hasDayTask) {
                        const dayDot = document.createElement('span');
                        dayDot.classList.add('day');
                        indicator.appendChild(dayDot);
                        dayCell.classList.add('task-day-day');
                    }

                    dayCell.appendChild(indicator);
                }

                // Open modal on clicking a day
                dayCell.addEventListener('click', () => openModal(day));
                calendarGrid.appendChild(dayCell);
            }
        };
