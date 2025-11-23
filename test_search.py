from youtubesearchpython import VideosSearch

try:
    print("Attempting search...")
    videosSearch = VideosSearch('NoCopyrightSounds', limit = 2)
    print("Search object created.")
    result = videosSearch.result()
    print("Search successful!")
    print(result)
except Exception as e:
    print(f"Search failed: {e}")
