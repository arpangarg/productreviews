from Tkinter import *
import ttk


class DisplayResults(object):

	def __init__(self, results_dict):
		self.results = results_dict

		self.root = self.create_root()

		self.create_skeleton()
		self.root.mainloop()

	def create_root(self):
		root = Tk()

		root.geometry("1400x600+300+300")
		root.title('Product Reviews Summary')

		return root

	def display_menu(self):
		menubar = Menu(self.root)
		self.root.config(menu=menubar)

		file_menu = Menu(menubar)
		file_menu.add_command(label="Exit", command=self.root.quit)
		menubar.add_cascade(label="File", menu=file_menu)

	def create_skeleton(self):
		main_frame = ttk.Frame(self.root, padding="12 12 12 12")
		main_frame.pack(fill=BOTH, expand=True)

		main_frame.columnconfigure(5, weight=1)
		main_frame.columnconfigure(14, weight=1)
		main_frame.rowconfigure(5, weight=1)

		close_button = ttk.Button(
			main_frame,
			text='Close',
			command=self.root.quit
		)
		close_button.grid(row=8, column=17, pady=5)

		left_frame = ttk.Frame(main_frame, borderwidth=3, relief=RIDGE)
		left_frame.grid(
			row=0,
			column=0,
			rowspan=7,
			columnspan=4,
			sticky=(W, E, N, S)
		)

		label_left = ttk.Label(left_frame, text='Product Features')
		label_left.pack(padx=5, pady=5)

		right_frame = ttk.Frame(main_frame, borderwidth=3, relief=RIDGE)
		right_frame.grid(row=0,
			column=4,
			rowspan=7,
			columnspan=14,
			sticky=(W, E, N, S)
		)
		right_frame.columnconfigure(3, weight=1)
		right_frame.columnconfigure(10, weight=1)
		right_frame.rowconfigure(2, weight=1)

		label_pro = ttk.Label(right_frame, text='Pros')
		label_pro.grid(row=1, columnspan=7, padx=5, pady=5)

		label_con = ttk.Label(right_frame, text='Cons')
		label_con.grid(row=1, column=7, columnspan=7, padx=5, pady=5)

		self.pro_box = Text(right_frame)
		self.pro_box.configure(wrap='word')
		self.pro_box.grid(
			row=2,
			column=0,
			columnspan=7,
			padx=5,
			pady=5,
			sticky=(W, E, N, S)
		)

		self.con_box = Text(right_frame)
		self.con_box.configure(wrap='word')
		self.con_box.grid(
			row=2,
			column=7,
			columnspan=7,
			padx=5,
			pady=5,
			sticky=(W, E, N, S)
		)

		self.features = tuple(self.results.keys())
		feature_names = StringVar(value=self.features)

		self.feature_box = Listbox(left_frame, listvariable=feature_names)

		for i in range(0, len(self.features), 2):
			self.feature_box.itemconfigure(i, background='#f0f0ff')

		self.feature_box.bind('<<ListboxSelect>>', self.show_pros_cons)
		self.feature_box.pack(fill=BOTH, expand=True, padx=5, pady=5)

	def show_pros_cons(self, *args):
		idxs = self.feature_box.curselection()
		feature_key = self.features[int(idxs[0])]
		
		self.pro_box.delete('1.0', 'end')
		self.con_box.delete('1.0', 'end')

		for pro in self.results[feature_key][0]:
			self.pro_box.insert('end', pro + '\n\n')

		for con in self.results[feature_key][1]:
			self.con_box.insert('end', con + '\n\n')
