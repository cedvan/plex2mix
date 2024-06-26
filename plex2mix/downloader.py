from concurrent.futures import ThreadPoolExecutor
import os
from plexapi.server import PlexServer
from plexapi.playlist import Playlist
from plexapi.audio import Track


class Downloader:
    def __init__(self, server: PlexServer, path: str, playlists_path: str, threads=4) -> None:

        self.server = server
        self.playlists = self.server.playlists(playlistType='audio')
        self.path = os.path.expanduser(os.path.join(path))
        self.playlists_path = os.path.expanduser(os.path.join(playlists_path))
        self.pool = ThreadPoolExecutor(max_workers=threads)
        self.downloadedTracks = []

    def get_playlists(self) -> list:
        if self.playlists is None:
            return []
        return self.playlists

    def get_playlist_titles(self) -> list:
        if self.playlists is None:
            return []
        return [p.title for p in self.playlists]

    def __download_track(self, track: Track,  overwrite=False) -> str:
        album_path, filepath = self.get_path(track)
        size_on_server = track.media[0].parts[0].size
        if not os.path.exists(filepath) or overwrite:
            track.download(album_path, keep_original_name=True)

        self.downloadedTracks.append(filepath)

        return filepath

    def get_path(self, track: Track) -> tuple:
        librairy = self.server.library.sectionByID(track.librarySectionID)
        directory, file = os.path.split(track.media[0].parts[0].file)

        # Remove library path in directory path
        for location in librairy.locations:
            if directory.startswith(location):
                directory = directory.lstrip(location)
                break

        # Fix OS separators
        album_path = ''
        for part in directory.split('/'):
            album_path = os.path.join(album_path, part)

        album_path = os.path.join(self.path, album_path)
        filepath = os.path.join(album_path, file)
        return album_path, filepath

    def dump_m3u8(self, playlist: Playlist) -> None:
        title = playlist.title.strip()
        path = os.path.join(self.playlists_path,
                            f"{title}.m3u8")
        f = open(path, "w", encoding="utf-8")
        f.write("#EXTM3u\n")
        for track in playlist.items():
            if track.duration and track.grandparentTitle and track.parentTitle is not None:
                _, filepath = self.get_path(track)
                m3u8 = f"#EXTINF:{track.duration // 1000},{track.grandparentTitle} - {track.title}\n#EXT-X-RATING:{track.userRating if track.userRating is not None else 0}\n{filepath}\n"
                f.write(m3u8)

    def futures(self):
        return self.futures

    def download(self, playlist: Playlist, overwrite=False) -> list:

        tasks = []
        for track in playlist.items():
            future = self.pool.submit(self.__download_track, track, overwrite)
            tasks.append(future)
        self.pool.submit(self.dump_m3u8, playlist)
        return tasks
