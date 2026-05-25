import calendar
import math
import tkinter as tk
from datetime import datetime, timedelta


class Countdown:
    DEFAULT_SECONDS = 25 * 60
    BG = '#111827'
    PANEL = '#1f2937'
    PANEL_LIGHT = '#374151'
    TEXT = '#f9fafb'
    MUTED = '#9ca3af'
    ACCENT = '#22c55e'
    DANGER = '#ef4444'

    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.94)
        self.root.configure(bg=self.BG)
        self.root.geometry('+100+100')

        self.seconds = self.DEFAULT_SECONDS
        self.countdown_mode = 'duration'
        self.target_datetime = None
        self.running = False
        self.after_id = None
        self._x = 0
        self._y = 0

        self.shell = tk.Frame(
            self.root,
            bg=self.BG,
            highlightbackground=self.PANEL_LIGHT,
            highlightthickness=1,
        )
        self.shell.pack(fill='both', expand=True)

        self.header = tk.Frame(self.shell, bg=self.BG)
        self.header.pack(fill='x', padx=14, pady=(10, 0))

        self.title = tk.Label(
            self.header,
            text='Countdown',
            font=('Segoe UI', 10, 'bold'),
            fg=self.MUTED,
            bg=self.BG,
        )
        self.title.pack(side='left')

        self.mode_label = tk.Label(
            self.header,
            text='Duration',
            font=('Segoe UI', 9),
            fg=self.ACCENT,
            bg=self.BG,
        )
        self.mode_label.pack(side='left', padx=(8, 0))

        self.close_btn = self.make_button(
            self.header,
            'x',
            self.root.destroy,
            width=3,
            bg=self.BG,
            fg=self.MUTED,
        )
        self.close_btn.pack(side='right')

        self.label = tk.Label(
            self.shell,
            text=self.fmt(),
            font=('Consolas', 34, 'bold'),
            fg=self.TEXT,
            bg=self.BG,
            padx=16,
        )
        self.label.pack(pady=(4, 8))

        self.controls = tk.Frame(self.shell, bg=self.BG)
        self.controls.pack(padx=14, pady=(0, 14))

        self.minus_btn = self.make_button(
            self.controls,
            '-1m',
            lambda: self.adjust(-60),
            width=5,
        )
        self.minus_btn.pack(side='left', padx=3)

        self.btn = self.make_button(
            self.controls,
            'Start',
            self.start_pause,
            width=7,
            bg=self.ACCENT,
            fg='#052e16',
            active_bg='#16a34a',
        )
        self.btn.pack(side='left', padx=3)

        self.plus_btn = self.make_button(
            self.controls,
            '+1m',
            lambda: self.adjust(60),
            width=5,
        )
        self.plus_btn.pack(side='left', padx=3)

        self.reset_btn = self.make_button(self.controls, 'Reset', self.reset, width=6)
        self.reset_btn.pack(side='left', padx=3)

        self.settings_btn = self.make_button(
            self.controls,
            'Set',
            self.open_settings,
            width=5,
        )
        self.settings_btn.pack(side='left', padx=3)

        for widget in (self.shell, self.header, self.title, self.mode_label, self.label):
            widget.bind('<ButtonPress-1>', self.drag_start)
            widget.bind('<B1-Motion>', self.drag_move)

        self.root.bind('<Button-3>', lambda event: self.root.destroy())
        self.root.mainloop()

    def make_button(
        self,
        parent,
        text,
        command,
        width=6,
        bg=None,
        fg=None,
        active_bg=None,
    ):
        bg = bg or self.PANEL
        fg = fg or self.TEXT
        active_bg = active_bg or self.PANEL_LIGHT
        return tk.Button(
            parent,
            text=text,
            width=width,
            command=command,
            relief='flat',
            bd=0,
            bg=bg,
            fg=fg,
            activebackground=active_bg,
            activeforeground=fg,
            cursor='hand2',
            font=('Segoe UI', 9, 'bold'),
            padx=6,
            pady=4,
        )

    def fmt(self):
        if self.countdown_mode == 'deadline' and self.target_datetime is not None:
            years, months, days, hours, minutes, seconds = self.deadline_parts()
            return f'{years}y {months}mo {days}d {hours:02d}:{minutes:02d}:{seconds:02d}'

        if self.seconds < 3600:
            minutes, seconds = divmod(self.seconds, 60)
            return f'{minutes:02d}:{seconds:02d}'

        hours = self.seconds // 3600
        minutes, seconds = divmod(self.seconds % 3600, 60)
        return f'{hours}:{minutes:02d}:{seconds:02d}'

    def deadline_parts(self):
        now = datetime.now()
        target = self.target_datetime
        if target is None or target <= now:
            self.seconds = 0
            return 0, 0, 0, 0, 0, 0

        self.seconds = max(0, math.ceil((target - now).total_seconds()))
        total_months = (target.year - now.year) * 12 + target.month - now.month

        if self.add_months(now, total_months) > target:
            total_months -= 1

        anchor = self.add_months(now, total_months)
        years, months = divmod(total_months, 12)
        remainder = target - anchor
        days = remainder.days
        hours, rem = divmod(remainder.seconds, 3600)
        minutes, seconds = divmod(rem, 60)
        return years, months, days, hours, minutes, seconds

    def add_months(self, value, months):
        month_index = value.month - 1 + months
        year = value.year + month_index // 12
        month = month_index % 12 + 1
        day = min(value.day, calendar.monthrange(year, month)[1])
        return value.replace(year=year, month=month, day=day)

    def stop_and_set(self, total_seconds, mode='duration', target=None):
        self.running = False
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        self.countdown_mode = mode
        self.target_datetime = target
        self.seconds = max(0, total_seconds)
        self.mode_label.config(text='Deadline' if mode == 'deadline' else 'Duration')
        self.label.config(text=self.fmt(), fg=self.TEXT)
        self.btn.config(text='Start')

    def update(self):
        if not self.running:
            return

        if self.countdown_mode == 'duration':
            self.seconds = max(0, self.seconds - 1)
        elif self.target_datetime is not None:
            self.seconds = max(
                0,
                math.ceil((self.target_datetime - datetime.now()).total_seconds()),
            )

        self.label.config(text=self.fmt())

        if self.seconds > 0:
            self.after_id = self.root.after(1000, self.update)
        else:
            self.finish()

    def finish(self):
        self.running = False
        self.after_id = None
        self.btn.config(text='Start')
        self.label.config(fg=self.DANGER)
        self.root.after(2000, lambda: self.label.config(fg=self.TEXT))

    def start_pause(self):
        if not self.running:
            if self.countdown_mode == 'deadline' and self.target_datetime is not None:
                self.seconds = max(
                    0,
                    math.ceil((self.target_datetime - datetime.now()).total_seconds()),
                )

            if self.seconds > 0:
                self.running = True
                self.btn.config(text='Pause')
                self.label.config(text=self.fmt(), fg=self.TEXT)
                self.after_id = self.root.after(1000, self.update)
        else:
            self.running = False
            if self.after_id:
                self.root.after_cancel(self.after_id)
                self.after_id = None
            self.btn.config(text='Start')

    def adjust(self, delta):
        if not self.running and self.countdown_mode == 'duration':
            self.seconds = max(0, self.seconds + delta)
            self.label.config(text=self.fmt())

    def reset(self):
        self.stop_and_set(self.DEFAULT_SECONDS)

    def open_settings(self):
        win = tk.Toplevel(self.root)
        win.title('Set Countdown')
        win.resizable(False, False)
        win.attributes('-topmost', True)
        win.configure(bg=self.BG)

        content = tk.Frame(
            win,
            bg=self.BG,
            padx=16,
            pady=14,
            highlightbackground=self.PANEL_LIGHT,
            highlightthickness=1,
        )
        content.pack(fill='both', expand=True)

        tk.Label(
            content,
            text='Set Countdown',
            font=('Segoe UI', 12, 'bold'),
            fg=self.TEXT,
            bg=self.BG,
        ).pack(anchor='w')

        mode = tk.StringVar(value=self.countdown_mode)
        mode_frame = tk.Frame(content, bg=self.BG)
        mode_frame.pack(pady=(10, 8), anchor='w')

        for text, value in (
            ('Duration', 'duration'),
            ('Deadline', 'deadline'),
        ):
            tk.Radiobutton(
                mode_frame,
                text=text,
                variable=mode,
                value=value,
                bg=self.BG,
                fg=self.TEXT,
                selectcolor=self.PANEL,
                activebackground=self.BG,
                activeforeground=self.TEXT,
                font=('Segoe UI', 9),
            ).pack(side='left', padx=(0, 12))

        dur_frame = tk.Frame(content, bg=self.BG)
        hour_var = tk.StringVar(value='0')
        min_var = tk.StringVar(value='25')
        sec_var = tk.StringVar(value='0')
        self.add_field_row(
            dur_frame,
            (
                ('Hours', hour_var, 4),
                ('Minutes', min_var, 4),
                ('Seconds', sec_var, 4),
            ),
        )

        dl_frame = tk.Frame(content, bg=self.BG)
        now = datetime.now() + timedelta(hours=1)
        defaults = {
            'year': now.year,
            'month': now.month,
            'day': now.day,
            'hour': now.hour,
            'minute': now.minute,
            'second': now.second,
        }
        entries = {}
        deadline_fields = []
        for key, label, width in (
            ('year', 'Year', 6),
            ('month', 'Month', 4),
            ('day', 'Day', 4),
            ('hour', 'Hour', 4),
            ('minute', 'Minute', 4),
            ('second', 'Second', 4),
        ):
            var = tk.StringVar(value=str(defaults[key]))
            entries[key] = var
            deadline_fields.append((label, var, width))
        self.add_field_row(dl_frame, deadline_fields)

        message = tk.Label(
            content,
            text='',
            fg=self.DANGER,
            bg=self.BG,
            font=('Segoe UI', 9),
        )
        message.pack(anchor='w', pady=(6, 0))

        button_frame = tk.Frame(content, bg=self.BG)
        button_frame.pack(fill='x', pady=(10, 0))

        def confirm():
            try:
                if mode.get() == 'duration':
                    hours = self.read_int(hour_var, 'Hours', minimum=0)
                    minutes = self.read_int(min_var, 'Minutes', minimum=0)
                    seconds = self.read_int(sec_var, 'Seconds', minimum=0)
                    total = hours * 3600 + minutes * 60 + seconds
                    if total <= 0:
                        raise ValueError('Duration must be greater than zero.')
                    self.stop_and_set(total)
                else:
                    year = self.read_int(entries['year'], 'Year', minimum=1)
                    month = self.read_int(entries['month'], 'Month', 1, 12)
                    day = self.read_int(entries['day'], 'Day', 1, 31)
                    hour = self.read_int(entries['hour'], 'Hour', 0, 23)
                    minute = self.read_int(entries['minute'], 'Minute', 0, 59)
                    second = self.read_int(entries['second'], 'Second', 0, 59)
                    target = datetime(year, month, day, hour, minute, second)
                    total = max(0, math.ceil((target - datetime.now()).total_seconds()))
                    if total <= 0:
                        raise ValueError('Deadline must be in the future.')
                    self.stop_and_set(total, mode='deadline', target=target)
                win.destroy()
            except ValueError as error:
                message.config(text=str(error))

        self.make_button(
            button_frame,
            'Cancel',
            win.destroy,
            width=8,
            bg=self.PANEL,
        ).pack(side='right', padx=(6, 0))

        self.make_button(
            button_frame,
            'Apply',
            confirm,
            width=8,
            bg=self.ACCENT,
            fg='#052e16',
            active_bg='#16a34a',
        ).pack(side='right')

        def toggle_frame(*_):
            message.config(text='')
            if mode.get() == 'duration':
                dl_frame.pack_forget()
                dur_frame.pack(fill='x', pady=(8, 0))
            else:
                dur_frame.pack_forget()
                dl_frame.pack(fill='x', pady=(8, 0))

        mode.trace_add('write', toggle_frame)
        toggle_frame()
        win.transient(self.root)
        win.grab_set()
        win.focus_force()

    def add_field_row(self, parent, fields):
        for column, (label, var, width) in enumerate(fields):
            field = tk.Frame(parent, bg=self.BG)
            field.grid(row=0, column=column, padx=(0, 8), sticky='w')

            tk.Label(
                field,
                text=label,
                bg=self.BG,
                fg=self.MUTED,
                font=('Segoe UI', 8),
            ).pack(anchor='w')

            tk.Entry(
                field,
                textvariable=var,
                width=width,
                justify='center',
                relief='flat',
                bg=self.PANEL,
                fg=self.TEXT,
                insertbackground=self.TEXT,
                font=('Consolas', 10),
            ).pack()

    def read_int(self, var, label, minimum=None, maximum=None):
        try:
            value = int(var.get())
        except ValueError as exc:
            raise ValueError(f'{label} must be a number.') from exc

        if minimum is not None and value < minimum:
            raise ValueError(f'{label} must be at least {minimum}.')

        if maximum is not None and value > maximum:
            raise ValueError(f'{label} must be at most {maximum}.')

        return value

    def drag_start(self, event):
        self._x = event.x
        self._y = event.y

    def drag_move(self, event):
        x = self.root.winfo_x() + event.x - self._x
        y = self.root.winfo_y() + event.y - self._y
        self.root.geometry(f'+{x}+{y}')


if __name__ == '__main__':
    Countdown()
