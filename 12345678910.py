import serial
import serial.tools.list_ports
import time
import tkinter as tk
from tkinter import messagebox, ttk

# ==========================================
# متغيرات عامة
# ==========================================
ser = None
current_x = 0
current_y = 0
prev_x = 0
prev_y = 0
has_point = False
is_connected = False
BAUD_RATE = 9600


def get_available_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]


def update_ports_list(event=None):
    ports = get_available_ports()
    combo_ports['values'] = ports
    if ports:
        if not combo_ports.get() or combo_ports.get() not in ports:
            combo_ports.current(0)
    else:
        combo_ports.set('')


def toggle_connection():
    global ser, is_connected

    if is_connected:
        if ser and ser.is_open:
            ser.close()
        is_connected = False
        btn_connect.config(
            text='اتصال 🔌', bg='#2980B9', activebackground='#1B4F72'
        )
        lbl_status.config(text='الحالة: غير متصل', fg='#7F8C8D')
        update_controls_state()
        messagebox.showinfo('اتصال', 'تم قطع الاتصال بالمنفذ.')
        return

    selected_port = combo_ports.get()
    if not selected_port:
        messagebox.showwarning('تنبيه', 'يرجى اختيار منفذ الأردوينو.')
        return

    try:
        ser = serial.Serial(selected_port, BAUD_RATE, timeout=1)
        time.sleep(2)
        is_connected = True
        btn_connect.config(
            text='قطع الاتصال ❌', bg='#C0392B', activebackground='#922B21'
        )
        lbl_status.config(
            text=f'الحالة: متصل ({selected_port})', fg='#27AE60'
        )
        update_controls_state()
        messagebox.showinfo('نجاح', f'تم الاتصال بالمنفذ {selected_port}!')

    except Exception as e:
        is_connected = False
        lbl_status.config(text='الحالة: تعذر الاتصال', fg='#C0392B')
        update_controls_state()
        messagebox.showerror('خطأ اتصال', f'تعذر الاتصال:\n{e}')


def update_controls_state():
    state = 'normal' if is_connected else 'disabled'
    btn_send.config(state=state if validate_inputs() else 'disabled')
    btn_reset.config(state=state)
    btn_clear.config(state=state)
    btn_estop.config(state=state)


# ==========================================
# التحقق من المدخلات (النطاق من -10 إلى +10)
# ==========================================
def validate_inputs(*args):
    x_str = entry_x.get().strip()
    y_str = entry_y.get().strip()

    valid_x = True
    valid_y = True

    if x_str and x_str != '-':
        try:
            x_val = int(x_str)
            if not (-10 <= x_val <= 10):
                valid_x = False
        except ValueError:
            valid_x = False

    if y_str and y_str != '-':
        try:
            y_val = int(y_str)
            if not (-10 <= y_val <= 10):
                valid_y = False
        except ValueError:
            valid_y = False

    lbl_error_x.config(text='⚠️ خارج النطاق!' if not valid_x else '')
    lbl_error_y.config(text='⚠️ خارج النطاق!' if not valid_y else '')

    is_valid = (
        valid_x
        and valid_y
        and bool(x_str)
        and bool(y_str)
        and x_str != '-'
        and y_str != '-'
    )

    if is_connected:
        btn_send.config(state='normal' if is_valid else 'disabled')

    return is_valid


