"""
music_player.py

A module that provides functionality for playing music tracks and sound effects using 
the Pygame library. The MusicPlayer class allows for managing music playback with features 
such as shuffle, loop, pause, and track navigation. Additionally, it handles playing sound 
effects with simple controls.

Classes:
    MusicPlayer: A class that manages music and sound effect playback, offering 
                 functionalities like play, pause, stop, shuffle, loop, and sound effect playback.

Functions:
    load_files(directory): Loads music or sound effect files from a given directory.
    play_music(index=None): Plays a specific or currently selected music track.
    pause_music(): Pauses the currently playing music track.
    unpause_music(): Unpauses the paused music track.
    stop_music(): Stops the currently playing music track.
    next_track(): Plays the next music track in the playlist.
    previous_track(): Plays the previous music track in the playlist.
    shuffle_tracks(): Shuffles the music playlist and starts playback from the first track.
    toggle_loop(): Toggles loop mode for continuous playback of the current track.
    play_sound_effect(effect_index): Plays a sound effect from the available list.
    list_music(): Returns the list of available music file names.
    list_sound_effects(): Returns the list of available sound effect file names.

Dependencies:
    - Pygame: Used to handle audio playback functionalities.
    - OS: Provides directory and file management to load audio files.

Usage:
    Initialize a MusicPlayer object with paths to the directories containing music and 
    sound effect files. Use the various playback control methods to interact with the 
    audio files in a flexible manner.
"""

import os
import random
import logging
import time
import pygame


logging.basicConfig(level=logging.INFO)


class MusicPlayer:
    """
    A music and sound effects player that manages the playback of audio tracks
    and sound effects using Pygame. It supports features like shuffling, looping,
    and control over track navigation.

    Attributes:
        music_files (list): A list of paths to music files.
        sound_effects_files (list): A list of paths to sound effect files.
        current_track_index (int): The index of the currently playing track.
        loop (bool): Flag to indicate whether looping is enabled.
        shuffle (bool): Flag to indicate whether shuffle mode is enabled.
    """

    def __init__(self, music_dir, sound_effects_dir):
        """
        Initializes the MusicPlayer with directories containing music and sound
        effects files, and initializes the Pygame mixer.

        Args:
            music_dir (str): The directory path where music files are stored.
            sound_effects_dir (str): The directory path where sound effects files are stored.
        """
        try:
            pygame.mixer.init()
            pygame.display.set_mode((1, 1))  # Initializes a small display window
            self.music_files = self.load_files(music_dir)
            self.sound_effects_files = self.load_files(sound_effects_dir)
            self.current_track_index = 0
            self.loop = False
            self.shuffle = False
            logging.info("MusicPlayer initialized successfully.")
        except Exception as e:
            logging.error(f"Error initializing MusicPlayer: {e}")

    def load_files(self, directory):
        """
        Loads music or sound effect files from a directory and filters files
        with extensions `.mp3` and `.wav`.

        Args:
            directory (str): The directory path from which to load audio files.

        Returns:
            list: A list of file paths to the audio files found in the directory.
        """
        try:
            return [
                os.path.join(directory, file)
                for file in os.listdir(directory)
                if file.endswith((".mp3", ".wav"))
            ]
        except FileNotFoundError:
            logging.error(f"Directory not found: {directory}")
            return []
        except Exception as e:
            logging.error(f"Error loading files from {directory}: {e}")
            return []

    def play_music(self, index=None):
        """
        Plays a selected music track by index or continues playing the current track.

        Args:
            index (int, optional): The index of the track to play. If not provided,
                                   the current track is played.
        """
        try:
            if not self.music_files:
                logging.warning("No music files available to play.")
                return
            if index is not None:
                self.current_track_index = index
            track = self.music_files[self.current_track_index]
            pygame.mixer.music.load(track)
            pygame.mixer.music.play()
            logging.info(f"Playing music: {os.path.basename(track)}")
        except IndexError:
            logging.error("Track index out of range.")
        except pygame.error as e:
            logging.error(f"Error playing music: {e}")

    def pause_music(self):
        """
        Pauses the currently playing music track.
        """
        try:
            pygame.mixer.music.pause()
            logging.info("Music paused.")
        except pygame.error as e:
            logging.error(f"Error pausing music: {e}")

    def unpause_music(self):
        """
        Resumes playing the paused music track.
        """
        try:
            pygame.mixer.music.unpause()
            logging.info("Music unpaused.")
        except pygame.error as e:
            logging.error(f"Error unpausing music: {e}")

    def stop_music(self):
        """
        Stops the currently playing music track.
        """
        try:
            pygame.mixer.music.stop()
            logging.info("Music stopped.")
        except pygame.error as e:
            logging.error(f"Error stopping music: {e}")

    def next_track(self):
        """
        Skips to the next track in the playlist. If the current track is the last one,
        it loops back to the first track.
        """
        try:
            self.current_track_index = (self.current_track_index + 1) % len(
                self.music_files
            )
            self.play_music()
            logging.info(f"Playing next track.")
        except Exception as e:
            logging.error(f"Error playing next track: {e}")

    def previous_track(self):
        """
        Returns to the previous track in the playlist. If the current track is the
        first one, it loops back to the last track.
        """
        try:
            self.current_track_index = (self.current_track_index - 1) % len(
                self.music_files
            )
            self.play_music()
            logging.info("Playing previous track.")
        except Exception as e:
            logging.error(f"Error playing previous track: {e}")

    def shuffle_tracks(self):
        """
        Shuffles the order of the music playlist and starts playing from the first track
        in the shuffled list.
        """
        try:
            random.shuffle(self.music_files)
            self.play_music(0)
            logging.info("Tracks shuffled and playing first track.")
        except Exception as e:
            logging.error(f"Error shuffling tracks: {e}")

    def toggle_loop(self):
        """
        Toggles the loop mode for the currently playing music. When loop mode is enabled,
        the current track repeats indefinitely until stopped manually.
        """
        try:
            self.loop = not self.loop
            pygame.mixer.music.set_endevent(
                pygame.USEREVENT if self.loop else pygame.NOEVENT
            )
            logging.info(f"Looping {'enabled' if self.loop else 'disabled'}.")
        except pygame.error as e:
            logging.error(f"Error toggling loop mode: {e}")

    def play_sound_effect(self, effect_index):
        """
        Plays a sound effect from the list of loaded sound effects.

        Args:
            effect_index (int): The index of the sound effect to play.
        """
        try:
            sound = pygame.mixer.Sound(self.sound_effects_files[effect_index])
            sound.play()
            logging.info(
                f"Playing sound effect: {os.path.basename(self.sound_effects_files[effect_index])}"
            )
        except IndexError:
            logging.error("Sound effect index out of range.")
        except pygame.error as e:
            logging.error(f"Error playing sound effect: {e}")

    def list_music(self):
        """
        Returns the list of available music file names (without directory paths).

        Returns:
            list: A list of music file names.
        """
        try:
            return [os.path.basename(file) for file in self.music_files]
        except Exception as e:
            logging.error(f"Error listing music: {e}")
            return []

    def list_sound_effects(self):
        """
        Returns the list of available sound effect file names (without directory paths).

        Returns:
            list: A list of sound effect file names.
        """
        try:
            return [os.path.basename(file) for file in self.sound_effects_files]
        except Exception as e:
            logging.error(f"Error listing sound effects: {e}")
            return []


