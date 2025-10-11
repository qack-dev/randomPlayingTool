
import os
import random
import tkinter as tk
from tkinter import filedialog, messagebox
import pygame

class MusicPlayer:
    """
    作業用BGMランダム再生ツールを管理するクラス。
    UIの作成、ファイル検索、音楽再生のロジックを担当します。
    """
    def __init__(self, root):
        """アプリケーションを初期化します。"""
        self.root = root
        self.root.title("作業用BGMランダム再生ツール")
        self.root.geometry("500x200")

        # --- 音楽再生ライブラリの初期化 ---
        pygame.mixer.init()

        # --- 状態管理用の変数 ---
        self.music_files = []
        self.current_track_index = -1
        self.playing = False
        self.paused = False

        # --- UIコンポーネントの作成と配置 ---
        self.setup_ui()

        # --- 定期的に再生終了をチェック ---
        self.check_music_end()

    def setup_ui(self):
        """UIウィジェットの作成と配置を行います。"""
        # --- フレームの作成 ---
        top_frame = tk.Frame(self.root, pady=10)
        top_frame.pack(fill=tk.X, padx=10)

        control_frame = tk.Frame(self.root, pady=10)
        control_frame.pack(padx=10)

        info_frame = tk.Frame(self.root, pady=10)
        info_frame.pack(fill=tk.X, padx=10)

        # --- ウィジェットの作成 ---
        # フォルダ選択
        self.folder_button = tk.Button(top_frame, text="音楽フォルダを選択", command=self.select_folder)
        self.folder_button.pack(pady=5)

        # 再生/停止ボタン
        self.play_stop_button = tk.Button(control_frame, text="再生", command=self.toggle_play_stop, width=10, state=tk.DISABLED)
        self.play_stop_button.pack(side=tk.LEFT, padx=5)

        # 次の曲へボタン
        self.next_button = tk.Button(control_frame, text="次の曲へ", command=self.play_next, width=10, state=tk.DISABLED)
        self.next_button.pack(side=tk.LEFT, padx=5)

        # 再生中ファイル名ラベル
        self.status_label = tk.Label(info_frame, text="再生待機中...", anchor="w", justify="left")
        self.status_label.pack(fill=tk.X)

    def select_folder(self):
        """フォルダ選択ダイアログを開き、音楽ファイルを検索します。"""
        folder_path = filedialog.askdirectory()
        if not folder_path:
            return

        self.find_music_files(folder_path)

        if self.music_files:
            self.current_track_index = -1
            self.play_stop_button.config(state=tk.NORMAL)
            self.next_button.config(state=tk.NORMAL)
            messagebox.showinfo("準備完了", f"{len(self.music_files)} 曲の音楽ファイルが見つかりました。")
            self.status_label.config(text="再生ボタンを押してください。")
        else:
            self.play_stop_button.config(state=tk.DISABLED)
            self.next_button.config(state=tk.DISABLED)
            messagebox.showwarning("ファイルなし", "指定されたフォルダに音楽ファイル (.mp3, .wav, .flac) が見つかりませんでした。")
            self.status_label.config(text="フォルダを選択してください。")

    def find_music_files(self, folder_path):
        """指定されたフォルダ内を再帰的に検索し、音楽ファイルリストを作成します。"""
        self.music_files = []
        supported_formats = ('.mp3', '.wav', '.flac')
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(supported_formats):
                    self.music_files.append(os.path.join(root, file))
        
        # 音楽リストをシャッフル
        if self.music_files:
            random.shuffle(self.music_files)

    def toggle_play_stop(self):
        """再生/停止ボタンの状態を切り替えます。"""
        if not self.playing:
            self.play_music()
        else:
            self.stop_music()

    def play_music(self):
        """音楽を再生します。"""
        if not self.music_files:
            return

        if self.paused:
            # 一時停止からの再開
            pygame.mixer.music.unpause()
            self.paused = False
        else:
            # 新しい曲または次の曲を再生
            self.current_track_index += 1
            if self.current_track_index >= len(self.music_files):
                self.current_track_index = 0 # リストの最初に戻る
            
            track_path = self.music_files[self.current_track_index]
            try:
                pygame.mixer.music.load(track_path)
                pygame.mixer.music.play()
                # 表示を「フォルダの絶対パス / ファイル名」の形式に変更
                folder_path = os.path.dirname(track_path)
                file_name = os.path.basename(track_path)
                self.status_label.config(text=f"再生中: {folder_path} / {file_name}")
            except pygame.error as e:
                messagebox.showerror("再生エラー", f"ファイルを再生できませんでした。\n{e}")
                self.playing = False
                return

        self.playing = True
        self.play_stop_button.config(text="停止")

    def stop_music(self):
        """音楽を停止します。"""
        pygame.mixer.music.stop()
        self.playing = False
        self.paused = False # 停止したら一時停止状態もリセット
        self.play_stop_button.config(text="再生")
        self.status_label.config(text="停止中")

    def play_next(self):
        """次の曲を再生します。"""
        self.stop_music()
        self.play_music()

    def check_music_end(self):
        """再生が終了したかを確認し、終了していれば次の曲を再生します。"""
        if self.playing and not pygame.mixer.music.get_busy():
            # 再生中で、かつ再生が終わった場合
            self.play_next()
        
        # 100ミリ秒後にもう一度この関数を呼び出す
        self.root.after(100, self.check_music_end)

if __name__ == "__main__":
    root = tk.Tk()
    app = MusicPlayer(root)
    root.mainloop()