# ==========================================
# رسم المستوى الإحداثي (من -10 إلى +10)
# ==========================================
def draw_coordinate_system():
    canvas_grid.delete('all')

    w = canvas_grid.winfo_width()
    h = canvas_grid.winfo_height()

    if w < 100 or h < 100:
        return

    size = min(w, h) - 40
    center_x = w / 2
    center_y = h / 2

    scale = size / 20.0  # تقسيم المسافة على 20 وحدة (-10 إلى +10)

    min_x = center_x - 10 * scale
    max_x = center_x + 10 * scale
    min_y = center_y - 10 * scale
    max_y = center_y + 10 * scale

    canvas_grid.create_rectangle(
        min_x, min_y, max_x, max_y, outline='#BDC3C7', width=2
    )

    # رسم الشبكة لـ 10 أرقام في كل اتجاه
    for i in range(-10, 11):
        px = center_x + i * scale
        py = center_y - i * scale
        canvas_grid.create_line(px, min_y, px, max_y, fill='#E5E5E5')
        canvas_grid.create_line(min_x, py, max_x, py, fill='#E5E5E5')

    # المحاور الرئيسية
    canvas_grid.create_line(
        min_x, center_y, max_x, center_y, fill='#2C3E50', width=2
    )
    canvas_grid.create_line(
        center_x, max_y, center_x, min_y, fill='#2C3E50', width=2
    )

    # أسماء وأرقام المحاور من -10 إلى 10
    canvas_grid.create_text(
        max_x + 15,
        center_y,
        text='X',
        font=('Segoe UI', 11, 'bold'),
        fill='#2C3E50',
    )
    canvas_grid.create_text(
        center_x,
        min_y - 15,
        text='Y',
        font=('Segoe UI', 11, 'bold'),
        fill='#2C3E50',
    )

    for i in range(-10, 11):
        if i == 0:
            continue
        px = center_x + i * scale
        py = center_y - i * scale
        canvas_grid.create_text(
            px,
            center_y + 15,
            text=str(i),
            font=('Segoe UI', 8),
            fill='#34495E',
        )
        canvas_grid.create_text(
            center_x - 15,
            py,
            text=str(i),
            font=('Segoe UI', 8),
            fill='#34495E',
        )

    # رسم النقطة ومسار الحركة
    if has_point:
        curr_px = center_x + current_x * scale
        curr_py = center_y - current_y * scale

        if prev_x != current_x or prev_y != current_y:
            prev_px = center_x + prev_x * scale
            prev_py = center_y - prev_y * scale
            canvas_grid.create_line(
                prev_px,
                prev_py,
                curr_px,
                curr_py,
                fill='#2980B9',
                width=2,
                dash=(4, 4),
            )

        canvas_grid.create_oval(
            curr_px - 7,
            curr_py - 7,
            curr_px + 7,
            curr_py + 7,
            fill='#E74C3C',
            outline='#C0392B',
            width=2,
        )
        canvas_grid.create_text(
            curr_px + 35,
            curr_py - 15,
            text=f'({current_x}, {current_y})',
            font=('Segoe UI', 10, 'bold'),
            fill='#C0392B',
        )


def on_canvas_click(event):
    if not is_connected:
        return

    w = canvas_grid.winfo_width()
    h = canvas_grid.winfo_height()
    size = min(w, h) - 40
    center_x = w / 2
    center_y = h / 2
    scale = size / 20.0

    calc_x = (event.x - center_x) / scale
    calc_y = (center_y - event.y) / scale

    if -10 <= calc_x <= 10 and -10 <= calc_y <= 10:
        target_x = int(round(calc_x))
        target_y = int(round(calc_y))

        entry_x.delete(0, tk.END)
        entry_y.delete(0, tk.END)
        entry_x.insert(0, str(target_x))
        entry_y.insert(0, str(target_y))

        execute_move(target_x, target_y)


def execute_move(x, y):
    global current_x, current_y, prev_x, prev_y, has_point

    prev_x = current_x
    prev_y = current_y

    current_x = int(x)
    current_y = int(y)
    has_point = True

    draw_coordinate_system()

    lbl_position.config(
        text=f'الموقع الحالي: X = {current_x}    Y = {current_y}'
    )

    if ser and ser.is_open:
        try:
            message = f'X{current_x},Y{current_y}\n'
            ser.write(message.encode('utf-8'))
        except Exception as e:
            messagebox.showerror('خطأ', f'حدث خطأ أثناء الإرسال:\n{e}')


def send_coordinates():
    try:
        x = int(float(entry_x.get().strip()))
        y = int(float(entry_y.get().strip()))
        execute_move(x, y)
    except ValueError:
        pass


def emergency_stop():
    if ser and ser.is_open:
        try:
            ser.write(b'ESTOP\n')
            messagebox.showwarning('🚨 طوارئ', 'تم إرسال أمر إيقاف الطوارئ!')
        except Exception as e:
            messagebox.showerror('خطأ', f'تعذر إرسال أمر الطوارئ:\n{e}')


