from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image, ImageTk  # To change img sizes
from mutagen.mp3 import MP3  # Scanning mp3 files

import tkinter.ttk as ttk  # Add slider
import pygame  # To manipulate with audio
import time  # Work with time formats
import ctypes  # For increase dpi


def set_normal_dpi(root):
	ctypes.windll.shcore.SetProcessDpiAwareness(1)
	root.tk.call('tk', 'scaling', 5/4)

root = Tk()
root.title('PyMP#')
root.geometry('575x400')
set_normal_dpi(root)
Current_folder = ""

# Initialize Pygame Mixer
pygame.mixer.init()

# Get song time length info
def play_time(song_path):
	# My solution to make time in needed format
		# current_second = pygame.mixer.music.get_pos() // 1000
		# current_minute = current_second // 60
		# current_hour = current_minute // 60
		# current_time = f'Time: {current_hour:02}:{current_minute%60:02}:{current_second%60:02}'

	# Check for double timing
	if stopped:
		return None

	global song_length
	# Solution with time module
	current_time = pygame.mixer.music.get_pos() // 1000
	converted_current_time = time.strftime('%M:%S', time.gmtime(current_time))

	# Get song length with mutagen.mp3
	# Load Song with Mutagen
	song_mutagen = MP3(song_path)
	# Get song Length (in seconds)
	song_length = song_mutagen.info.length
	# Convert to time format
	converted_song_length = time.strftime('%M:%S', time.gmtime(song_length))

	if int(player_slider.get()) == int(song_length)+1:
		status_bar.config(text=f'Time Elapsed: {converted_song_length}  of  {converted_song_length}    ')
	elif paused:
		pass
	elif int(player_slider.get()) == current_time-1:
		# Slider hasn't been moved

		# Update slider To position
		song_length_int = int(song_length)
		player_slider.config(to=song_length_int, value=current_time)
	else:
		# Slider has been moved
		
		# Update slider To position
		song_length_int = int(song_length)
		player_slider.config(to=song_length_int, value=int(player_slider.get()))

		# Reconvert time
		converted_current_time = time.strftime('%M:%S', time.gmtime(int(player_slider.get())))

		# Move slider along by one second
		next_time = int(player_slider.get()) + 1
		player_slider.config(value=next_time)

		status_bar.config(text=f'Time Elapsed: {converted_current_time}  of  {converted_song_length}    ')



	status_bar.config(text=f'Time Elapsed: {converted_current_time}  of  {converted_song_length}    ')

	# player_slider.config(value=current_time)
	

	slider_label.config(text=f'Slider: {int(player_slider.get())} and Song pos: {current_time}')
	

	status_bar.after(1000, lambda: play_time(song_path))


# Play selected song
def play():
	# Reset slider and status bar
	status_bar.config(text='')
	player_slider.config(value=0)

	song = song_box.get(ACTIVE)
	song = f'{Current_folder}/{song}'
	
	pygame.mixer.music.load(song)
	pygame.mixer.music.play(loops=0)

	# Call the play_time function to get time elapsed and song length
	song_path = f'{Current_folder}/{song_box.get(ACTIVE)}'
	stopped = False
	play_time(song_path)


# Stop playing current song
global stopped
stopped = False

def stop():
	# Reset slider and status bar
	status_bar.config(text='')
	player_slider.config(value=0)

	# Stop song from playing
	pygame.mixer.music.stop()
	song_box.selection_clear(ACTIVE)

	# Set Stop var to True
	global stopped
	stopped = True


# Creatre Global pause var
global paused
paused = False
# Pause and unpause the current song
def pause(is_paused):
	global paused
	paused = is_paused

	if not paused:
		pygame.mixer.music.pause()
		paused = True
	else:
		pygame.mixer.music.unpause()
		paused = False


# Constant to choose direction in playlist
FORWARD = 1
BACK = -1
def move(direction):
	# Reset slider and status bar
	status_bar.config(text='')
	player_slider.config(value=0)
	# .curselection() returns tuple of form (%song_index%, )
	# Get the next one song
	playslit_len = song_box.size()
	forward_song = (song_box.curselection()[0] + direction) % playslit_len

	# Select next song and play it
	song_box.selection_clear(ACTIVE)
	song_box.select_set(forward_song)
	song_box.activate(forward_song)
	play()


# Constatns to choose working mode of remove function
CURRENT = (ANCHOR, )
ALL = (0, END)
def remove(count):
	stop()
	song_box.delete(*count)
	pygame.mixer.music.stop()


def slide(x):
	# slider_pos = int(player_slider.get())
	# total_pos = int(song_length)
	# slider_label.config(text=f'{slider_pos} of {total_pos}')
	song = song_box.get(ACTIVE)
	song = f'{Current_folder}/{song}'

	pygame.mixer.music.load(song)
	pygame.mixer.music.play(loops=0, start=int(player_slider.get()))


def volume(x):
	pygame.mixer.music.set_volume(1 - volume_slider.get())

	curret_volume = pygame.mixer.music.get_volume() * 100  # from 0 to 100


