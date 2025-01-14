from datetime import datetime
from tkinter import ttk
from web import WebScraper, NumberCounter
import tkinter as tk
import csv

def assign_colour(num: str, sig_nums: list[str], notable_nums: list[str]) -> str:

    if num in sig_nums[:2] or num.replace('0', '') in sig_nums[:2]:
        return 'SpringGreen3'
    elif num in sig_nums[2:] or num.replace('0', '') in sig_nums[2:]:
        return 'gold'
    elif num in notable_nums or num.replace('0', '') in notable_nums:
        return 'lavender'
    else:
        return 'white'

def create_tables():
    team1 = team1_combo.get()
    team2 = team2_combo.get()
    date = datetime.strptime(f'{day_combo.get()} {month_combo.get()} {year_combo.get()}','%d %B %Y')
    ws = WebScraper(date)
    ws.run(team1, team2)
    nc = NumberCounter(date, ws.phrase_results, ws.date_stats)
    ranked_tups = nc.display_nums()
    sig_tups = [tup for tup in ranked_tups if tup[1] > 2]
    sig_nums = [tup[0] for tup in sig_tups]
    notable_nums = [tup[0] for tup in ranked_tups if tup[0] not in sig_nums]

    # Create the date-cipher table
    ## Column Names
    col_names = ['Phrase', 'Ordinal', 'Reduction', 'Reverse' , 'Rev. Red', 'Chaldean']
    for i, col_name in enumerate(col_names):
        cell = tk.Label(cipher_frame, text=col_name, bg='light grey', borderwidth=1, relief="solid", padx=5, pady=5)
        cell.grid(row=0, column=i, sticky='nsew')

    for i, key in enumerate(ws.phrase_dict.keys()):
        cell = tk.Label(cipher_frame, text=key, borderwidth=1, relief="solid", padx=5, pady=5)
        cell.grid(row=i+1, column=0, sticky="nsew")
        for j, num in enumerate(list(ws.phrase_dict.values())[i]):
            # Create a label for each cell
            bg_colour = assign_colour(num, sig_nums, notable_nums)
            cell = tk.Label(cipher_frame, text=num, bg=bg_colour, borderwidth=1, relief="solid", padx=5, pady=5)
            cell.grid(row=i+1, column=j+1, sticky="nsew")

    # Create the date-stats table
    ## Column Names
    col_names = ['Statistic', 'No.1', 'No.2']
    for i, col_name in enumerate(col_names):
        cell = tk.Label(stats_frame, text=col_name, bg='light grey', borderwidth=1, relief="solid", padx=5, pady=5)
        cell.grid(row=0, column=i, sticky='nsew')

    for i, key in enumerate(ws.date_stats.keys()):
        cell = tk.Label(stats_frame, text=key, borderwidth=1, relief="solid", padx=5, pady=5)
        cell.grid(row=i+1, column=0, sticky="nsew")
        for j, num in enumerate(list(ws.date_stats.values())[i]):
            # Create a label for each cell
            bg_colour = assign_colour(num, sig_nums, notable_nums)
            cell = tk.Label(stats_frame, text=num, bg=bg_colour, borderwidth=1, relief="solid", padx=5, pady=5)
            cell.grid(row=i+1, column=j+1, sticky="nsew")

    # Create the ranked table
    ## Column Names
    col_names = ['Number', 'Freq.']
    for i, col_name in enumerate(col_names):
        cell = tk.Label(ranked_frame, text=col_name, bg='light grey', borderwidth=1, relief="solid", padx=5, pady=5)
        cell.grid(row=0, column=i, sticky='nsew')

    for i, row in enumerate(sig_tups):
        for j, value in enumerate(row):
            # Create a label for each cell
            if j < 1:
                bg_colour = assign_colour(value, sig_nums, notable_nums)
            else:
                bg_colour = 'white'
            cell = tk.Label(ranked_frame, text=value, bg=bg_colour, borderwidth=1, relief="solid", padx=5, pady=5)
            cell.grid(row=i+1, column=j, sticky="nsew")
    
def submit():
    create_tables()

if __name__=="__main__":
    window = tk.Tk()
    window.title('Baseball Predictor')
    window.geometry('980x980')

    title_label = ttk.Label(master=window, text='Date', font='Calibri 24 bold')
    title_label.pack()

    input_frame = ttk.Frame(master=window)
    # Days
    days = list(range(1, 32))
    day_combo = ttk.Combobox(input_frame, values=days, width=5)
    day_combo.set("Day")  # Placeholder text
    day_combo.grid(row=0, column=0, padx=10, pady=10)

    # Months
    months = ["January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"]
    month_combo = ttk.Combobox(input_frame, values=months, width=10)
    month_combo.set("Month")  # Placeholder text
    month_combo.grid(row=0, column=1, padx=10, pady=10)

    # Years
    years = list(range(2024, 2051))
    year_combo = ttk.Combobox(input_frame, values=years, width=8)
    year_combo.set("Year")  # Placeholder text
    year_combo.grid(row=0, column=2, padx=10, pady=10)

    # Teams
    teams = []
    with open('teams.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            teams.append(row[0])
    
    team1_combo = ttk.Combobox(input_frame, values=teams, width=12)
    team1_combo.set('Team 1')
    team1_combo.grid(row=1, column=0, padx=10, pady=10)

    vs_label = ttk.Label(input_frame, text='VS', font='Calibri 18 bold')
    vs_label.grid(row=1, column=1, padx=10, pady=10)

    team2_combo = ttk.Combobox(input_frame, values=teams, width=12)
    team2_combo.set('Team 2')
    team2_combo.grid(row=1, column=2, padx=10, pady=10)
    
    input_frame.pack()

    submit_button = ttk.Button(window, text='Submit', command=create_tables)
    submit_button.pack()

    output_frame = ttk.Frame(window)
    
    cipher_frame = ttk.Frame(output_frame)
    stats_frame = ttk.Frame(output_frame)
    cipher_frame.pack(side='left', padx=10)
    stats_frame.pack(side='left', padx=10)

    ranked_frame = ttk.Frame(output_frame)
    ranked_frame.pack(side='left', padx=10)

    output_frame.pack()

    window.mainloop()