def reset_coordinates():
    """زر إعادة المحرك يدوياً إلى نقطة الصفر (0,0)"""
    entry_x.delete(0, tk.END)
    entry_y.delete(0, tk.END)
    entry_x.insert(0, '0')
    entry_y.insert(0, '0')
    execute_move(0, 0)


def clear_coordinate():
    global current_x, current_y, prev_x, prev_y, has_point
    entry_x.delete(0, tk.END)
    entry_y.delete(0, tk.END)
    current_x = prev_x = 0
    current_y = prev_y = 0
    has_point = False
    draw_coordinate_system()
    lbl_position.config(text='الموقع الحالي: (0,0)')


def on_canvas_resize(event=None):
    draw_coordinate_system()


def on_closing():
    global ser
    if ser and ser.is_open:
        ser.close()
    root.destroy()


# ==========================================
# الواجهة الرئيسية
# ==========================================
root = tk.Tk()
root.title('لوحة التحكم - النطاق (-10 إلى +10)')
root.geometry('1100x650')
root.configure(bg='#2C3E50')
root.resizable(True, True)

root.protocol('WM_DELETE_WINDOW', on_closing)

header = tk.Label(
    root,
    text='لوحة التحكم - المستوى الإحداثي (من -10 إلى +10)',
    font=('Segoe UI', 18, 'bold'),
    bg='#2C3E50',
    fg='#ECF0F1',
)
header.pack(side='top', fill='x', pady=(15, 5))

content_frame = tk.Frame(root, bg='#2C3E50')
content_frame.pack(expand=True, fill='both', padx=15, pady=10)

left_frame = tk.Frame(content_frame, bg='#ECF0F1', bd=2, relief='groove')
left_frame.pack(side='left', expand=True, fill='both', padx=(0, 10))

lbl_plot_title = tk.Label(
    left_frame,
    text='المستوى الإحداثي (انقر لاختيار الزوج المرتب 🖱️)',
    font=('Segoe UI', 11, 'bold'),
    bg='#ECF0F1',
    fg='#2C3E50',
)
lbl_plot_title.pack(anchor='n', pady=8)

canvas_grid = tk.Canvas(
    left_frame,
    bg='white',
    highlightthickness=1,
    highlightbackground='#BDC3C7',
    cursor='crosshair',
)
canvas_grid.pack(expand=True, fill='both', padx=15, pady=(0, 5))
canvas_grid.bind('<Button-1>', on_canvas_click)

lbl_position = tk.Label(
    left_frame,
    text='الموقع الحالي: X = 0    Y = 0',
    font=('Segoe UI', 10, 'bold'),
    bg='#ECF0F1',
    fg='#2C3E50',
)
lbl_position.pack(pady=(0, 8))

right_frame = tk.Frame(
    content_frame, bg='#ECF0F1', width=440, padx=15, pady=15, bd=2, relief='groove'
)
right_frame.pack(side='right', fill='y', padx=(5, 0))
right_frame.pack_propagate(False)

lbl_ctrl_title = tk.Label(
    right_frame,
    text='إعدادات التحكم والاتصال',
    font=('Segoe UI', 12, 'bold'),
    bg='#ECF0F1',
    fg='#2C3E50',
)
lbl_ctrl_title.grid(row=0, column=0, columnspan=3, pady=(0, 10))

lbl_port = tk.Label(
    right_frame,
    text='المنفذ:',
    font=('Segoe UI', 10, 'bold'),
    bg='#ECF0F1',
    fg='#34495E',
)
lbl_port.grid(row=1, column=2, padx=2, pady=5, sticky='e')

combo_ports = ttk.Combobox(
    right_frame, width=14, font=('Segoe UI', 9), state='readonly'
)
combo_ports.grid(row=1, column=0, columnspan=2, padx=2, pady=5)
combo_ports.bind('<Button-1>', update_ports_list)

