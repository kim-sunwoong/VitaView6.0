import os.path
import pandas as pd
import tkinter.messagebox as msgbox
import numpy as np
from tkinter import ttk
from tkinter import *
from tkinter import filedialog
from datetime import datetime

lab_staff_name_list = ["sunwoong kim", ""]  # I assume the second name in the list should be an actual name
lab_staff_id_list = ["svk6122", ""]

access_status_user_info = 0


def get_user_info():
    global access_status_user_info
    entered_username = username.get().lower()
    entered_userid = userid.get().lower()

    if len(entered_username) == 0 or len(entered_userid) == 0:
        msgbox.showwarning("User Access", "Please Enter User Information")

        print(entered_username)
        print(entered_userid)
        return
    if (entered_username in lab_staff_name_list) and (entered_userid in lab_staff_id_list):
        msgbox.showinfo("User Access", "Access Accepted")
        access_status_user_info = 1
    else:
        msgbox.showinfo("User Access", "Access Denied")
        access_status_user_info = 0

def add_file():
    files = filedialog.askopenfilenames(title="Please Select CSV File",
                                        filetypes=(("CSV Files", "*.csv"), ("All files", "*.*")),
                                        initialdir="/Users/sunwoongkim/Library/CloudStorage/OneDrive-ThePennsylvaniaStateUniversity/My_Project/doris")  # 미리 파일 저장 위치 정해서 여기에
    for file in files:
        list_file.insert(END, file)


def del_file():
    for index in reversed(
            list_file.curselection()):  # list_file 에서 현재 선택된 파일들 의 index 를 tuple 로 반환/ reversed 한 이유는 첫번째 index를 지워면
        # 이후의 index 순서가 다시 리셋되기 때문, 뒤에서 부터 지움!!!
        list_file.delete(index)
    msgbox.showwarning('Delete', "File Deleted")
    top = Toplevel(root)
    top.geometry("350x150+1200+500")
    top.title("Child Window")
    Label(top, text="You have Deleted the file", font='Mistral 18 bold').place(x=50, y=60)


def generate():
    if access_status_user_info == 0:

        dataframes = {}
        indi_file_name_list = []
        if list_file.size() == 0:
            msgbox.showwarning("Warning", "Please select as least one file")
            return
        if len(drug_name.get()) == 0:
            msgbox.showwarning("Warning", "Name of the file is required")
            return

        exp_folder_selected = filedialog.askdirectory()


        option_file_type = cmb_file_type.get()
        if option_file_type == "Excel":
            option_file_type = 1
        elif option_file_type == "CSV":
            option_file_type = 0

        option_time_bin = cmb_time_bin.get()
        if option_time_bin == "30 second":
            option_time_bin = 2
        elif option_time_bin == "45 second":
            option_time_bin = 3
        elif option_time_bin == "1 minute":
            option_time_bin = 4
        elif option_time_bin == "ALL":
            option_time_bin = 1

        analysis_type = cmb_group.get()
        if analysis_type == 'Group Analysis':
            analysis_type = 0
        elif analysis_type == 'Individual Analysis':
            analysis_type = 1
        # Group
        if analysis_type == 0:
            for i in list_file.get(0, END):
                file_name = i[::-1].split('/', 1)[0][::-1].replace(".csv", "")
                each_files = pd.read_csv(i, na_values=[0, np.NaN], header=[0, 1, 2], parse_dates=[0]).drop(0)   #.fillna(0)
                # each_files.interpolate(method='linear', limit_direction='both', inplace=True) (전체 데이터의 모든 값을 예측)

                time_data_group = each_files.iloc[::option_time_bin, [0]]
                activity_data_group = each_files.iloc[::option_time_bin, 2::2]
                temperature_data_group = each_files.iloc[::option_time_bin, 1::2]

                #activity_data_group.fillna(0, inplace=True)
                #temperature_data_group.interpolate(method='linear', limit_direction='both', inplace=True)

                '''
                예상한 데이터 셀 하이라이트 
                temperature_data_group_original = temperature_data_group.copy()

                yellow_fill = PatternFill(start_color='FFFF00', end_color='FFFF00', fill_type='solid')

                for row in range(2, len(temperature_data_group) + 2):  # openpyxl is 1-indexed, header is row 1
                    if pd.isna(temperature_data_group_original.iloc[row - 2, 0]) and not pd.isna(temperature_data_group.iloc[row - 2, 0]):
                        # Apply yellow fill if the original value was NaN but the current value is not
                        cell = sheet.cell(row=row, column=1)
                        cell.fill = yellow_fill
                '''

                activity_data_group['Average'] = activity_data_group.mean(axis=1)
                temperature_data_group['Average'] = temperature_data_group.mean(axis=1)

                final_data = pd.concat([time_data_group, activity_data_group, temperature_data_group], axis=1)
                final_data = final_data.round(2)

                if option_file_type == 1:
                    excel_file_name = os.path.join(f'{exp_folder_selected}/{file_name}_{drug_name.get()}_G{datetime.now().strftime("%Y%m%d")}.xlsx')
                    final_data.to_excel(excel_file_name, sheet_name=drug_name.get())
                elif option_file_type == 0:
                    csv_file_name = os.path.join(
                        f'{exp_folder_selected}/{file_name}_{drug_name.get()}_G{datetime.now().strftime("%Y%m%d")}.csv')
                    final_data.to_csv(csv_file_name, sheet_name=drug_name.get())
            msgbox.showinfo("", "File Successfully Exported")

        # Individual
        elif analysis_type == 1:
            for i in list_file.get(0, END):
                file_name = i[::-1].split('/', 1)[0][::-1].replace(".csv", "")
                each_selected_file = pd.read_csv(i)
                each_selected_file.rename(columns={'Date/': 'Date'}, inplace=True)
                shape = each_selected_file.shape[1]

                name_list = []
                num_group = 0
                for_column_name = 1
                date_ = 0
                first_group = 1
                second_group = 2
                final_dataset = {}
                # 행 2개씩 묶어서 그룹
                while num_group < (int(shape) - 1) / 2:
                    column_name = (each_selected_file.columns[for_column_name])
                    name_list.append(column_name)
                    slice_df = each_selected_file.iloc[::option_time_bin, [date_, first_group, second_group]]
                    final_dataset[column_name] = slice_df

                    first_group += 2
                    second_group += 2

                    for_column_name += 2
                    num_group += 1
                for key, value in final_dataset.items():
                    df_to_export = pd.DataFrame(value)
                    if option_file_type == 1:
                        excel_file_name = os.path.join(f'{exp_folder_selected}/{file_name}_{key}_{drug_name.get()}_I{datetime.now().strftime("%Y%m%d")}.xlsx')
                        df_to_export.to_excel(excel_file_name, sheet_name=key, index=False)
                    elif option_file_type == 0:
                        csv_file_name = os.path.join(f'{exp_folder_selected}/{file_name}_{key}_{drug_name.get()}_I{datetime.now().strftime("%Y%m%d")}.csv')
                        df_to_export.to_csv(csv_file_name, index=False)
            msgbox.showinfo("", "File Successfully Exported")
    else:
        msgbox.showwarning("", "Please Get Access")
        return

