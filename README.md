# YouTube Playlist Duration Calculator

This is a web application that allows you to calculate the total duration of a YouTube playlist. You can also specify a custom playback speed and a range of videos within the playlist to calculate the duration for.

## Features

- **Playlist Duration Calculation:** Quickly calculates the total duration of a YouTube playlist.
- **Custom Playback Speed:**  Allows you to calculate the duration at a custom playback speed (e.g., 1.5x, 2x).
- **Range Selection:**  Enables you to specify a start and end video within the playlist to calculate the duration of a specific section.
- **Flexible Input:** Accepts a YouTube playlist link, playlist ID or a video link from the playlist.
- **Detailed Output:** Displays the playlist title and total duration in hours, minutes, and seconds.
- **Batch Processing:** Calculate durations for multiple playlists simultaneously.
- **User-Friendly Interface:** Simple and intuitive design for easy navigation.
- **Dark Mode:** Includes a dark mode option for a comfortable user experience.
- **No Sign-Up Required:** Start calculating instantly without the need for an account.
- **Multi-Platform Compatibility:** Optimized for desktop and mobile devices.
- **Accurate:** Uses the YouTube API to fetch accurate video durations.

## How to Use

1. **Enter Playlist Link/ID/Video Link:** In the provided text area, paste a YouTube playlist link, the playlist ID, or a link to a video within the playlist.
2. **Specify Range (Optional):** If you want to calculate the duration for a specific range of videos, enter the starting and ending video numbers in the "Start Range" and "End Range" fields. If you don't, the whole playlist will be calculated.
3. **Enter Custom Speed (Optional):** If you want to calculate the duration at a specific speed, enter the desired playback speed (e.g., 1.5, 2.25) in the "playback speed" field.
4. **Enter Your API Key (Optional):** You may provide your own YouTube API key if you wish to increase rate limit or to support the developer.
5. **Click Calculate:**  Press the "Calculate" button to get the total duration.
6. **View Results:** The calculated duration will be displayed below the input form, along with other informations.

## Technologies Used

- **Frontend:** HTML, CSS (Halfmoon framework), JavaScript
- **Backend:** Python (FastApi)
- **YouTube API:** For fetching video durations

## Project Structure
   .
├── app.py           # Main Flask application
├── static/
│   ├── favicon.ico      # Favicon
│   ├── form_validation.js  # Form Validation script 
│   ├── logo.png       # Website logo image
├── templates/
│   └── index.html     # HTML template for the main page
├── README.md          # This file
└── manifest.json      # Manifest file for PWA



## Live Demo

You can access the live demo of the project at: [https://yt-playlist-len-calc.onrender.com/](https://yt-playlist-len-calc.onrender.com/)

## Contributing

Feel free to contribute to the project by opening issues or submitting pull requests.

## License

This project is open source and available under the MIT License.

## Support

Consider giving feedback at [Ko-fi](https://ko-fi.com/anuragyadav)