btn_connect = tk.Button(
    right_frame,
    text='اتصال 🔌',
    font=('Segoe UI', 10, 'bold'),
    bg='#2980B9',
    fg='white',
    activebackground='#1B4F72',
    relief='flat',
    cursor='hand2',
    width=18,
    command=toggle_connection,
)
btn_connect.grid(row=2, column=0, columnspan=3, pady=(8, 2))

lbl_status = tk.Label(
    right_frame,
    text='الحالة: غير متصل',
    font=('Segoe UI', 9, 'bold'),
    bg='#ECF0F1',
    fg='#7F8C8D',
)
lbl_status.grid(row=3, column=0, columnspan=3, pady=(0, 15))

var_x = tk.StringVar()
var_y = tk.StringVar()
var_x.trace_add('write', validate_inputs)
var_y.trace_add('write', validate_inputs)

label_x = tk.Label(
    right_frame,
    text='قيمة X:',
    font=('Segoe UI', 10, 'bold'),
    bg='#ECF0F1',
    fg='#34495E',
)
label_x.grid(row=4, column=2, padx=2, pady=5, sticky='e')

entry_x = tk.Entry(
    right_frame,
    textvariable=var_x,
    width=8,
    font=('Segoe UI', 10),
    bd=2,
    relief='groove',
    justify='center',
)
entry_x.grid(row=4, column=1, padx=2, pady=5)

lbl_error_x = tk.Label(
    right_frame, text='', font=('Segoe UI', 8, 'bold'), bg='#ECF0F1', fg='#C0392B'
)
lbl_error_x.grid(row=4, column=0, padx=2, pady=5, sticky='w')

label_y = tk.Label(
    right_frame,
    text='قيمة Y:',
    font=('Segoe UI', 10, 'bold'),
    bg='#ECF0F1',
    fg='#34495E',
)
label_y.grid(row=5, column=2, padx=2, pady=5, sticky='e')

entry_y = tk.Entry(
    right_frame,
    textvariable=var_y,
    width=8,
    font=('Segoe UI', 10),
    bd=2,
    relief='groove',
    justify='center',
)
entry_y.grid(row=5, column=1, padx=2, pady=5)

lbl_error_y = tk.Label(
    right_frame, text='', font=('Segoe UI', 8, 'bold'), bg='#ECF0F1', fg='#C0392B'
)
lbl_error_y.grid(row=5, column=0, padx=2, pady=5, sticky='w')

btn_send = tk.Button(
    right_frame,
    text='إرسال الإحداثيات 🚀',
    font=('Segoe UI', 10, 'bold'),
    bg='#27AE60',
    fg='white',
    activebackground='#219150',
    relief='flat',
    cursor='hand2',
    width=18,
    command=send_coordinates,
)
btn_send.grid(row=6, column=0, columnspan=3, pady=(15, 4))

btn_reset = tk.Button(
    right_frame,
    text='العودة للصفر ↺',
    font=('Segoe UI', 9, 'bold'),
    bg='#F39C12',
    fg='white',
    activebackground='#D68910',
    relief='flat',
    cursor='hand2',
    width=18,
    command=reset_coordinates,
)
btn_reset.grid(row=7, column=0, columnspan=3, pady=3)

btn_clear = tk.Button(
    right_frame,
    text='مسح التحديد 🗑',
    font=('Segoe UI', 9, 'bold'),
    bg='#7F8C8D',
    fg='white',
    activebackground='#626567',
    relief='flat',
    cursor='hand2',
    width=18,
    command=clear_coordinate,
)
btn_clear.grid(row=8, column=0, columnspan=3, pady=3)

btn_estop = tk.Button(
    right_frame,
    text='🛑 إيقاف طوارئ (E-STOP)',
    font=('Segoe UI', 10, 'bold'),
    bg='#C0392B',
    fg='white',
    activebackground='#922B21',
    relief='flat',
    cursor='hand2',
    width=20,
    command=emergency_stop,
)
btn_estop.grid(row=9, column=0, columnspan=3, pady=(20, 0))

update_ports_list()
update_controls_state()
canvas_grid.bind('<Configure>', on_canvas_resize)

root.mainloop()
