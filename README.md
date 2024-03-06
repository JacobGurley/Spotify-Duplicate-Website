# Spotify Duplicate Song Remover

## Overview
Spotify Duplicate Song Remover is a web application designed to find and remove duplicate songs from your playlists. This project utilizes the Spotify API, Flask, Python, HTML, JavaScript, and CSS, and is hosted on Heroku. It allows users to log in to their Spotify account, choose a playlist from their library, and then analyzes it to list duplicate songs, potential duplicate songs based on duration, and songs with missing information.

## Demo
Watch the program in action [here](https://youtu.be/KaYC0QnaxY8).

## Features
- **User Authentication:** Secure login through Spotify accounts.
- **Playlist Selection:** Users can select any of their playlists for analysis.
- **Duplicate Detection:** Identifies exact duplicate songs within a playlist.
- **Potential Duplicate Detection:** Flags songs that might be duplicates based on their duration.
- **Missing Information Identification:** Points out songs with missing metadata.
- **Deletion:** Deletes duplicate songs from the chosen playlist.
- **User Check:** If the user tries to delete a song from another user's playlist, they will recieve an error message.

## Technologies Used
- **Spotipy:** A lightweight Python library for the Spotify Web API.
- **Flask:** A micro web framework written in Python for building web applications.
- **HTML/CSS:** For structuring and styling the web interface.
- **JavaScript:** To enhance the interactivity of the web application.
- **Heroku:** A cloud platform for hosting the web application.