# Example usage:

if __name__ == "__main__":
    # Define directories containing music and sound effects
    music_dir = r"D:\Torrents\Music"
    sound_effects_dir = r"D:\Torrents\Sounds"

    # Initialize the MusicPlayer
    player = MusicPlayer(music_dir, sound_effects_dir)

    # List available music files
    print("Listing available music:")
    print(player.list_music())
    print("Toggling loop mode...")
    player.toggle_loop()

    # Play the first music track
    print("Playing the first music track...")
    player.play_music(0)

    # Main loop to keep script running
    running = True
    while running:
        for event in pygame.event.get():
            # Exit if the window is closed
            if event.type == pygame.QUIT:
                running = False

            # Handle the USEREVENT when the music finishes
            if event.type == pygame.USEREVENT:
                if player.loop:
                    # Restart the track in loop mode
                    print("Looping the track...")
                    player.play_music(player.current_track_index)

        time.sleep(1)  # Slow down the loop to avoid busy waiting

    # Quit pygame
    pygame.quit()


"""
Other example use cases:

if __name__ == "__main__":
    # Example usage of the MusicPlayer class
    print("Initializing MusicPlayer...")

    # Define directories containing music and sound effects
    music_dir = "D:\\Torrents\\Music"
    sound_effects_dir = "D:\\Torrents\\Sounds"

    # Initialize the MusicPlayer
    player = MusicPlayer(music_dir, sound_effects_dir)

    # List available music files
    print("Listing available music:")
    print(player.list_music())

    # List available sound effects
    print("Listing available sound effects:")
    print(player.list_sound_effects())

    print("Toggling loop mode...")
    player.toggle_loop()

    # Play the first music track
    print("Playing the first music track...")
    player.play_music(0)

    while pygame.mixer.music.get_busy():
        time.sleep(1)  # Wait to keep the script alive

    # Pause the music
    print("Pausing music...")
    player.pause_music()
    time.sleep(2)  # Wait 2 seconds before unpausing

    # Unpause the music
    print("Unpausing music...")
    player.unpause_music()
    time.sleep(3)  # Let the music play for 3 more seconds

    # Play the next track
    print("Playing the next track...")
    player.next_track()
    time.sleep(3)  # Let the new track play for 3 seconds

    # Stop the music
    print("Stopping music...")
    player.stop_music()

    # Play a sound effect
    print("Playing a sound effect...")
    if player.list_sound_effects():
        player.play_sound_effect(0)  # Play the first sound effect
        time.sleep(2)  # Let the sound effect play for 2 seconds
    else:
        print("No sound effects found.")

    # Shuffle the tracks and play the first shuffled track
    print("Shuffling tracks and playing the first one...")
    player.shuffle_tracks()
    time.sleep(3)  # Let the shuffled track play for 3 seconds

    # Toggle loop mode and play a track
    print("Toggling loop mode...")
    player.toggle_loop()
    player.play_music(1)  # Play another track with loop mode enabled
    time.sleep(5)  # Let it play for 5 seconds (loop mode is on, so it will repeat)
    print("Execution finished.")
"""

'''
music_dir = r"D:\Torrents\Music"
sound_effects_dir = r"D:\Torrents\Sounds"
player = MusicPlayer(music_dir, sound_effects_dir)

print(player.list_music())

player.play_music()
print("playing music")
time.sleep(7)
# Keep the script running while the music is playing
"""while pygame.mixer.music.get_busy():
    time.sleep(1)  # Wait to keep the script alive
"""
print("Going to next track")
player.next_track()
time.sleep(7)

print("pausing music")
player.pause_music()
time.sleep(3)

print("Unpausing")
player.unpause_music()
time.sleep(3)

print("Shuffling")
# player.shuffle_tracks()
# player.toggle_loop()
'''
