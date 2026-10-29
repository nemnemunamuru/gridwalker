import time
import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import tkinter.scrolledtext as scrolledtext

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from .utils import resource_path
from .logger import SolveLogger
from .grid import build_grid, check_constraints
from .spiral import spiral_seed_square, choose_best_spiral_seed
from .hamiltonian import hamiltonian_with_seed
from .plotting import plot_path_with_arrows


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Grid Path — Spiral then Search (refactored)")
        self.geometry("1000x760")

        try:
            self.iconbitmap(resource_path("gridwalker.ico"))
        except Exception:
            pass

        frm = ttk.Frame(self)
        frm.pack(side=tk.TOP, fill=tk.X, padx=10, pady=8)

        values = [str(v) for v in range(20, 201, 20)]

        ttk.Label(frm, text="Width (X)").grid(row=0, column=0, sticky="w")
        self.var_x = tk.StringVar(value="100")
        ttk.Combobox(frm, textvariable=self.var_x, values=values,
                     width=8, state="readonly").grid(row=0, column=1, padx=6)

        ttk.Label(frm, text="Height (Y)").grid(row=0, column=2, sticky="w")
        self.var_y = tk.StringVar(value="100")
        ttk.Combobox(frm, textvariable=self.var_y, values=values,
                     width=8, state="readonly").grid(row=0, column=3, padx=6)

        ttk.Label(frm, text="Timeout (sec)").grid(row=0, column=4, sticky="w")
        self.var_timeout = tk.StringVar(value="3.0")
        ttk.Entry(frm, textvariable=self.var_timeout, width=8).grid(row=0, column=5, padx=6)

        btn_frm = ttk.Frame(self)
        btn_frm.pack(side=tk.TOP, fill=tk.X, padx=10, pady=6)
        ttk.Button(btn_frm, text="Generate & Plot", command=self.run).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frm, text="Save CSV", command=self.save_csv).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frm, text="Log", command=self.show_log_popup).pack(side=tk.LEFT, padx=4)

        self.fig, self.ax = plt.subplots(figsize=(7.6, 7.2))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=8)

        self.current_path = []
        self.current_grid = None
        self.current_limits = None
        self.logger = SolveLogger()

    def show_log_popup(self):
        top = tk.Toplevel(self)
        top.title("Solving Log")
        top.geometry("820x540")
        txt = scrolledtext.ScrolledText(top, wrap="word", font=("Consolas", 10))
        txt.pack(fill="both", expand=True, padx=8, pady=8)
        txt.insert("1.0", self.logger.dump_text() if self.logger else "(no log)")
        txt.configure(state="disabled")

        btns = ttk.Frame(top)
        btns.pack(fill="x", padx=8, pady=6)

        def copy_all():
            self.clipboard_clear()
            self.clipboard_append(self.logger.dump_text())
            messagebox.showinfo("Copied", "Log copied to clipboard.")

        def save_as():
            f = filedialog.asksaveasfilename(
                title="Save Log As", defaultextension=".log",
                filetypes=[("Log", "*.log"), ("Text", "*.txt"), ("All", "*")]
            )
            if not f:
                return
            try:
                with open(f, "w", encoding="utf-8") as fp:
                    fp.write(self.logger.dump_text())
                messagebox.showinfo("Saved", f"Log saved:\n" + f)
            except Exception as e:
                messagebox.showerror("Save error", str(e))

        ttk.Button(btns, text="Copy", command=copy_all).pack(side="left", padx=4)
        ttk.Button(btns, text="Save…", command=save_as).pack(side="left", padx=4)
        ttk.Button(btns, text="Close", command=top.destroy).pack(side="right", padx=4)

    def run(self):
        self.logger = SolveLogger()
        self.logger.section("Inputs")

        try:
            width = int(self.var_x.get())
            height = int(self.var_y.get())
            if width < 20 or width > 200 or height < 20 or height > 200:
                raise ValueError
            self.logger.info(f"Width={width}, Height={height}")
        except Exception:
            self.logger.info("Input error: out of allowed range 20..200 (step 20).")
            messagebox.showerror("Input error", "Width/Height must be in 20..200 (step 20).")
            return

        if abs(width - height) >= 80:
            self.logger.info(f"Rejected: |X - Y| = {abs(width - height)} >= 80")
            messagebox.showerror(
                "Input error",
                "The difference |X - Y| must be less than 80.\nPlease choose widths/heights with smaller difference."
            )
            return

        try:
            timeout = float(self.var_timeout.get())
            if timeout <= 0:
                raise ValueError
            self.logger.info(f"Timeout={timeout:.2f}s")
        except Exception:
            self.logger.info("Input error: invalid timeout")
            messagebox.showerror("Input error", "Timeout (sec) must be a positive number.")
            return

        x_limit = width // 2
        y_limit = height // 2
        xs, ys, points, S = build_grid(x_limit, y_limit)
        self.current_grid = (xs, ys, S)
        self.current_limits = (x_limit, y_limit)
        self.logger.info(f"x_limit=±{x_limit}, y_limit=±{y_limit}, points={len(points)}")

        t_solve0 = time.perf_counter()
        if width == height:
            self.logger.section("Mode: Square (Spiral Only, orthogonal)")
            ok = False
            for cw in (True, False):
                for sd in range(4):
                    sp = spiral_seed_square(x_limit, start_dir=sd, clockwise=cw)
                    seen = set(); tmp = []
                    for q in sp:
                        if q in S and q not in seen:
                            tmp.append(q); seen.add(q)
                    self.logger.info(f"spiral cw={cw}, start_dir={sd}, len={len(tmp)}")
                    if len(tmp) == len(S):
                        full_path = tmp
                        ok = True; break
                if ok: break
            if not ok:
                self.logger.info("Square spiral could not cover all points — abort.")
                messagebox.showwarning(
                    "Spiral failed",
                    "Square spiral did not cover all points unexpectedly.\nTry a different orientation."
                )
                return

            violations = check_constraints(full_path)
            if violations:
                self.logger.section("Constraint check")
                self.logger.info(f"violations={len(violations)} (must be 0)")
                messagebox.showerror(
                    "Constraint violation",
                    f"Found {len(violations)} moves not equal to 10 or 10√2."
                )
                return

            title = (f"SQUARE (spiral only): Grid = ±{x_limit} × ±{y_limit} | "
                     f"Points = {len(points)} | Steps = {len(full_path)}")

        else:
            self.logger.section("Mode: Non-square (Spiral seed + Hamiltonian)")
            spiral_side = max(0, min(width, height) - 20); spiral_side -= (spiral_side % 10)
            spiral_half = spiral_side // 2
            self.logger.info(f"spiral_side={spiral_side}, spiral_half=±{spiral_half}")

            seed_path = choose_best_spiral_seed(spiral_half, x_limit, y_limit, logger=self.logger)
            for (sx, sy) in seed_path:
                if not (-x_limit <= sx <= x_limit and -y_limit <= sy <= y_limit):
                    self.logger.info(f"Seed out of bounds at ({sx},{sy}) — abort.")
                    messagebox.showwarning(
                        "Out of bounds",
                        f"Spiral (±{spiral_half}) exceeds grid (±{x_limit}, ±{y_limit}). Adjust X/Y."
                    )
                    return

            start = seed_path[-1] if seed_path else (0, 0)
            full_path = hamiltonian_with_seed(
                x_limit, y_limit, timeout_sec=timeout, start=start, seed_path=seed_path, logger=self.logger
            )
            if full_path is None:
                self.logger.info("Hamiltonian search failed (timeout or dead-end).")
                messagebox.showwarning(
                    "Search failed",
                    "Hamiltonian search timed out or failed.\nTry increasing the timeout or reducing X/Y."
                )
                return

            violations = check_constraints(full_path)
            if violations:
                self.logger.section("Constraint check")
                self.logger.info(f"violations={len(violations)} (must be 0)")
                for i, ((x1,y1),(x2,y2),d2) in enumerate(violations[:5]):
                    self.logger.info(f"  v{i}: ({x1},{y1})->({x2},{y2}) d2={d2}")
                messagebox.showerror(
                    "Constraint violation",
                    f"Found {len(violations)} moves not equal to 10 or 10√2."
                )
                return

            title = (f"Spiral (seed) → Search | Grid = ±{x_limit} × ±{y_limit} | "
                     f"Points = {len(points)} | Steps = {len(full_path)}")

        t_solve1 = time.perf_counter()
        self.logger.section("Summary")
        self.logger.info(f"elapsed={t_solve1 - t_solve0:.3f}s, path_len={len(full_path)} / points={len(S)}")

        self.current_path = full_path
        self.ax.clear()
        plot_path_with_arrows(self.fig, self.ax, S, full_path, x_limit, y_limit, title)
        self.canvas.draw()

    def save_csv(self):
        if not self.current_path:
            messagebox.showinfo("Info", "Please run 'Generate & Plot' first.")
            return
        fpath = filedialog.asksaveasfilename(
            title="Save as CSV",
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")]
        )
        if not fpath:
            return
        try:
            with open(fpath, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["MeasurePosX", "MeasurePosY", "CorrPosX", "CorrPosY"])
                for x, y in self.current_path:
                    w.writerow([x, y, 0, 0])
            messagebox.showinfo("Saved", f"CSV saved:\n" + fpath)
        except Exception as e:
            messagebox.showerror("Save error", str(e))