root = Tk()
root.title("STARR Life Sciences Crop. VitaView 6.0 DATA")
root.geometry("+1000+300")
root.resizable(True, True)

# User Information
user_info_frame = LabelFrame(root, text="User Info")
user_info_frame.pack()

lbl_username = Label(master=user_info_frame, text="User Name:", width=10)
lbl_username.pack(side="left")
username = Entry(user_info_frame)
username.pack(side="left", fill="x")
username.insert(0, "")

lbl_userid = Label(user_info_frame, text="User ID:", width=10)
lbl_userid.pack(side="left")
userid = Entry(user_info_frame)
userid.pack(side="left", fill="x")
userid.insert(0, "")

btn3 = Button(user_info_frame, padx=10, pady=5, fg='blue', bg='black', text="Next", command=get_user_info)
btn3.pack(fill="both")

# Read Option
"""
option_frame = LabelFrame(root, text="Read Option")
option_frame.pack(fill="both")

btn_entire_file = Button(option_frame, padx=2, pady=2, width=14, fg='green', bg="black", text="Entire File")
btn_entire_file.pack(side="left", fill="both", expand=True)
btn_indi_file = Button(option_frame, padx=2, pady=2, width=14, fg='purple', bg='yellow', text="Individual File")
btn_indi_file.pack(side="right", fill="both", expand=True)
"""
# Import Files
file_frame = LabelFrame(root, text="File")
file_frame.pack(fill="both")

txt_dest_path = Entry(file_frame)
txt_dest_path.pack(side='left', fill="x", ipady=5, expand=True)

btn_dest_path = Button(file_frame, text="Import", width=10, command=add_file)
btn_dest_path.pack(side="right")

btn_dest_path2 = Button(file_frame, text="Delete", width=10, command=del_file)
btn_dest_path2.pack(side="right")

# You have added
list_frame = LabelFrame(root, text="You have added")
list_frame.pack(fill="both")

scrollbar = Scrollbar(list_frame)
scrollbar.pack(side="right", fill="y")

list_file = Listbox(list_frame, selectmode="extended", height=10, yscrollcommand=scrollbar.set)
list_file.pack(side="left", fill="both", expand=True)
scrollbar.config(command=list_file.yview)

# drug selection
drug_selection_frame = LabelFrame(root, text="Drug Name")
drug_selection_frame.pack(fill="both")

drug_name = Entry(drug_selection_frame)
drug_name.pack(side="left", fill="x", ipady=1, expand=True)
drug_name.insert(0, "")

# Option
option_frame = LabelFrame(root, text="Option")
option_frame.pack(fill="both")

lbl_file_lab = Label(option_frame, text="File Type")
lbl_file_lab.pack(side="left")

file_type_opt = ['Excel', 'CSV']
cmb_file_type = ttk.Combobox(option_frame, state="readonly", values=file_type_opt)
cmb_file_type.current(0)
cmb_file_type.pack(side="left")

lbl_time_lab = Label(option_frame, text="Time bin")
lbl_time_lab.pack(side="left")

time_bin_opt = ['ALL', '30 second', '45 second', '1 minute']
cmb_time_bin = ttk.Combobox(option_frame, state="readonly", values=time_bin_opt)
cmb_time_bin.current(0)
cmb_time_bin.pack(side="left")

lbl_group_lab = Label(option_frame, text="Group")
lbl_group_lab.pack(side="left")

group_opt = ['Group Analysis', 'Individual Analysis']
cmb_group = ttk.Combobox(option_frame, state="readonly", values=group_opt)
cmb_group.current(0)
cmb_group.pack(side="left")

# Export Files
exp_file_frame = LabelFrame(root, text="Export Path", )
exp_file_frame.pack(fill="both")

txt_dest_path_exp = Entry(exp_file_frame)
txt_dest_path_exp.pack(side='left', fill="x", ipady=5, expand=True)

# btn_exp = Button(exp_file_frame, text="Export", command=browse_exp_path)
# btn_exp.pack(side="right")

btn_generate = Button(root, text="Generate", height=2, bg="Blue", command=generate)
btn_generate.pack(fill="both")

root.mainloop()