# Add song function
def add_song():
	global Current_folder

	sound_file_types = (("mp3 files", "*.mp3"), ("wav files", "*.wav"))
	song = filedialog.askopenfilename(initialdir='audio/', title="Choose a song", filetypes=(sound_file_types))
	
	# Strip out the directory info
	Current_folder = '/'.join(song.split('/')[:-1])
	song = song.split('/')[-1]

	# Add only new uniuqe songs
	if song not in song_box.get(0, END):
		song_box.insert(END, song)
	else:
		messagebox.showerror(title='Error', message=f'Song "{song}" already in playlist.')


def add_many_songs():
	global Current_folder

	sound_file_types = (("mp3 files", "*.mp3"), ("wav files", "*.wav"))
	songs = filedialog.askopenfilenames(initialdir='audio/', title="Choose a song", filetypes=(sound_file_types))
	
	# Strip out the directory info and rememer current folder
	Current_folder = '/'.join(songs[0].split('/')[:-1])
	songs = [song.split('/')[-1] for song in songs]

	# Add only new uniuqe songs
	already_in_playlist = set()
	is_repeats = False
	for song in songs:
		if song not in song_box.get(0, END):
			song_box.insert(END, song)
		else:
			is_repeats = True
			already_in_playlist.add(song)

	# Message error about repeated songs
	if is_repeats:
		repeated_songs = '\n'.join(already_in_playlist)
		messagebox.showerror(title='Error', message=f'The next songs are already in playlist: \n\n{repeated_songs}')


# -------------------------------------------------------
# Create Master frame
master_frame = Frame(root)
master_frame.pack(pady=20)

# Create Playlist Box
song_box = Listbox(master_frame, bg='black', fg='green', width=80, selectbackground='grey', selectforeground='black')
song_box.grid(row=0, column=0)

volume_frame = LabelFrame(master_frame, text='Volume')
volume_frame.grid(row=0, column=1, padx=10)

# Create player control buttons
resizing = (75, 75)

back_btn_img = ImageTk.PhotoImage(Image.open('GUI/previous.png').resize(resizing))
forward_btn_img = ImageTk.PhotoImage(Image.open('GUI/next.png').resize(resizing))
play_btn_img = ImageTk.PhotoImage(Image.open('GUI/play.png').resize(resizing))
pause_btn_img = ImageTk.PhotoImage(Image.open('GUI/pause.png').resize(resizing))
stop_btn_img = ImageTk.PhotoImage(Image.open('GUI/stop.png').resize(resizing))

# Create player control frames
controls_frame = Frame(master_frame)
controls_frame.grid(row=1, column=0, pady=20)

# Create Buttons
back_btn = Button(controls_frame, image=back_btn_img, borderwidth=0, command=lambda: move(BACK))
forward_btn = Button(controls_frame, image=forward_btn_img, borderwidth=0, command=lambda: move(FORWARD))
play_btn = Button(controls_frame, image=play_btn_img, borderwidth=0, command=play)
pause_btn = Button(controls_frame, image=pause_btn_img, borderwidth=0, command=lambda: pause(paused))
stop_btn = Button(controls_frame, image=stop_btn_img, borderwidth=0, command=stop)

back_btn.grid(row=0, column=0, padx=10)
forward_btn.grid(row=0, column=1, padx=10)
play_btn.grid(row=0, column=2, padx=10)
pause_btn.grid(row=0, column=3, padx=10)
stop_btn.grid(row=0, column=4, padx=10)

# Create Menu
my_menu = Menu(root)
root.config(menu=my_menu)

# Create add song menu
add_song_menu = Menu(my_menu, tearoff=0)
my_menu.add_cascade(label="Add songs", menu=add_song_menu)
add_song_menu.add_command(label="Add one song to playlist", command=add_song)
add_song_menu.add_command(label="Add many songs to playlist", command=add_many_songs)

# Create delete song menu
remove_song_menu = Menu(my_menu, tearoff=0)
my_menu.add_cascade(label="Remove songs", menu=remove_song_menu)
remove_song_menu.add_command(label="Delete a song", command=lambda: remove(CURRENT))
remove_song_menu.add_command(label="Delete all songs", command=lambda: remove(ALL))

# Create status bar
status_bar = Label(root, text='', bd=1, relief=GROOVE, anchor=E)
status_bar.pack(fill=X, side=BOTTOM, ipady=2)


# Create music position slider
player_slider = ttk.Scale(master_frame, from_=0, to=100, orient=HORIZONTAL, value=0, command=slide, length=400)
player_slider.grid(row=2, column=0, pady=30)

# Create temporary slider label
slider_label = Label(root, text='No song')
slider_label.pack(pady=10)

# Create volume slider
volume_slider = ttk.Scale(volume_frame, from_=0, to=1, orient=VERTICAL, value=0, command=volume, length=125)
volume_slider.pack()

# Load images for volume power graph
resizing_vol = (75, 75)


# Create volume meter
volume_meter = Label(master_frame)
volume_meter.grid(row=1, column=1, padx=10)

root.mainloop()