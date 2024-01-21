import tkinter as tk
import json


class StudyTracker:
    def __init__(self, master):
        self.master = master
        master.title("Study Tracker")

        self.courses = ["Physics", "Programming", "Math", "Engineering", "Other"]
        self.weeks = list(range(1, 15))
        self.study_hours = self.load_data()  # Load data from file

        # Variable to store checkbox state
        self.show_all_weeks_var = tk.BooleanVar(self.master)
        self.show_all_weeks_var.set(False)

        self.create_widgets()

    def create_widgets(self):
        # Labels
        tk.Label(self.master, text="Study Tracker").grid(row=0, column=1, pady=10)
        tk.Label(self.master, text="Select Course:").grid(row=1, column=0, padx=10)
        tk.Label(self.master, text="Hours Studied:").grid(row=2, column=0, padx=10)
        tk.Label(self.master, text="Select Week:").grid(row=3, column=0, padx=10)

        # Dropdown menu for courses
        self.course_var = tk.StringVar(self.master)
        self.course_var.set(self.courses[0])  # default value
        self.course_dropdown = tk.OptionMenu(self.master, self.course_var, *self.courses)
        self.course_dropdown.grid(row=1, column=1, pady=10)

        # Entry for hours studied
        self.hours_entry = tk.Entry(self.master)
        self.hours_entry.grid(row=2, column=1, pady=10)

        # Dropdown menu for weeks
        self.week_var = tk.IntVar(self.master)
        self.week_var.set(self.weeks[0])  # default value
        self.week_dropdown = tk.OptionMenu(self.master, self.week_var, *self.weeks, command=self.update_display)
        self.week_dropdown.grid(row=3, column=1, pady=10)

        # Checkbox to show all weeks
        tk.Checkbutton(self.master, text="Show All Weeks", variable=self.show_all_weeks_var,
                       command=self.update_display).grid(row=4, column=1, pady=5)

        # Button to add hours
        tk.Button(self.master, text="Add Hours", command=self.add_hours).grid(row=5, column=1, pady=10)

        # Total hours label
        self.total_label = tk.Label(self.master, text="Total Hours: 0")
        self.total_label.grid(row=6, column=1, pady=10)

        # Individual hours labels
        self.individual_labels = {}
        for i, course in enumerate(self.courses):
            label = tk.Label(self.master, text=f"{course} Hours: 0")
            label.grid(row=i + 7, column=1, pady=5)
            self.individual_labels[course] = label

        # Grid for weekly hours
        tk.Label(self.master, text="Weekly Hours").grid(row=1, column=2, pady=10, sticky="nsew")
        self.week_labels = {}
        for i, week in enumerate(self.weeks):
            label = tk.Label(self.master, text=f"Week {week}", bd=1, relief=tk.SOLID)
            label.grid(row=2, column=i + 2, pady=5, sticky="nsew")
            self.week_labels[week] = label
            for j, course in enumerate(self.courses):
                label = tk.Label(self.master, text=f"{course}: 0", bd=1, relief=tk.SOLID)
                label.grid(row=j + 3, column=i + 2, pady=5, padx=5, sticky="nsew")
                self.individual_labels[(course, week)] = label

            # Label for total hours in the week
            total_label = tk.Label(self.master, text="Total: 0", bd=1, relief=tk.SOLID)
            total_label.grid(row=len(self.courses) + 3, column=i + 2, pady=5, padx=5, sticky="nsew")
            self.individual_labels[("Total", week)] = total_label

        # Set row and column weights to make the grid expandable
        for i in range(2, 18):
            self.master.grid_rowconfigure(i, weight=1)
        for i in range(2, 16):
            self.master.grid_columnconfigure(i, weight=1)

        # Exit and Save button
        tk.Button(self.master, text="Exit and Save", command=self.exit_and_save).grid(row=len(self.courses) + 8,
                                                                                      column=1, pady=10)

        # Update the display based on the selected week and checkbox state
        self.update_display()

    def add_hours(self):
        selected_course = self.course_var.get()
        selected_week = self.week_var.get()

        # Ensure the selected course and week exist in the dictionary
        if selected_course not in self.study_hours:
            self.study_hours[selected_course] = {}
        if selected_week not in self.study_hours[selected_course]:
            self.study_hours[selected_course][selected_week] = 0

        try:
            hours = float(self.hours_entry.get())
            self.study_hours[selected_course][selected_week] += hours  # Update by adding to the existing value
            self.update_individual_label(selected_course)
            self.update_weekly_label(selected_week)
            self.update_total_label(selected_week)
            self.save_data()  # Save data to file
        except ValueError:
            print("Please enter a valid number for hours.")

    def update_individual_label(self, course):
        self.individual_labels[course].config(text=f"{course} Hours: {sum(self.study_hours[course].values())}")

    def update_weekly_label(self, week):
        for course in self.courses:
            if week in self.study_hours.get(course, {}):
                label = self.individual_labels.get((course, week))
                label.config(text=f"{course}: {self.study_hours[course][week]}")

        # Update total hours for the week
        total_label = self.individual_labels.get(("Total", week))
        total_hours = sum(
            self.study_hours[course][week] for course in self.courses if week in self.study_hours.get(course, {}))
        total_label.config(text=f"Total: {total_hours}")

    def update_total_label(self, selected_week):
        total_hours = sum(sum(week.values()) for week in self.study_hours.values() if selected_week in week)
        self.total_label.config(text=f"Total Hours: {total_hours}")

    def update_display(self, *args):
        selected_week = self.week_var.get()
        show_all_weeks = self.show_all_weeks_var.get()

        for week in self.weeks:
            label = self.week_labels.get(week)
            if show_all_weeks or week == selected_week:
                label.grid()
            else:
                label.grid_remove()

            for course in self.courses:
                label = self.individual_labels.get((course, week))
                if show_all_weeks or week == selected_week:
                    label.grid()
                else:
                    label.grid_remove()

            # Show or hide the total column for the week
            total_label = self.individual_labels.get(("Total", week))
            if show_all_weeks or week == selected_week:
                total_label.grid()
            else:
                total_label.grid_remove()

    def save_data(self):
        with open("study_data.json", "w") as file:
            json.dump(self.study_hours, file)

    def load_data(self):
        try:
            with open("study_data.json", "r") as file:
                data = json.load(file)

                # Ensure all courses and weeks are present with default values
                for course in self.courses:
                    data.setdefault(course, {})
                    for week in self.weeks:
                        data[course].setdefault(week, 0)

                return data
        except (FileNotFoundError, json.JSONDecodeError):
            # If file not found or decoding error, return empty data
            return {course: {week: 0 for week in self.weeks} for course in self.courses}

    def exit_and_save(self):
        self.save_data()
        self.master.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = StudyTracker(root)
    root.mainloop()
