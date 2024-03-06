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

## Setup and Local Running
To run this project locally, follow these steps:

1. **Clone the Repository**
- git clone: https://github.com/JacobGurley/Spotify-Duplicate-Website
2. **Install Dependencies**
- pip install -r requirements.txt
3. **Spotify Developer Account**
- Set up a Spotify Developer account and create an app to obtain the `Client ID` and `Client Secret`.
- Add `http://127.0.0.1:5000/callback` to the list of Redirect URIs in your Spotify app settings.
4. **Environment Variables**
Set up the following environment variables:
- SPOTIPY_CLIENT_ID='your_spotify_client_id'
- SPOTIPY_CLIENT_SECRET='your_spotify_client_secret'
- SPOTIPY_REDIRECT_URI='http://127.0.0.1:5000/callback'
5. **Run the Application**
- run command: python app.py
- Your app should now be running on [http://127.0.0.1:5000/](http://127.0.0.1:5000/).

## Limitations
Currently, the application is in development mode on Spotify, which means it's not publicly available for all users without developer credentials.

## Contributions
Contributions are welcome! If you have suggestions or want to improve the application, please feel free to fork the repository, make changes, and submit a pull request.

## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE) file for details.
